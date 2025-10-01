from .. import messages as msg
from ..resources import sym
from .run import run_command


# TODO this should be re-used in changelogger prepare_new_section
def get_latest_tag(fetch: bool = True) -> str | None:
    if fetch:
        _, _ = run_command(['git', 'fetch', '--tags'], print_stderr=False)
    res, success = run_command(['git', 'describe', '--tags', '--abbrev=0'], print_stderr=False)
    if success:
        return res.stdout.strip()
    return None


def get_repo_root():
    result, success = run_command(['git', 'rev-parse', '--show-toplevel'], print_stderr=False)
    if not success:
        msg.failure('not inside a Git repository.')
    # else:
    #     print(f"{sym.positive} Inside a Git repository.")
    return result.stdout.strip()


def commit_files(config, MESSAGE):
    msg.imsg('committing file changes', icon=sym.item)

    if not config['dry_run']:
        _, success = run_command(['git', 'add', 'pyproject.toml', 'uv.lock', 'CHANGELOG'], cwd=config['repo_root'])
        msg.failure('failed to add files to git') if not success else None

        _, success = run_command(['git', 'commit', '-m', MESSAGE], cwd=config['repo_root'])
        msg.failure('failed to commit changes') if not success else None


def create_git_tag(config, TAG, MESSAGE):
    msg.imsg(f'creating git tag: {TAG}', icon=sym.item)

    if not config['dry_run']:
        _, success = run_command(['git', 'tag', TAG, '-m', MESSAGE], cwd=config['repo_root'])
        msg.failure('failed to create git tag') if not success else None


def push_changes(config, TAG):
    msg.imsg('pushing to remote repository', icon=sym.item)

    if not config['dry_run']:
        _, success = run_command(['git', 'push'], cwd=config['repo_root'])
        msg.failure('failed to push file changes') if not success else None

        _, success = run_command(['git', 'push', 'origin', TAG], cwd=config['repo_root'])
        msg.failure('failed to push tag') if not success else None
