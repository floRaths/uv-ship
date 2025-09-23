from . import commands as cmd
from . import config as cfg
from .resources import ac, sym
from .resources import messages as msg


def main(bump: str, config_path: str = None, allow_dirty: bool = False):
    # welcome
    msg.print_header()

    # ensure we're in a git repo and point to its root
    repo_root = cmd.get_repo_root()

    # Load config
    config = cfg.load_config(config_path, cwd=repo_root)

    # dry run to collect all info first
    package_name, current_version, new_version = cmd.collect_info(bump)

    # show summary
    msg.print_command_summary(bump, package_name, current_version, new_version)

    release_branch = config.get('release_branch', 'main')
    tag_prefix = config.get('tag_prefix', 'v')
    allow_dirty = config['allow_dirty'] if 'allow_dirty' in config else allow_dirty
    reminders = config.get('reminders', None)

    # Construct tag and message
    TAG, MESSAGE = cmd.tag_and_message(tag_prefix, current_version, new_version)

    # check branch
    cmd.ensure_branch(release_branch)

    # check tag status
    cmd.check_tag(TAG, repo_root)

    # check working tree status
    cmd.ensure_clean_tree(repo_root, allow_dirty)

    print(f'{sym.positive} ready!')

    # show reminders if any
    msg.show_reminders(reminders)

    # show operations
    msg.step_by_step_operations()

    # Interactive confirmation
    confirm = input('do you want to proceed? [y/N]: ').strip().lower()
    if confirm not in ('y', 'yes'):
        msg.abort_by_user()
        return

    # TODO safeguard these steps and rollback on failure
    print(f'{sym.item} updating {package_name} version')
    cmd.run_command(['uv', 'version', '--bump', bump])

    print(f'{sym.item} committing file changes')
    cmd.run_command(['git', 'add', 'pyproject.toml', 'uv.lock'], cwd=repo_root)
    cmd.run_command(['git', 'commit', '-m', MESSAGE], cwd=repo_root)

    print(f'{sym.item} creating git tag: {TAG}')
    cmd.run_command(['git', 'tag', TAG, '-m', MESSAGE], cwd=repo_root)

    print(f'{sym.item} pushing to remote repository')
    cmd.run_command(['git', 'push'], cwd=repo_root)
    cmd.run_command(['git', 'push', 'origin', TAG], cwd=repo_root)

    print(f'\n{ac.GREEN}{sym.positive} done! new version registered and tagged.{ac.RESET}\n')


# if __name__ == '__main__':
