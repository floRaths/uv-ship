import argparse
import subprocess


def run_command(command, print_stdout=True):
    c_expanded = command

    result = subprocess.run(
        c_expanded,
        capture_output=True,
        text=True,
    )

    success = True if result.returncode == 0 else False

    if print_stdout:
        if len(result.stdout) > 0:
            print(result.stdout)

    if result.returncode != 0:
        print('Exit code:', result.returncode)
        print('Error:', result.stderr)

    return result, success


def main():
    parser = argparse.ArgumentParser(description='Bump version, create git tag, and push changes.')
    parser.add_argument('bump', choices=['major', 'minor', 'patch'], help='Type of version bump.')
    args = parser.parse_args()

    bump = args.bump

    result, success = run_command(['uv', 'version', '--color', 'never'], print_stdout=False)
    current_version = result.stdout.strip().split(' ')
    project_name = current_version[0]
    current_version = current_version[1]

    print(f'Bumping "{project_name}" to the next {bump} version.')

    run_command(['uv', 'version', '--bump', bump], print_stdout=True)

    result, success = run_command(['uv', 'version', '--short', '--color', 'never'], print_stdout=False)
    new_version = result.stdout.strip()

    TAG = f'v{new_version}'
    MESSAGE = f'new version: {current_version} → {new_version}'

    print('committing updated pyproject.toml and uv.lock files')
    result, success = run_command(['git', 'add', 'pyproject.toml', 'uv.lock'])
    result, success = run_command(['git', 'commit', '-m', MESSAGE], print_stdout=False)
    print(f'creating git tag: {TAG}')
    result, success = run_command(['git', 'tag', TAG, '-m', MESSAGE])
    print('pushing changes to remote repository')
    result, success = run_command(['git', 'push'])
    result, success = run_command(['git', 'push', 'origin', TAG])
    print('✅ Done! New version registered and tagged.')


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='Bump version, create git tag, and push changes.')
#     parser.add_argument('bump', choices=['major', 'minor', 'patch'], help='Type of version bump.')

#     args = parser.parse_args()
#     main(args.bump)
