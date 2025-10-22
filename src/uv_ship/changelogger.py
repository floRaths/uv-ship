import re
import textwrap
from datetime import date
from pathlib import Path

from . import commands as cmd
from . import messages as msg

HEADER_ANY = re.compile(r'^#{1,6}\s+.*$', re.M)
H_LVL = 2

tag_format = '`'
DEFAULT_UNRELEASED_TAG = 'latest'


def get_config_latest_tag(config: dict) -> str:
    """Return the placeholder tag used for unreleased changes."""
    configured = config.get('unreleased-tag', DEFAULT_UNRELEASED_TAG)
    return configured or DEFAULT_UNRELEASED_TAG


def get_repo_url(config: dict) -> str | None:
    """Get repository URL from config or git remote."""
    # Use config override if provided
    if config.get('repo_url'):
        return config['repo_url']

    # Try to get from git remote
    result, success = cmd.run_command(['git', 'remote', 'get-url', 'origin'], print_stderr=False)
    if not success:
        return None

    remote_url = result.stdout.strip()

    # Parse different URL formats to get base commit URL
    # SSH format: git@github.com:user/repo.git
    if remote_url.startswith('git@'):
        match = re.match(r'git@([^:]+):(.+?)(?:\.git)?$', remote_url)
        if match:
            host, path = match.groups()
            return f'https://{host}/{path}'

    # HTTPS format: https://github.com/user/repo.git
    elif remote_url.startswith('http'):
        # Remove .git suffix if present
        base_url = remote_url.removesuffix('.git')
        # return f'{base_url}/commit'
        return base_url

    return None


def get_commits():
    """Get commits with hash and message since last tag."""
    _, has_commits = cmd.run_command(['git', 'rev-parse', '--quiet', '--verify', 'HEAD'], print_stderr=False)
    if not has_commits:
        return []

    tag_res, has_tag = cmd.run_command(['git', 'describe', '--tags', '--abbrev=0'], print_stderr=False)
    base = tag_res.stdout.strip() if has_tag else None

    # Format: hash|subject
    if base:
        log_args = ['git', 'log', f'{base}..HEAD', '--pretty=format:%h|%s']
    else:
        log_args = ['git', 'log', '--pretty=format:%h|%s']

    result, _ = cmd.run_command(log_args, print_stdout=False)

    commits = []
    for line in result.stdout.strip().split('\n'):
        if '|' in line:
            hash_short, message = line.split('|', 1)
            commits.append({'hash': hash_short, 'message': message})

    return commits


def format_commits(commits: list[dict], config: dict) -> str:
    """Format commits using the changelog template."""
    if not commits:
        return '- (no changes since last tag)'

    template = config.get('changelog_template', '- {message}')

    # Only get repo URL if template needs it
    repo_url = None
    if any(token in template for token in ('{commit_ref}', '{repo_url}')):
        repo_url = get_repo_url(config)
        if repo_url is None:
            msg.warning('Could not determine repository URL for changelog entries. Falling back to commit hashes.')

    formatted_lines = []
    for commit in commits:
        commit_hash = commit['hash']

        # Create commit reference (markdown link if repo URL available)
        if repo_url:
            commit_ref = f'[{commit_hash}]({repo_url}/commit/{commit_hash})'
        else:
            commit_ref = commit_hash

        # Replace template variables
        line = template.format(
            message=commit['message'],
            commit_ref=commit_ref,
            hash=commit_hash,
            commit_hash=commit_hash,
            repo_url=repo_url or commit_hash,
        )
        formatted_lines.append(line)

    return '\n'.join(formatted_lines)


def read_changelog(config: dict, clog_path: str | Path = None, tag_format: str = tag_format) -> str:
    if not clog_path:
        clog_path = Path(config['repo_root']) / config['changelog_path']

    p = Path(clog_path) if isinstance(clog_path, str) else clog_path

    if not p.exists():
        first_section = '## beginning of changelog'  # prepare_new_section('latest', add_date=True)
        p.write_text(f'# Changelog\n\n{first_section}', encoding='utf-8')

    return p.read_text(encoding='utf-8'), clog_path


def _header_re(tag: str, level: int = H_LVL) -> re.Pattern:
    tag = f'{tag_format}{tag}{tag_format}'
    hashes = '#' * level
    # start of line, "## ", the tag, then either space/end/dash, then the rest of the line
    return re.compile(
        rf'^{re.escape(hashes)}\s+{re.escape(tag)}(?=\s|$|[-–—]).*$',
        re.M,
    )


# def _normalize_bullets(text: str) -> str:
#     # Ensure each non-empty line starts with "- " and trim spaces
#     lines = []
#     for raw in text.splitlines():
#         s = raw.strip()
#         if not s:
#             continue
#         if not s.startswith('- '):
#             s = '- ' + s.lstrip('-•* ').strip()
#         lines.append(s)
#     return '\n'.join(lines) + '\n'


def find_section_spans(content: str, tag: str, level: int = H_LVL):
    """
    Find all sections with the given tag and level.
    Returns a list of (start, end) tuples.
    """
    spans = []
    matches = list(_header_re(tag, level).finditer(content))

    for i, m in enumerate(matches):
        start = m.start()
        nxt = HEADER_ANY.search(content, pos=m.end())
        end = nxt.start() if nxt else len(content)
        spans.append((start, end))

    return spans


def prepare_header(tag: str, add_date: bool = True, level: int = H_LVL) -> str:
    today = date.today().isoformat() if add_date else None
    header_line = f'{"#" * level} {tag_format}{tag}{tag_format}'
    if today:
        header_line += f' — [{today}]'
    return header_line


