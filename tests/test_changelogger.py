from uv_ship.changelogger import commit_url_base, format_commits, normalize_repo_url


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


def test_format_commits_strips_credentials_from_repo_url():
    commits = [{'hash': 'feed123', 'message': 'Sanitize URL'}]
    config = {
        'changelog_template': '- {commit_ref}',
        'repo_url': 'https://user:token@github.com/org/repo.git',
    }

    result = format_commits(commits, config)

    assert result == '- [feed123](https://github.com/org/repo/commit/feed123)'


def test_normalize_repo_url_strips_credentials_and_git_suffix():
    url = 'https://user:pass@github.example.com:8443/org/project.git'

    assert normalize_repo_url(url) == 'https://github.example.com:8443/org/project'


def test_normalize_repo_url_no_change_for_non_http():
    url = 'ssh://git@github.com/org/project.git'

    assert normalize_repo_url(url) == 'ssh://git@github.com/org/project.git'


def test_commit_url_base_trims_commit_suffix():
    assert commit_url_base('https://example.com/repo/commit') == 'https://example.com/repo'
    assert commit_url_base('https://example.com/repo') == 'https://example.com/repo'
