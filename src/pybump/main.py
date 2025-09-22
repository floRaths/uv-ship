from . import command as cmd
from . import config as cfg
from . import git as git
from .resources import sym

# ANSI codes
BOLD = '\033[1m'
ITALIC = '\033[3m'
UNDERLINE = '\033[4m'
RESET = '\033[0m'
GREEN = '\033[32m'
RED = '\033[31m'


def print_welcome(package_name, bump, current_version, new_version):
    welcome_message = [
        '',
        'The following operations will be performed:',
        '  1. update the version in pyproject.toml and uv.lock',
        '  2. create a tagged commit with the updated files',
        '  3. push the changes to the remote repository\n',
    ]
    print('\n'.join(welcome_message))


def get_version_str(return_project_name: bool = False):
    result, _ = cmd.run_command(['uv', 'version', '--color', 'never'])
    project_name, version = result.stdout.strip().split(' ')

    if return_project_name:
        return project_name, version

    return version


def check_tag(tag, repo_root):
    local_result, _ = cmd.run_command(['git', 'tag', '--list', tag], cwd=repo_root)
    remote_result, _ = cmd.run_command(['git', 'ls-remote', '--tags', 'origin', tag], cwd=repo_root)

    if remote_result.stdout.strip():
        print(f'{sym.negative} Tag {BOLD}{tag}{RESET} already exists on the remote. Aborting.')
        return None

    if local_result.stdout.strip():
        confirm = (
            input(f'{sym.warning} Tag {BOLD}{tag}{RESET} already exists locally. Overwrite? [y/N]: ').strip().lower()
        )
        if confirm not in ('y', 'yes'):
            print(f'{sym.negative} Aborted by user.')
            return None

        print(f'{sym.item} deleting existing local tag {tag}')
        cmd.run_command(['git', 'tag', '-d', tag], cwd=repo_root)

    return True


def main(bump: str, config_path: str = None):
    # Ensure we're in a git repo and point to its root
    print('\n', end='')
    print(f'{BOLD}uv-bump{RESET}', end=' - ')
    repo_root = git.get_repo_root()
    
    # Load config
    config = cfg.load_config(config_path, cwd=repo_root)
    exit(1) if not config else None
    
    # dry run to collect all info first
    result, _ = cmd.run_command(['uv', 'version', '--bump', bump, '--dry-run', '--color', 'never'])
    package_name, current_version, _, new_version = result.stdout.strip().split(' ')

    # Initial output message
    print(f'bumping to the next {ITALIC}{bump}{RESET} version:')
    print('\n', end='')
    print(f'{package_name} {BOLD}{RED}{current_version}{RESET} → {BOLD}{GREEN}{new_version}{RESET}\n')

    release_branch = config.get('release_branch', 'main')
    tag_prefix = config.get('tag_prefix', 'v')
    allow_dirty = config.get('allow_dirty', False)

    # Construct tag and message
    TAG = f'{tag_prefix}{new_version}'
    MESSAGE = f'new version: {current_version} → {new_version}'

    # check branch
    print(f'{sym.item} checking branch...')
    on_branch = git.ensure_branch(release_branch)
    exit(1) if not on_branch else None

    # check tag status
    print(f'{sym.item} checking tags...')
    tag_clear = check_tag(TAG, repo_root)
    exit(1) if not tag_clear else None

    tree_clean = git.ensure_clean_tree(repo_root, allow_dirty)
    exit(1) if not tree_clean else None

    print(f'{sym.positive} ready!')
    print_welcome(package_name, bump, current_version, new_version)

    # Interactive confirmation
    confirm = input('Do you want to proceed? [y/N]: ').strip().lower()
    if confirm not in ('y', 'yes'):
        print(f'{sym.negative} Aborted by user.')
        return

    print('\n')
    print(f'{sym.item} updating {package_name} version...')
    cmd.run_command(['uv', 'version', '--bump', bump])

    print(f'{sym.item} committing file changes')
    cmd.run_command(['git', 'add', 'pyproject.toml', 'uv.lock'], cwd=repo_root)
    cmd.run_command(['git', 'commit', '-m', MESSAGE], cwd=repo_root)

    print(f'{sym.item} creating git tag: {TAG}')
    cmd.run_command(['git', 'tag', TAG, '-m', MESSAGE], cwd=repo_root)

    print(f'{sym.item} pushing to remote repository...')
    cmd.run_command(['git', 'push'], cwd=repo_root)
    cmd.run_command(['git', 'push', 'origin', TAG], cwd=repo_root)

    print(f'\n{sym.positive} Done! New version registered and tagged.')


# if __name__ == '__main__':
