import re
from datetime import date
from pathlib import Path

from . import commands as cmd
from . import messages as msg

HEADER_ANY = re.compile(r'^#{1,6}\s+.*$', re.M)
H_LVL = 2


def get_commits():
    tag_res, _ = cmd.run_command(['git', 'describe', '--tags', '--abbrev=0'])
    base = tag_res[0].strip() if isinstance(tag_res, tuple) else tag_res.stdout.strip()

    result, _ = cmd.run_command(['git', 'log', f'{base}..HEAD', '--pretty=format:- %s'], print_stdout=False)

    return result.stdout


def read_changelog(config: dict, clog_path: str | Path = None) -> str:
    if not clog_path:
        clog_path = Path(config['repo_root']) / config['changelog_path']

    p = Path(clog_path) if isinstance(clog_path, str) else clog_path
    if not p.exists():
        raise FileNotFoundError(f'Changelog file {clog_path} does not exist.')
    return p.read_text(encoding='utf-8'), clog_path


def _header_re(tag: str, level: int = H_LVL) -> re.Pattern:
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


def prepare_new_section(new_tag: str, add_date: bool = True, level: int = H_LVL) -> str:
    today = date.today().isoformat() if add_date else None
    header_line = f'{"#" * level} {new_tag}'
    if today:
        header_line += f' — [{today}]'
    header_line += '\n'

    commits = get_commits()
    body = _normalize_bullets(commits)
    new_section = f'{header_line}\n{body}\n'
    return new_section


def show_changelog(content: str, print_n_sections: int | None, level: int = H_LVL):
    if print_n_sections is not None:
        # split on section headers of the same level
        section_re = re.compile(rf'^(#{{{level}}}\s+.*$)', re.M)
        parts = section_re.split(content)

        report_n = print_n_sections if print_n_sections != 1 else 'latest'
        first_line = f'\n{msg.ac.BOLD}Updated CHANGELOG{msg.ac.RESET} (showing {report_n} sections)\n\n'

        rendered = [first_line]
        for i in range(1, len(parts), 2):  # step through header/body pairs
            rendered.append(parts[i])  # header
            rendered.append(parts[i + 1])  # body
            if len(rendered) // 2 >= print_n_sections:
                break
        print(''.join(rendered).strip())
    else:
        print(content)


def insert_new_section(content: str, new_section: str, span: tuple[int, int]) -> str:
    return content[: span[0]] + new_section + content[span[1] :]


def get_latest_clog_tag(clog_content: str) -> str:
    headers = HEADER_ANY.finditer(clog_content)
    first_header = next((h for h in headers if h.group().startswith('## ')), None)
    first_clog_tag = first_header.group().removeprefix('## ').split(' — ')[0]
    return first_clog_tag


def add_new_section(clog_content: str, new_section: str):
    headers = HEADER_ANY.finditer(clog_content)
    first_header = next((h for h in headers if h.group().startswith('## ')), None)
    span = first_header.start(), first_header.start()

    res = insert_new_section(clog_content, new_section, span)
    return res


def replace_section(clog_content: str, new_section: str, span: tuple[int, int]):
    res = insert_new_section(clog_content, new_section, span)
    return res


def update_changelog(config: dict, tag: str, save: bool = True, show_result: int = 0):
    new_section = prepare_new_section(tag)

    clog_content, clog_path = read_changelog(config=config)

    latest_tag = cmd.get_latest_tag()  # TODO maybe move this to a separate section
    latest_clog_tag = get_latest_clog_tag(clog_content)

    if latest_clog_tag == latest_tag:
        # print('The changelog need to be updated for the last release.')
        replace = False
    elif latest_clog_tag in ('latest', tag):
        # print('The changelog was already updated for the last release, but needs to be refreshed.')
        replace = True
    else:
        msg.warning(
            f'latest changelog tag ({latest_clog_tag}) does not match latest Git tag ({latest_tag}).',
        )
        replace = False

    if not replace:
        clog_updated = add_new_section(clog_content, new_section)
    else:
        spans = find_section_spans(clog_content, latest_clog_tag)
        if len(spans) > 1:
            print(f'Warning: Found multiple sections for tag {latest_clog_tag}. Replacing the first one.')
        clog_updated = replace_section(clog_content, new_section, spans[0])

    if save:
        clog_path.write_text(clog_updated, encoding='utf-8')

    if show_result > 0:
        show_changelog(content=clog_updated, print_n_sections=show_result)
