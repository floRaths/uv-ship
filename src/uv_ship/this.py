from . import commands as cmd
from . import config as cfg
from . import messages as msg
from .resources import ac, sym


def collect_info():
    result, _ = cmd.run_command(['uv', 'version', '--color', 'never'])
    package_name, current_version = result.stdout.strip().split(' ')
    return package_name, current_version


def tag_and_message(tag_prefix: str, current_version: str):
    TAG = f'{tag_prefix}{current_version}'
    MESSAGE = f'new version: {current_version}'
    return TAG, MESSAGE


def this(config: str = None, **kwargs):
    # welcome
    print_header()

    # ensure we're in a git repo and point to its root
    repo_root = cmd.get_repo_root()

    # Load config
    config = cfg.load_config(path=config, cwd=repo_root)
    args = {k.replace('_', '-'): v for k, v in kwargs.items()}
    config.update(args)

    # dry run to collect all info first
    package_name, current_version = collect_info()

    # show summary
    print_command_summary(package_name, current_version)

    # Construct tag and message
    TAG, MESSAGE = tag_and_message(config['tag-prefix'], current_version)

    # check branch
    cmd.ensure_branch(config['release-branch'])

    # check tag status
    cmd.check_tag(TAG, repo_root)

    # check working tree status
    cmd.ensure_clean_tree(repo_root, config['dirty'])

    # all preflight checks passed
    msg.imsg('ready!', icon=sym.positive)

    # show reminders if any
    show_reminders(config['reminders'])

    # show operations
    step_by_step_operations()

    # # Interactive confirmation
    # confirm = input('do you want to proceed? [y/N]: ').strip().lower()
    # if confirm not in ('y', 'yes'):
    #     msg.abort_by_user()
    #     return

    # # cmd.pre_commit_checks()

    # # # TODO test safeguards
    # cmd.update_files(package_name, config['bump-type'])

    # cmd.commit_files(repo_root, MESSAGE)

    # cmd.create_git_tag(TAG, MESSAGE, repo_root)

    # cmd.push_changes(TAG, repo_root)

    # msg.success(f'done! new version {new_version} registered and tagged.\n')


def print_header():
    print('\n', end='')
    msg.imsg('uv-ship', color=ac.BOLD)  # , end=' - ')


def print_command_summary(package_name, current_version):
    print('releasing the current package version:')
    print('\n', end='')
    print(f'{package_name} {ac.BOLD}{ac.GREEN}{current_version}{ac.RESET}\n')


def step_by_step_operations():
    operations_message = [
        '',
        'the following operations will be performed:',
        '  1. update version in pyproject.toml and uv.lock',
        '  2. create a tagged commit with the updated files',
        '  3. push changes to the remote repository\n',
    ]
    print('\n'.join(operations_message))


def show_reminders(reminders):
    if reminders:
        print('\n', end='')
        print('you have set reminders in your config:')
        for r in reminders or []:
            print(f'{sym.item} {r}')
