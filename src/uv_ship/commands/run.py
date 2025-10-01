import subprocess


def run_command(args: list, cwd: str = None, print_stdout: bool = False, print_stderr: bool = True):
    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if print_stdout and result.stdout:
        print(result.stdout)
    if print_stderr and result.returncode != 0:
        # print('Exit code:', result.returncode)
        print('Error:', result.stderr)
    return result, result.returncode == 0
