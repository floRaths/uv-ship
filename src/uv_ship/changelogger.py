import re
from datetime import date
from pathlib import Path

# import uv_ship
from . import commands as cmd

# # get the root of the repo relative to the package
# root = Path(uv_ship.__file__).resolve().parent.parent.parent
# changelog_path = root / 'CHANGELOG'

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


def update_changelog(
    path: str,
    prev_tag: str,
    new_tag: str,
    header_level: int = 2,
    add_date: bool = True,
    overwrite_if_exists: bool = True,
    save: bool = True,
):
    commits: str = get_changelog()

    path = Path(path)
    content = path.read_text(encoding='utf-8')

    # Prepare new header
    today = date.today().isoformat() if add_date else None
    header_line = f'{"#" * header_level} {new_tag}'
    if today:
        header_line += f' — [{today}]'
    header_line += '\n'

    body = _normalize_bullets(commits)
    new_section = f'{header_line}\n{body}\n'

    # If new_tag exists, replace its body (up to next header)
    new_span = _find_section_span(content, new_tag, header_level)
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
        path.write_text(updated, encoding='utf-8')

    print(updated)