def prepare_new_section(new_tag: str, config: dict, add_date: bool = True, level: int = H_LVL) -> str:
    header_line = prepare_header(new_tag, add_date=add_date, level=level)

    commits = get_commits()
    body = format_commits(commits, config)

    new_section = f'{header_line}\n\n{body}\n\n'
    return new_section


def show_changelog(
    content: str,
    clog_file: str,
    print_n_sections: int = None,
    level: int = H_LVL,
    latest_placeholder: str = DEFAULT_UNRELEASED_TAG,
):
    if print_n_sections is not None:
        # split on section headers of the same level
        section_re = re.compile(rf'^(#{{{level}}}\s+.*$)', re.M)
        parts = section_re.split(content)

        report_n = print_n_sections if print_n_sections != 1 else latest_placeholder
        first_line = f'\n{msg.ac.BOLD}Updated {clog_file}{msg.ac.RESET} (showing {report_n} sections)\n\n'

        rendered = [first_line]
        for i in range(1, len(parts), 2):  # step through header/body pairs
            rendered.append(parts[i])  # header
            rendered.append(parts[i + 1])  # body
            if len(rendered) // 2 >= print_n_sections:
                break

        final_text = ''.join(rendered).strip()
        print(textwrap.indent(final_text, prefix='    '))
    else:
        print(textwrap.indent(content, prefix='    '))
        # print(content)


def _insert_content(content: str, new_section: str, span: tuple[int, int]) -> str:
    return content[: span[0]] + new_section + content[span[1] :]


def get_headers(clog_content: str):
    headers = HEADER_ANY.finditer(clog_content)

    clog_headers = []
    for header in headers:
        if header.group(0).startswith('##'):
            clog_headers.append(header)

    return clog_headers


def get_latest_clog_tag(clog_content: str, tag_format: str = tag_format) -> str:
    # headers = HEADER_ANY.finditer(clog_content)
    headers = get_headers(clog_content)
    first_header = next((h for h in headers), None)
    first_clog_tag = first_header.group().removeprefix('## ').split(' — ')[0]
    return first_clog_tag.strip(tag_format)


def replace_section(clog_content: str, new_section: str, span: tuple[int, int]):
    res = _insert_content(clog_content, new_section, span)
    return res


def strategy_apply(clog_content: str, new_tag: str):
    span = get_headers(clog_content)[0].span()
    new_header = prepare_header(new_tag)
    updated = replace_section(clog_content, new_header, span)
    return updated


def strategy_update(clog_content: str, new_section: str):
    headers = get_headers(clog_content)
    first_header = next((h for h in headers), None)
    span = first_header.start(), first_header.start()

    res = _insert_content(clog_content, new_section, span)
    return res


def strategy_replace(clog_content: str, new_section: str, latest_clog_tag: str):
    spans = find_section_spans(clog_content, latest_clog_tag)
    if len(spans) > 1:
        print(f'Warning: Found multiple sections for tag {latest_clog_tag}. Replacing the first one.')
    clog_updated = replace_section(clog_content, new_section, spans[0])
    return clog_updated


def eval_clog_update_strategy(config: dict, clog_content: str, new_tag: str, print_eval: bool = False):
    latest_repo_tag = cmd.git.get_latest_tag()
    latest_clog_tag = get_latest_clog_tag(clog_content)
    latest_placeholder = get_config_latest_tag(config)

    strategy = 'unknown'
    if not latest_repo_tag:
        if print_eval:
            print('No tags found in repository. Can not evaluate changelog update strategy.')
        strategy = 'update'
    elif latest_clog_tag == latest_repo_tag:
        if print_eval:
            print('The changelog has not been updated since the last release.')
        strategy = 'update'
    elif latest_clog_tag in (latest_placeholder, new_tag):
        if print_eval:
            print(
                'The changelog was already updated since the last release, do you want to apply this tag, or refresh it?'
            )
        strategy = 'prompt'
    else:
        msg.warning(
            f'latest changelog tag ({latest_clog_tag}) does not match latest Git tag ({latest_repo_tag}).',
        )
        strategy = 'update'
    return strategy, latest_repo_tag, latest_clog_tag


def execute_update_strategy(config, clog_path, clog_content, new_tag, strategy, save, **kwargs):
    new_section = prepare_new_section(new_tag, config, add_date=True)
    latest_placeholder = get_config_latest_tag(config)

    if strategy == 'prompt':
        print(
            f'It looks like the changelog was already updated since the last release (`{latest_placeholder}` is present).'
        )

        msg.imsg('run: `uv-ship log --latest` to compare with latest commits\n', icon=msg.sym.item, color=msg.ac.BLUE)

        if new_tag == latest_placeholder:
            confirm = input('do you want to refresh the changelog? [y|N]:').strip().lower()

            if confirm in ('y', 'yes'):
                strategy = 'replace'

        else:
            confirm = input(f'refresh changelog or apply tag {new_tag} to that section? [r|A]:').strip().lower()
            if confirm in ('r', 'replace'):
                strategy = 'replace'
            else:
                strategy = 'apply'

    if strategy == 'update':
        clog_updated = strategy_update(clog_content, new_section)
    elif strategy == 'replace':
        clog_updated = strategy_replace(clog_content, new_section, latest_placeholder)
    elif strategy == 'apply':
        clog_updated = strategy_apply(clog_content, new_tag)
    else:
        msg.failure(f'unknown changelog update strategy: {strategy}')

    show_changelog(
        content=clog_updated, clog_file=config['changelog_path'], latest_placeholder=latest_placeholder, **kwargs
    )
    print('')

    if save:
        clog_path.write_text(clog_updated, encoding='utf-8')
