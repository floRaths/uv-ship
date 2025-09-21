import subprocess


def get_proj_version():
    result = subprocess.run(['uv', 'version', '--short', '--color', 'never'], capture_output=True, text=True)
    return result.stdout.rstrip('\n')


def bump_proj_version(which):
    subprocess.run(['uv', 'version', '--bump', which])


def run_command(command, expand=True):

    if expand:
        c_expanded = command.split(' ')
    else:
        c_expanded = command

    result = subprocess.run(
        c_expanded,
        capture_output=True,
        text=True,
    )

    success = True if result.returncode == 0 else False

    print(result.stdout)

    if result.returncode != 0:
        print('Exit code:', result.returncode)
        print('Error:', result.stderr)

    return result, success
