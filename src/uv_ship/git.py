from . import command as cmd
from .resources import ac, sym


def get_repo_root():
    result, success = cmd.run_command(['git', 'rev-parse', '--show-toplevel'])
    if not success:
        print(f'{sym.negative} not inside a Git repository.')
        exit(1)
    # else:
    #     print(f"{sym.positive} Inside a Git repository.")
    return result.stdout.strip()


def ensure_branch(release_branch: str):
    if release_branch is False:
        print(f'{sym.warning} skipping branch check as per configuration [release_branch = false].')
        return True

    result, success = cmd.run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    if not success:
        print(f'{sym.negative} failed to determine current branch.')
        return True

    branch = result.stdout.strip()
    if branch != release_branch:
        print(f"{sym.negative} you are on branch '{branch}'. uv-ship config requires '{release_branch}'.")
        return False

    print(f'{sym.positive} on release branch "{branch}".')
    return True


def ensure_clean_tree(repo_root, allow_dirty: bool = False):
    """Check for staged/unstaged changes before continuing."""
    result, _ = cmd.run_command(['git', 'status', '--porcelain'], cwd=repo_root)
    lines = result.stdout.splitlines()

    if not lines:
        print('✓ working tree clean.')
        return True  # clean working tree

    staged = [line for line in lines if line[0] not in (' ', '?')]  # first column = staged
    unstaged = [line for line in lines if line[1] not in (' ', '?')]  # second column = unstaged

    if staged:
        if not allow_dirty:
            print(f'{sym.negative} You have staged changes. Please commit or unstage them before proceeding.')
            proceed = False
        else:
            proceed = True

    if unstaged:
        if not allow_dirty:
            confirm = input(f'{sym.warning} You have unstaged changes. Proceed anyway? [y/N]: ').strip().lower()
            if confirm not in ('y', 'yes'):
                print(f'{ac.RED}{sym.negative} aborted by user.{ac.RESET}')
                return False
            else:
                return True
        else:
            proceed = True

    if proceed:
        print(f'{sym.warning} proceeding with uncommitted changes. [allow_dirty = true]')
        return True

    return False
