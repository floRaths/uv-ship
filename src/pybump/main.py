from . import command as cmd
from . import config as cfg
from . import git as git

# ANSI codes
BOLD = '\033[1m'
RESET = '\033[0m'
GREEN = '\033[32m'
RED = '\033[31m'


def print_welcome(package_name, bump, current_version, new_version):
    welcome_message = [
        # '\n',
        f'\nBumping "{package_name}" to the next {bump} version:',
        f'{BOLD}{RED}{current_version}{RESET} → {BOLD}{GREEN}{new_version}{RESET}\n',
        'The following steps will be performed:',
        '  1. Update the version in pyproject.toml and uv.lock',
        '  2. Create a tagged commit with the updated files',
        '  3. Push the changes to the remote repository\n',
    ]
    print('\n'.join(welcome_message))


def get_version_str(return_project_name: bool = False):
    result, _ = cmd.run_command(['uv', 'version', '--color', 'never'])
    project_name, version = result.stdout.strip().split(' ')

    if return_project_name:
        return project_name, version

    return version


def main(bump: str, config_path: str = None):
    print(f'\n{BOLD}Initializing uv-bump...{RESET}')
    repo_root = git.get_repo_root()

    config = cfg.load_config(config_path, cwd=repo_root)
    if not config:
        exit(1)

    release_branch = config.get('release_branch', 'main')
    tag_prefix = config.get('tag_prefix', 'v')
    git.ensure_branch(release_branch)

    result, _ = cmd.run_command(['uv', 'version', '--bump', 'patch', '--dry-run', '--color', 'never'])
    package_name, current_version, _, new_version = result.stdout.strip().split(' ')

    TAG = f'{tag_prefix}{new_version}'
    MESSAGE = f'new version: {current_version} → {new_version}'

    print_welcome(package_name, bump, current_version, new_version)

    # Interactive confirmation
    confirm = input('Do you want to proceed? [y/N]: ').strip().lower()
    if confirm not in ('y', 'yes'):
        print('❌ Aborted by user.')
        return

    print(f'\n• updating {package_name} version...')
    cmd.run_command(['uv', 'version', '--bump', bump])

    print('• committing file changes')
    cmd.run_command(['git', 'add', 'pyproject.toml', 'uv.lock'], cwd=repo_root)
    cmd.run_command(['git', 'commit', '-m', MESSAGE], cwd=repo_root)

    print(f'• creating git tag: {TAG}')
    cmd.run_command(['git', 'tag', TAG, '-m', MESSAGE], cwd=repo_root)

    print('• pushing to remote repository')
    cmd.run_command(['git', 'push'], cwd=repo_root)
    cmd.run_command(['git', 'push', 'origin', TAG], cwd=repo_root)

    print('\n✓ Done! New version registered and tagged.')


# if __name__ == '__main__':
