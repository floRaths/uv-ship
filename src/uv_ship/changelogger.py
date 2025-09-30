import re
from datetime import date
from pathlib import Path

from . import commands as cmd
from . import messages as msg

HEADER_ANY = re.compile(r'^#{1,6}\s+.*$', re.M)
H_LVL = 2

tag_format = '`'


def get_commits():
    _, has_commits = cmd.run_command(['git', 'rev-parse', '--quiet', '--verify', 'HEAD'], print_stderr=False)
    if not has_commits:
        return 'there are no commits in the repository yet...'

    tag_res, has_tag = cmd.run_command(['git', 'describe', '--tags', '--abbrev=0'], print_stderr=False)
    base = tag_res.stdout.strip() if has_tag else None

    # if there is no tag, show all commits
    if base:
        log_args = ['git', 'log', f'{base}..HEAD', '--pretty=format:- %s']
    else:
        log_args = ['git', 'log', '--pretty=format:- %s']

    result, _ = cmd.run_command(log_args, print_stdout=False)
    return result.stdout


def read_changelog(config: dict, clog_path: str | Path = None, tag_format: str = tag_format) -> str:
    if not clog_path:
        clog_path = Path(config['repo_root']) / config['changelog_path']

    p = Path(clog_path) if isinstance(clog_path, str) else clog_path

    if not p.exists():
        first_section = prepare_new_section('latest', add_date=True)
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


def _normalize_bullets(text: str) -> str:
    # Ensure each non-empty line starts with "- " and trim spaces
    lines = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if not s.startswith('- '):
            s = '- ' + s.lstrip('-•* ').strip()
        lines.append(s)
    return '\n'.join(lines) + '\n'


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


def prepare_new_section(new_tag: str, add_date: bool = True, level: int = H_LVL) -> str:
    header_line = prepare_header(new_tag, add_date=add_date, level=level)

    commits = get_commits()
    if len(commits) == 0:
        commits = '- (no changes since last tag)'

    body = _normalize_bullets(commits)
    new_section = f'{header_line}\n\n{body}\n'
    return new_section


def show_changelog(content: str, clog_file: str, print_n_sections: int | None, level: int = H_LVL):
    if print_n_sections is not None:
        # split on section headers of the same level
        section_re = re.compile(rf'^(#{{{level}}}\s+.*$)', re.M)
        parts = section_re.split(content)

        report_n = print_n_sections if print_n_sections != 1 else 'latest'
        first_line = f'\n{msg.ac.BOLD}Updated {clog_file}{msg.ac.RESET} (showing {report_n} sections)\n\n'

        rendered = [first_line]
        for i in range(1, len(parts), 2):  # step through header/body pairs
            rendered.append(parts[i])  # header
            rendered.append(parts[i + 1])  # body
            if len(rendered) // 2 >= print_n_sections:
                break
        print(''.join(rendered).strip())
    else:
        print(content)


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


def eval_clog_update_strategy(clog_content: str, new_tag: str):
    latest_repo_tag = cmd.get_latest_tag()
    latest_clog_tag = get_latest_clog_tag(clog_content)

    # print(f'Latest Git tag: {latest_repo_tag}')
    # print(f'Latest changelog tag: {latest_clog_tag}')

    strategy = 'unknown'
    if not latest_repo_tag:
        print('No tags found in repository. Can not evaluate changelog update strategy.')
        strategy = 'update'
    elif latest_clog_tag == latest_repo_tag:
        print('The changelog has not been updated since the last release.')
        strategy = 'update'
    elif latest_clog_tag in ('latest', new_tag):
        print('The changelog was already updated since the last release, do you want to apply this tag, or refresh it?')
        strategy = 'prompt'
    else:
        msg.warning(
            f'latest changelog tag ({latest_clog_tag}) does not match latest Git tag ({latest_repo_tag}).',
        )
        strategy = 'update'
    return strategy


def update_changelog(config: dict, new_tag: str, save: bool = True, show_result: int = 0, prompt: bool = False):
    clog_content, clog_path = read_changelog(config=config)

    strategy = eval_clog_update_strategy(clog_content, new_tag)

    if strategy == 'prompt' and prompt:
        confirm = input('apply tag or refresh changelog? [r|A]:').strip().lower()
        if confirm in ('r', 'replace'):
            strategy = 'replace'
        else:
            strategy = 'apply'
    elif strategy == 'prompt' and not prompt:
        strategy = 'apply'

    new_section = prepare_new_section(new_tag)

    if strategy == 'update':
        clog_updated = strategy_update(clog_content, new_section)
    elif strategy == 'replace':
        clog_updated = strategy_replace(clog_content, new_section, 'latest')
    elif strategy == 'apply':
        clog_updated = strategy_apply(clog_content, new_tag)
    else:
        msg.failure(f'unknown changelog update strategy: {strategy}')

    if save:
        clog_path.write_text(clog_updated, encoding='utf-8')

    if show_result > 0:
        show_changelog(content=clog_updated, clog_file=config['changelog_path'], print_n_sections=show_result)
