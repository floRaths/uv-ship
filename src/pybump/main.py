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


def get_repo_root():
    result, success = run_command(['git', 'rev-parse', '--show-toplevel'], print_stdout=False)
    if not success:
        print('❌ Not inside a Git repository.')
        exit(1)
    # else:
    #     print("✅ Inside a Git repository.")
    return result.stdout.strip()


def run_git_command(args, cwd=None, print_stdout=True):
    result = subprocess.run(
        ['git'] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if print_stdout and result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print('Exit code:', result.returncode)
        print('Error:', result.stderr)
    return result, result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description='Bump version, create git tag, and push changes.')
    parser.add_argument('bump', choices=['major', 'minor', 'patch'], help='Type of version bump.')
    args = parser.parse_args()

    bump = args.bump

    repo_root = get_repo_root()

    result, success = run_command(['uv', 'version', '--color', 'never'], print_stdout=False)
    current_version = result.stdout.strip().split(' ')
    project_name = current_version[0]
    current_version = current_version[1]

    print('\n')
    print(f'Bumping "{project_name}" to the next {bump} version:')
    run_command(['uv', 'version', '--bump', bump, '--dry-run'], print_stdout=True)

    print('This will perform the following actions:')
    print('  1. Update the version in pyproject.toml and uv.lock')
    print('  2. Create a tagged commit with the updated files')
    print('  3. Push the changes to the remote repository\n')

    # Interactive confirmation
    confirm = input('Do you want to proceed? [y/N]: ').strip().lower()
    if confirm not in ('y', 'yes'):
        print('❌ Aborted by user.')
        return

    print(f'\nUpdating {project_name} version...\n')
    run_command(['uv', 'version', '--bump', bump], print_stdout=False)

    result, success = run_command(['uv', 'version', '--short', '--color', 'never'], print_stdout=False)
    new_version = result.stdout.strip()

    TAG = f'v{new_version}'
    MESSAGE = f'new version: {current_version} → {new_version}'

    print('committing updated pyproject.toml and uv.lock files')
    run_git_command(['add', 'pyproject.toml', 'uv.lock'], cwd=repo_root)
    run_git_command(['commit', '-m', MESSAGE], cwd=repo_root, print_stdout=False)

    print(f'creating git tag: {TAG}')
    run_git_command(['tag', TAG, '-m', MESSAGE], cwd=repo_root)

    print('pushing changes to remote repository')
    run_git_command(['push'], cwd=repo_root)
    run_git_command(['push', 'origin', TAG], cwd=repo_root)

    print('✅ Done! New version registered and tagged.')


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='Bump version, create git tag, and push changes.')
#     parser.add_argument('bump', choices=['major', 'minor', 'patch'], help='Type of version bump.')

#     args = parser.parse_args()
#     main(args.bump)
