import subprocess

from . import messages as msg
from .resources import sym


def run_command(args: list, cwd: str = None, print_stdout: bool = False, print_stderr: bool = True):
    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if print_stdout and result.stdout:
        print(result.stdout)
    if print_stderr and result.returncode != 0:
        # print('Exit code:', result.returncode)
        print('Error:', result.stderr)
    return result, result.returncode == 0


# TODO this should be re-used in changelogger prepare_new_section
def get_latest_tag(fetch: bool = True) -> str | None:
    if fetch:
        _, _ = run_command(['git', 'fetch', '--tags'], print_stderr=False)
    res, success = run_command(['git', 'describe', '--tags', '--abbrev=0'], print_stderr=False)
    if success:
        return res.stdout.strip()
    return None


def get_repo_root():
    result, success = run_command(['git', 'rev-parse', '--show-toplevel'], print_stderr=False)
    if not success:
        msg.failure('not inside a Git repository.')
    # else:
    #     print(f"{sym.positive} Inside a Git repository.")
    return result.stdout.strip()


def collect_info(version: str = None):
    result, _ = run_command(['uv', 'version', version, '--dry-run', '--color', 'never'])
    package_name, old_version, _, new_version = result.stdout.strip().split(' ')
    return package_name, old_version, new_version


def calculate_version(bump_type: str, pre_release: str = None):
    command = ['uv', 'version', '--dry-run', '--color', 'never', '--bump', bump_type]
    command = command if not pre_release else command + ['--bump', pre_release]
    r, _ = run_command(command)
    return r.stdout.strip().split(' ')[-1]


def tag_and_message(tag_prefix: str, new_version: str, current_version: str = None):
    TAG = f'{tag_prefix}{new_version}'

    if current_version:
        MESSAGE = f'new version: {current_version} → {new_version}'
    else:
        MESSAGE = f'new version: {new_version}'

    return TAG, MESSAGE


def get_version_str(return_project_name: bool = False):
    result, _ = run_command(['uv', 'version', '--color', 'never'])
    project_name, version = result.stdout.strip().split(' ')

    if return_project_name:
        return project_name, version

    return version


def update_files(config, package_name, version):
    msg.imsg(f'updating {package_name} version', icon=sym.item)

    if not config['dry_run']:
        _, success = run_command(['uv', 'version', version])
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
