import subprocess

from . import messages as msg
from .resources import sym


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


def get_latest_tag(fetch: bool = True) -> str:
    if fetch:
        _, _ = run_command(['git', 'fetch', '--tags'])
    res, _ = run_command(['git', 'describe', '--tags', '--abbrev=0'])
    latest_tag = res.stdout.strip()
    return latest_tag


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


def get_version_str(return_project_name: bool = False):
    result, _ = run_command(['uv', 'version', '--color', 'never'])
    project_name, version = result.stdout.strip().split(' ')

    if return_project_name:
        return project_name, version

    return version


def update_files(config, package_name):
    msg.imsg(f'updating {package_name} version', icon=sym.item)

    if not config['dry_run']:
        if 'bump_type' in config:
            _, success = run_command(['uv', 'version', '--bump', config['bump_type']])
            exit(1) if not success else None

        if 'version' in config:
            _, success = run_command(['uv', 'version', config['version']])
            exit(1) if not success else None


def commit_files(config, MESSAGE):
    msg.imsg('committing file changes', icon=sym.item)

    if not config['dry_run']:
        _, success = run_command(['git', 'add', 'pyproject.toml', 'uv.lock', 'CHANGELOG'], cwd=config['repo_root'])
        msg.failure('failed to add files to git') if not success else None

        _, success = run_command(['git', 'commit', '-m', MESSAGE], cwd=config['repo_root'])
        msg.failure('failed to commit changes') if not success else None


def create_git_tag(config, TAG, MESSAGE):
    msg.imsg(f'creating git tag: {TAG}', icon=sym.item)

    if not config['dry_run']:
        _, success = run_command(['git', 'tag', TAG, '-m', MESSAGE], cwd=config['repo_root'])
        msg.failure('failed to create git tag') if not success else None


def push_changes(config, TAG):
    msg.imsg('pushing to remote repository', icon=sym.item)

    if not config['dry_run']:
        _, success = run_command(['git', 'push'], cwd=config['repo_root'])
        msg.failure('failed to push file changes') if not success else None

        _, success = run_command(['git', 'push', 'origin', TAG], cwd=config['repo_root'])
        msg.failure('failed to push tag') if not success else None


# region unused
def pre_commit_checks():
    msg.imsg('running pre-commit checks', icon=sym.item)
    _, success = run_command(['pre-commit', 'run', '--all-files'], print_stdout=False)
    msg.failure('failed to run pre-commit checks') if not success else None
