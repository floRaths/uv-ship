from .resources import ac, sym


def imsg(text: str, icon=None, color=None, **kwargs):
    icon = '' if icon is None else f'{icon} '
    color = ac.RESET if color is None else color
    print(f'{color}{icon}{text}{ac.RESET}', **kwargs)


def failure(message):
    imsg(f'{message}\n', icon=sym.negative, color=ac.RED)
    exit(1)


def warning(message):
    imsg(f'{message}', icon=sym.warning, color=ac.YELLOW)


def success(message):
    imsg(f'{message}', icon=sym.positive, color=ac.GREEN)


def abort_by_user():
    failure('aborted by user.')


def dry_run_warning():
    imsg('>> THIS IS A DRY RUN - NO CHANGES WILL BE MADE <<\n', color=ac.DIM)


def welcome_message():
    print('')
    imsg(f'{ac.GREEN}uv-ship', color=ac.BOLD, end=' - ')
    imsg('a CLI-tool for shipping with uv', color=None)


def preflight_complete():
    print('')
    imsg('have you updated the documentation?', icon=None, color=ac.BLUE)

    # all preflight checks passed
    print('')
    imsg(f'{"-" * 62}', icon=None)
    imsg('If everything looks good, you can proceed with the release.', icon=None)
    # msg.imsg('ready to ship!', icon=sym.positive)

    step_by_step_operations()


def step_by_step_operations():
    operations_message = [
        '',
        'the following operations will be performed:',
        '  1. update version in pyproject.toml and uv.lock',
        '  2. create a tagged commit with the updated files',
        '  3. push changes to the remote repository\n',
    ]
    print('\n'.join(operations_message))


def user_confirmation():
    confirm = input('do you want to proceed? [y/N]: ').strip().lower()
    if confirm not in ('y', 'yes'):
        abort_by_user()
