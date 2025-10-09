from uv_ship.changelogger import format_commits


def test_format_commits_with_commit_hash_only():
    commits = [{'hash': 'abc1234', 'message': 'Fix bug'}]
    config = {'changelog_template': '{message} - {commit_hash}'}

    result = format_commits(commits, config)

    assert result == 'Fix bug - abc1234'


def test_format_commits_with_repo_url_and_commit_hash():
    commits = [{'hash': 'deadbeef', 'message': 'Add feature'}]
    config = {
        'changelog_template': '{message} - {repo_url}:{commit_hash}',
        'repo_url': 'https://example.com/commit',
    }

    result = format_commits(commits, config)

    assert result == 'Add feature - https://example.com/commit:deadbeef'


def test_format_commits_with_commit_ref_default_link():
    commits = [{'hash': 'abcd123', 'message': 'Improve docs'}]
    config = {
        'changelog_template': '- {commit_ref}',
        'repo_url': 'https://example.com/commit',
    }

    result = format_commits(commits, config)

    assert result == '- [abcd123](https://example.com/commit/abcd123)'
