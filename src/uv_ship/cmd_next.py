from . import commands as cmd
from . import config as cfg
from . import messages as msg
from . import preflight as prf
from .resources import ac


def next_workflow(config: str = None, **kwargs):
    # welcome
    print_header()

    # ensure we're in a git repo and point to its root
    repo_root = cmd.get_repo_root()

    # Load config
    config = cfg.load_config(path=config, cwd=repo_root, cmd_args=kwargs)
    print(config)

    # dry run to collect all info first
    package_name, current_version, new_version = cmd.collect_info(config['bump_type'])

    # show summary
    print_command_summary(config, package_name, current_version, new_version)

    # Construct tag and message
    TAG, MESSAGE = cmd.tag_and_message(config['tag_prefix'], current_version, new_version)

    # run preflight checks
    prf.run_preflight(config, TAG)

    # show operations
    step_by_step_operations()

    # Interactive confirmation
    confirm = input('do you want to proceed? [y/N]: ').strip().lower()
    if confirm not in ('y', 'yes'):
        msg.abort_by_user()
        return

    # cmd.pre_commit_checks()

    # # TODO test safeguards
    cmd.update_files(config, package_name)

    cmd.commit_files(config, MESSAGE)

    cmd.create_git_tag(config, TAG, MESSAGE)

    cmd.push_changes(config, TAG)

    msg.success(f'done! new version {new_version} registered and tagged.\n')


def print_header():
    print('\n', end='')
    msg.imsg('uv-ship', color=ac.BOLD)  # , end=' - ')


def print_command_summary(config, package_name, current_version, new_version):
    bump = config['bump_type']
    print(f'bumping to the next {ac.ITALIC}{bump}{ac.RESET} version:')
    print('\n', end='')

    if config['dry_run']:
        msg.imsg('>> THIS IS A DRY RUN - NO CHANGES WILL BE PUSHED <<\n', color=ac.DIM)

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
