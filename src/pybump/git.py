from . import command as cmd


def get_repo_root():
    result, success = cmd.run_command(['git', 'rev-parse', '--show-toplevel'])
    if not success:
        print('❌ Not inside a Git repository.')
        exit(1)
    # else:
    #     print("✅ Inside a Git repository.")
    return result.stdout.strip()


def ensure_branch(release_branch: str):
    if release_branch is False:
        print('Skipping branch check as per configuration [release_branch = false].')
        return

    result, success = cmd.run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    if not success:
        print('❌ Failed to determine current branch.')
        exit(1)

    branch = result.stdout.strip()
    if branch != release_branch:
        print(f"❌ You are on branch '{branch}'. uv-bump config requires '{release_branch}'.")
        exit(1)
