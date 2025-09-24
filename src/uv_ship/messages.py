from .resources import ac, sym


def imsg(text: str, icon=None, color=None, **kwargs):
    icon = '' if icon is None else f'{icon} '
    color = ac.RESET if color is None else color
    print(f'{color}{icon}{text}{ac.RESET}', **kwargs)


def failure(message):
    imsg(f'{message}\n', icon=sym.negative, color=ac.RED)
    exit(1)


def success(message):
    imsg(f'{message}', icon=sym.positive, color=ac.GREEN)


def abort_by_user():
    failure('aborted by user.')
