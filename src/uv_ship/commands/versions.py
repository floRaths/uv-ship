from .. import messages as msg
from .run import run_command


def get_git_version(short=False):
    res, _ = run_command(['git', '--version'], print_stderr=False)
    return res.stdout.strip().split()[2], _


def get_gh_version(short=False):
    res, _ = run_command(['gh', '--version'], print_stderr=False)
    short_v = res.stdout.strip().split()[-3]
    long_v = res.stdout.strip().split('\n')[0].split('version ')[-1]
    if short:
        return short_v, _
    return long_v, _


def get_uv_version(short=False):
    res, _ = run_command(['uv', 'self', 'version', '--short', '--color', 'never'], print_stderr=False)
    if short:
        return res.stdout.strip().split()[0], _
    return res.stdout.strip(), _


def get_uv_ship_version(short=False):
    res, _ = run_command(['uv-ship', '--self'], print_stderr=False)
    if short:
        return res.stdout.strip().split()[-1], _
    return res.stdout.strip(), _


def get_self_version(short=False):
    from importlib.metadata import version

    return version('uv_ship'), True


def get_tool_versions(print_status=False):
    versions = {
        'git': {'func': get_git_version(short=True), 'required': True},
        'github': {'func': get_gh_version(short=True), 'required': False},
        'uv': {'func': get_uv_version(short=True), 'required': True},
        'uv-ship': {'func': get_self_version(short=True), 'required': True},
    }

    results = {}
    for k, param in versions.items():
        version, _ = param['func']
        if not _ and param['required']:
            if print_status:
                msg.failure(f'{k} is not installed or not available on PATH.')
            # version = False
        elif not _ and not param['required']:
            if print_status:
                msg.warning(f'{k} is not installed or not available on PATH.')
            # version = False
        elif _ and param['required']:
            if print_status:
                msg.success(f'{k} is installed and available on PATH.')
            results[k] = version

    return results
