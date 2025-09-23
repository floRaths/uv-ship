import subprocess

from .resources import ac, sym
from .resources import messages as msg


def run_command(args: list, cwd: str = None, print_stdout: bool = False):
    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if print_stdout and result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print('Exit code:', result.returncode)
        print('Error:', result.stderr)
    return result, result.returncode == 0


def get_repo_root():
    result, success = run_command(['git', 'rev-parse', '--show-toplevel'])
    if not success:
        print(f'{sym.negative} not inside a Git repository.')
        exit(1)
    # else:
    #     print(f"{sym.positive} Inside a Git repository.")
    return result.stdout.strip()


def collect_info(bump: str):
    result, _ = run_command(['uv', 'version', '--bump', bump, '--dry-run', '--color', 'never'])
    package_name, current_version, _, new_version = result.stdout.strip().split(' ')
    return package_name, current_version, new_version


def tag_and_message(tag_prefix: str, current_version: str, new_version: str):
    TAG = f'{tag_prefix}{new_version}'
    MESSAGE = f'new version: {current_version} → {new_version}'
    return TAG, MESSAGE


def ensure_branch(release_branch: str):
    if release_branch is False:
        print(f'{sym.warning} skipping branch check as per configuration [release_branch = false].')
        on_branch = True

    result, success = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
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
    result, _ = run_command(['git', 'status', '--porcelain'], cwd=repo_root)
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


def get_changelog():
    tag_res, ok = run_command(['git', 'describe', '--tags', '--abbrev=0'])
    base = tag_res[0].strip() if isinstance(tag_res, tuple) else tag_res.stdout.strip()

    result, _ = run_command(['git', 'log', f'{base}..HEAD', '--pretty=format:- %s'], print_stdout=False)

    return result.stdout


def get_version_str(return_project_name: bool = False):
    result, _ = run_command(['uv', 'version', '--color', 'never'])
    project_name, version = result.stdout.strip().split(' ')

    if return_project_name:
        return project_name, version

    return version


def check_tag(tag, repo_root):
    local_result, _ = run_command(['git', 'tag', '--list', tag], cwd=repo_root)
    remote_result, _ = run_command(['git', 'ls-remote', '--tags', 'origin', tag], cwd=repo_root)

    if remote_result.stdout.strip():
        print(f'{sym.negative} Tag {ac.BOLD}{tag}{ac.RESET} already exists on the remote. Aborting.')
        tag_clear = False

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
            run_command(['git', 'tag', '-d', tag], cwd=repo_root)
            tag_clear = True
    else:
        print(f'{sym.positive} no tag conflicts.')
        tag_clear = True

    exit(1) if not tag_clear else None


def update_files(package_name, bump):
    print(f'{sym.item} updating {package_name} version')
    result, success = run_command(['uv', 'version', '--bump', bump])
    exit(1) if not success else None


def commit_files(repo_root, MESSAGE):
    print(f'{sym.item} committing file changes')

    result, success = run_command(['git', 'add', 'pyproject.toml', 'uv.lock'], cwd=repo_root)
    exit(1) if not success else None

    result, success = run_command(['git', 'commit', '-m', MESSAGE], cwd=repo_root)
    exit(1) if not success else None


def create_git_tag(TAG, MESSAGE, repo_root):
    print(f'{sym.item} creating git tag: {TAG}')
    result, success = run_command(['git', 'tag', TAG, '-m', MESSAGE], cwd=repo_root)
    exit(1) if not success else None


def push_changes(TAG, repo_root):
    print(f'{sym.item} pushing to remote repository')

    result, success = run_command(['git', 'push'], cwd=repo_root)
    exit(1) if not success else None

    result, success = run_command(['git', 'push', 'origin', TAG], cwd=repo_root)
    exit(1) if not success else None
