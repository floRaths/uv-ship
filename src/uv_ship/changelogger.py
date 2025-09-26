import re
from datetime import date
from pathlib import Path

from . import commands as cmd
from . import messages as msg

HEADER_ANY = re.compile(r'^#{1,6}\s+.*$', re.M)


def get_changelog():
    tag_res, ok = cmd.run_command(['git', 'describe', '--tags', '--abbrev=0'])
    base = tag_res[0].strip() if isinstance(tag_res, tuple) else tag_res.stdout.strip()

    result, _ = cmd.run_command(['git', 'log', f'{base}..HEAD', '--pretty=format:- %s'], print_stdout=False)

    return result.stdout


def _header_re(tag: str, level: int) -> re.Pattern:
    hashes = '#' * level
    # start of line, "## ", the tag, then either space/end/dash, then the rest of the line
    return re.compile(
        rf'^{re.escape(hashes)}\s+{re.escape(tag)}(?=\s|$|[-–—]).*$',
        re.M,
    )


def _find_section_span(content: str, tag: str, level: int):
    m = _header_re(tag, level).search(content)
    if not m:
        return None, None
    start = m.start()
    nxt = HEADER_ANY.search(content, pos=m.end())
    end = nxt.start() if nxt else len(content)
    return start, end


def _insertion_point_before_tag(content: str, prev_tag: str, level: int = 2) -> int:
    """
    Insert right before the previous-tag section if present.
    Otherwise, insert after the main title (a leading '# ...') if present.
    Otherwise, insert at the top.
    """
    prev_span = _find_section_span(content, prev_tag, level)
    if prev_span[0] is not None:
        return prev_span[0]

    # If the file starts with a title like "# Changelog", put new section after that title block
    first_hdr = HEADER_ANY.search(content, pos=0)
    if first_hdr and first_hdr.start() == 0 and len(first_hdr.group(0).split()[0]) == 1:
        # Find where the title block ends (right before the next header)
        next_hdr = HEADER_ANY.search(content, pos=first_hdr.end())
        if next_hdr:
            return next_hdr.start()
        else:
            return len(content)
    # Fallback: top of file
    return 0


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


def _read_changelog(changelog_path: str | Path) -> str:
    p = Path(changelog_path) if isinstance(changelog_path, str) else changelog_path
    if not p.exists():
        raise FileNotFoundError(f'Changelog file {changelog_path} does not exist.')
    return p.read_text(encoding='utf-8')


def prepare_new_section(new_tag: str, header_level: int = 2, add_date: bool = True) -> str:
    today = date.today().isoformat() if add_date else None
    header_line = f'{"#" * header_level} {new_tag}'
    if today:
        header_line += f' — [{today}]'
    header_line += '\n'

    commits = get_changelog()
    body = _normalize_bullets(commits)
    new_section = f'{header_line}\n{body}\n'
    return new_section


def has_tag(changelog_path: str | Path, tag: str) -> bool:
    content = _read_changelog(changelog_path)
    span = _find_section_span(content, tag, level=2)
    return span[0] is not None


def show_changelog(content: str, print_n_sections: int | None, header_level: int = 2):
    if print_n_sections is not None:
        # split on section headers of the same level
        section_re = re.compile(rf'^(#{{{header_level}}}\s+.*$)', re.M)
        parts = section_re.split(content)

        first_line = f'\n{msg.ac.BOLD}Updated CHANGELOG{msg.ac.RESET} (showing {print_n_sections} sections)\n\n'

        # parts alternates: [prefix_text, header1, body1, header2, body2, …]
        rendered = [first_line]
        for i in range(1, len(parts), 2):  # step through header/body pairs
            rendered.append(parts[i])  # header
            rendered.append(parts[i + 1])  # body
            if len(rendered) // 2 >= print_n_sections:
                break
        print(''.join(rendered))
    else:
        print(content)


def update_changelog(
    changelog_path: str,
    prev_tag: str,
    new_tag: str,
    header_level: int = 2,
    add_date: bool = True,
    overwrite_if_exists: bool = True,
    save: bool = True,
    show_result: bool = True,
    print_n_sections: int | None = None,
    replace_latest: bool = False,
):
    content = _read_changelog(changelog_path)

    new_section = prepare_new_section(new_tag, header_level, add_date)

    latest_span = _find_section_span(content, 'latest', header_level)

    new_span = latest_span if replace_latest else _find_section_span(content, new_tag, header_level)

    # If new_tag exists, replace its body (up to next header)
    # new_span = _find_section_span(content, new_tag, header_level)
    if new_span[0] is not None:
        if not overwrite_if_exists:
            raise ValueError(f'Section for {new_tag} already exists.')
        # Replace from header to next header with freshly built section
        updated = content[: new_span[0]] + new_section + content[new_span[1] :]

    else:
        # Insert before prev_tag section (or best-effort placement)
        insert_at = _insertion_point_before_tag(content, prev_tag, header_level)
        insert_at

        # Ensure nice spacing around insertion
        prefix = content[:insert_at].rstrip() + '\n\n' if insert_at > 0 else ''
        suffix = content[insert_at:].lstrip('\n')
        updated = prefix + new_section + ('\n' if not suffix.startswith('#') else '') + suffix

    if save:
        Path(changelog_path).write_text(updated, encoding='utf-8')

    if show_result:
        show_changelog(content=updated, print_n_sections=print_n_sections, header_level=header_level)
