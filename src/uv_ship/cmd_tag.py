from . import commands as cmd
from . import config as cfg
from . import messages as msg
from . import preflight as prf
from .resources import ac


def collect_info():
    result, _ = cmd.run_command(['uv', 'version', '--color', 'never'])
    package_name, current_version = result.stdout.strip().split(' ')
    return package_name, current_version


def tag_and_message(tag_prefix: str, current_version: str):
    TAG = f'{tag_prefix}{current_version}'
    MESSAGE = f'new version: {current_version}'
    return TAG, MESSAGE


def tag_workflow(config: str = None, **kwargs):
    # welcome
    print_header()

    # ensure we're in a git repo and point to its root
    repo_root = cmd.get_repo_root()

    # Load config
    config = cfg.load_config(path=config, cwd=repo_root, cmd_args=kwargs)

    # dry run to collect all info first
    package_name, current_version = collect_info()

    # show summary
    print_command_summary(config, package_name, current_version, config['version'])

    # Construct tag and message
    TAG, MESSAGE = cmd.tag_and_message(config['tag_prefix'], current_version, config['version'])

    # run preflight checks
    prf.run_preflight(config, TAG)

    # show operations
    step_by_step_operations()

    # Interactive confirmation
    confirm = input('do you want to proceed? [y/N]: ').strip().lower()
    if confirm not in ('y', 'yes'):
        msg.abort_by_user()
        return

    # # cmd.pre_commit_checks()

    # # TODO test safeguards
    cmd.update_files(config, package_name)

    # cmd.commit_files(repo_root, MESSAGE)

    # cmd.create_git_tag(TAG, MESSAGE, repo_root)

    # cmd.push_changes(TAG, repo_root)

    # msg.success(f'done! new version {new_version} registered and tagged.\n')


def print_header():
    print('\n', end='')
    msg.imsg('uv-ship', color=ac.BOLD)  # , end=' - ')


def print_command_summary(config, package_name, current_version, new_version):
    print(f'setting project {package_name} to version {new_version}:')
    print('\n', end='')

    if config['dry_run']:
        msg.imsg('>> THIS IS A DRY RUN - NO CHANGES WILL BE MADE <<\n', color=ac.DIM)

    print(f'{package_name} {ac.BOLD}{ac.RED}{current_version}{ac.RESET} → {ac.BOLD}{ac.GREEN}{new_version}{ac.RESET}\n')


def step_by_step_operations():
    operations_message = [
        '',
        'the following operations will be performed:',
        '  1. update version in pyproject.toml and uv.lock',
        '  2. create a tagged commit with the updated files',
        '  3. push changes to the remote repository\n',
    ]
    print('\n'.join(operations_message))
