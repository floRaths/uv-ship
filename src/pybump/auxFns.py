import argparse
import subprocess


def run_command(command):
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


def main():
    parser = argparse.ArgumentParser(description="Bump version, create git tag, and push changes.")
    parser.add_argument("bump", choices=["major", "minor", "patch"], help="Type of version bump.")
    args = parser.parse_args()

    bump = args.bump

    result, success = run_command(['uv', 'version', '--short', '--color', 'never'])
    current_version = result.stdout.strip()

    run_command(['uv', 'version', '--bump', bump])

    result, success = run_command(['uv', 'version', '--short', '--color', 'never'])
    new_version = result.stdout.strip()

    TAG = f'v{new_version}'
    MESSAGE = f'new version: {current_version} → {new_version}'

    result, success = run_command(['git', 'add', 'pyproject.toml', 'uv.lock'])
    result, success = run_command(['git', 'commit', '-m', MESSAGE])
    result, success = run_command(['git', 'tag', TAG, '-m', MESSAGE])
    result, success = run_command(['git', 'push'])
    result, success = run_command(['git', 'push', 'origin', TAG])


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='Bump version, create git tag, and push changes.')
#     parser.add_argument('bump', choices=['major', 'minor', 'patch'], help='Type of version bump.')

#     args = parser.parse_args()
#     main(args.bump)
