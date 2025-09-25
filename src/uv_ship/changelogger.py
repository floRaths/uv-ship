import re
from datetime import date
from pathlib import Path

HEADER_ANY = re.compile(r'^(#{1,6})\s+.+$', re.M)


def _header_regex_for_tag(tag: str) -> re.Pattern:
    """
    Accepts headers like:
      ## v0.4.3
      ### [v0.4.3]
      ## v0.4.3 - 2025-09-25
      ## [v0.4.3] — 2025-09-25
    """
    tag_esc = re.escape(tag)
    return re.compile(
        rf'^(?P<hashes>#{1, 6})\s+\[?{tag_esc}\]?(?:\s*[-–—]\s*\d{{4}}-\d{{2}}-\d{{2}})?\s*$',
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


def _find_section_span(content: str, header_re: re.Pattern):
    """
    Return (start_idx, end_idx, header_level) for the section whose header matches header_re.
    end_idx is the start of the *next* header (or len(content) if last).
    If not found, return (None, None, None).
    """
    match = header_re.search(content)
    if not match:
        return None, None, None
    start = match.start()
    level = len(match.group('hashes'))
    # next header of any level:
    next_match = HEADER_ANY.search(content, pos=match.end())
    end = next_match.start() if next_match else len(content)
    return start, end, level


def _insertion_point_before_tag(content: str, prev_tag: str):
    """
    Insert right before the previous-tag section if present.
    Otherwise, insert after the main title (a leading '# ...') if present.
    Otherwise, insert at the top.
    """
    prev_span = _find_section_span(content, _header_regex_for_tag(prev_tag))
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


def update_changelog(
    path: str | Path,
    prev_tag: str,
    new_tag: str,
    entries_text: str,
    header_level: int = 2,
    add_date: bool = True,
    overwrite_if_exists: bool = True,
) -> None:
    """
    Update CHANGELOG.md:
      - Insert a new section '## new_tag - YYYY-MM-DD' (or without date) with given entries
      - Place it immediately before the section for prev_tag (if found), else after the top title, else at top
      - If a section for new_tag already exists:
          * overwrite its body if overwrite_if_exists=True
          * else raise ValueError
    """
    path = Path(path)
    content = path.read_text(encoding='utf-8')

    # Prepare new header
    today = date.today().isoformat() if add_date else None
    header_line = f'{"#" * header_level} {new_tag}'
    if today:
        header_line += f' - {today}'
    header_line += '\n'

    body = _normalize_bullets(entries_text)
    new_section = f'{header_line}\n{body}'

    # If new_tag exists, replace its body (up to next header)
    new_span = _find_section_span(content, _header_regex_for_tag(new_tag))
    if new_span[0] is not None:
        if not overwrite_if_exists:
            raise ValueError(f'Section for {new_tag} already exists.')
        # Replace from header to next header with freshly built section
        updated = content[: new_span[0]] + new_section + content[new_span[1] :]
        path.write_text(updated, encoding='utf-8')
        return

    # Insert before prev_tag section (or best-effort placement)
    insert_at = _insertion_point_before_tag(content, prev_tag)

    # Ensure nice spacing around insertion
    prefix = content[:insert_at].rstrip() + '\n\n' if insert_at > 0 else ''
    suffix = content[insert_at:].lstrip('\n')
    updated = prefix + new_section + ('\n' if not suffix.startswith('#') else '') + suffix

    path.write_text(updated, encoding='utf-8')
