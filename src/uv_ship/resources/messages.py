from . import ac, sym


def print_header():
    print('\n', end='')
    print(f'{ac.BOLD}uv-ship{ac.RESET}', end=' - ')


def failed_to(reason):
    print(f'{ac.RED}{sym.negative} failed to {reason}.{ac.RESET}\n')
    exit(1)


def abort_by_user():
    print(f'{ac.RED}{sym.negative} aborted by user.{ac.RESET}\n')


def preflight_passed():
    print(f'{sym.positive} ready!')


def print_command_summary(bump, package_name, current_version, new_version):
    print(f'bumping to the next {ac.ITALIC}{bump}{ac.RESET} version:')
    print('\n', end='')
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


def show_reminders(reminders):
    if reminders:
        print('\n', end='')
        print('you have set reminders in your config:')
        for r in reminders or []:
            print(f'{sym.item} {r}')


def done():
    print(f'\n{ac.GREEN}{sym.positive} done! new version registered and tagged.{ac.RESET}\n')
