from . import changelogger as cl
from . import commands as cmd
from . import messages as msg
from .resources import ac, sym


def run_preflight(config, TAG, skip_input: bool = False):
    # check branch
    check_release_branch(config['release_branch'])

    # check tag status
    check_tags(TAG, config['repo_root'])

    # check working tree status
    check_worktree(config['repo_root'], config['allow_dirty'], skip_input=skip_input)

    confirm = input(f'{sym.warning} update changelog? [y/N]: ').strip().lower()

    if confirm in ('y', 'yes'):
        res, _ = cmd.run_command(['git', 'describe', '--tags', '--abbrev=0'])
        prev_tag = res.stdout.strip()
        print(f'updating CHANGELOG with new section {ac.BOLD}{TAG}{ac.RESET}...')
        cl.update_changelog(
            'CHANGELOG',
            prev_tag=prev_tag,
            new_tag=TAG,
            save=True,
            print_n_sections=3,
            header_level=2,
            show_result=False,
            replace_latest=True,
        )

    # if cl.has_tag('CHANGELOG', 'latest'):
    #     print(f'found existing "latest" section in CHANGELOG, update and replace with {TAG}?\n')

    # all preflight checks passed
    msg.imsg('ready!', icon=sym.positive)

    # # show reminders if any
    # show_reminders(config['reminders'])


def check_release_branch(release_branch: str):
    if release_branch is False:
        msg.warning('skipping branch check as per configuration [release_branch = false].')
        return

    result, success = cmd.run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    if not success:
        msg.warning('failed to determine current branch!')
        return

    branch = result.stdout.strip()
    if branch != release_branch:
        msg.failure(f'you are on branch "{branch}". uv-ship config requires "{release_branch}"!')
        return
    else:
        msg.imsg(f'on release branch "{branch}".', icon=sym.positive)
        return


def check_worktree(repo_root, allow_dirty: bool = False, skip_input: bool = False):
    """Check for staged/unstaged changes before continuing."""
    result, _ = cmd.run_command(['git', 'status', '--porcelain'], cwd=repo_root)
    lines = result.stdout.splitlines()

    if not lines:
        print('✓ working tree clean.')
        tree_clean = True  # clean working tree

    else:
        proceed_dirty = False
        tree_clean = False

        staged = [line for line in lines if line[0] not in (' ', '?')]  # first column = staged
        unstaged = [line for line in lines if line[1] not in (' ', '?')]  # second column = unstaged

        if staged:
            if not allow_dirty:
                print(f'{sym.negative} you have staged changes. Please commit or unstage them before proceeding.')
            else:
                proceed_dirty = True

        if unstaged:
            if not allow_dirty:
                confirm = (
                    'y'
                    if skip_input
                    else input(f'{sym.warning} you have unstaged changes. Proceed anyway? [y/N]: ').strip().lower()
                )
                if confirm not in ('y', 'yes'):
                    msg.abort_by_user()
                else:
                    tree_clean = True
            else:
                proceed_dirty = True

        if proceed_dirty:
            print(f'{sym.warning} proceeding with uncommitted changes. [allow_dirty = true]')
            tree_clean = True

    exit(1) if not tree_clean else None


def check_tags(tag, repo_root):
    local_result, _ = cmd.run_command(['git', 'tag', '--list', tag], cwd=repo_root)
    remote_result, _ = cmd.run_command(['git', 'ls-remote', '--tags', 'origin', tag], cwd=repo_root)

    if remote_result.stdout.strip():
        msg.failure(f'tag {tag} already exists on the remote.')

    if local_result.stdout.strip():
        confirm = (
            input(f'{sym.warning} Tag {ac.BOLD}{tag}{ac.RESET} already exists locally. Overwrite? [y/N]: ')
            .strip()
            .lower()
        )
        if confirm not in ('y', 'yes'):
            msg.abort_by_user()
            tag_clear = False

        else:
            print(f'{sym.item} deleting existing local tag {tag}')
            cmd.run_command(['git', 'tag', '-d', tag], cwd=repo_root)
            tag_clear = True
    else:
        print(f'{sym.positive} no tag conflicts.')
        tag_clear = True

    exit(1) if not tag_clear else None


def show_reminders(reminders):
    if reminders:
        print('\n', end='')
        print('you have set reminders in your config:')
        for r in reminders or []:
            print(f'{sym.item} {r}')
