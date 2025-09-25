from . import commands as cmd
from . import messages as msg
from .resources import ac, sym


def run_preflight(config, TAG):
    # check branch
    ensure_branch(config['release_branch'])

    # check tag status
    check_tag(TAG, config['repo_root'])

    # check working tree status
    ensure_clean_tree(config['repo_root'], config['dirty'])

    # all preflight checks passed
    msg.imsg('ready!', icon=sym.positive)

    # show reminders if any
    show_reminders(config['reminders'])


def ensure_branch(release_branch: str):
    if release_branch is False:
        print(f'{sym.warning} skipping branch check as per configuration [release_branch = false].')
        on_branch = True

    result, success = cmd.run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    if not success:
        print(f'{sym.negative} failed to determine current branch.')
        on_branch = True

    branch = result.stdout.strip()
    if branch != release_branch:
        print(f"{sym.negative} you are on branch '{branch}'. uv-ship config requires '{release_branch}'.")
        on_branch = False
    else:
        print(f'{sym.positive} on release branch "{branch}".')
        on_branch = True

    exit(1) if not on_branch else None


def ensure_clean_tree(repo_root, allow_dirty: bool = False):
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
                confirm = input(f'{sym.warning} you have unstaged changes. Proceed anyway? [y/N]: ').strip().lower()
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


def check_tag(tag, repo_root):
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
