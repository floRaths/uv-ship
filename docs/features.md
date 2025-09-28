# CLI reference

### `uv-ship`
usage: `uv-ship [option] command [args]`

#### options:
  `--config` Path to config file (inferred if not provided).
  `--dry-run` Show what would be done without making any changes.
  `--help` Show a help message and exit.

---


## commands
### `uv-ship next`

calculates the next semantic version (`major`, `minor`, or `patch`), runs the preflight checks, offers to refresh the changelog, updates version metadata, and executes the commit/tag/push sequence unless running as a dry run.

usage: `uv-ship next [options] {major|minor|patch}`

possible values:
- major, minor, patch
- not yet supported: stable, alpha, beta, rc, post, dev

#### options:
  `--dirty` Allow dirty working directory.
  `--help` Show this message and exit.

---

### `uv-ship version`
sets `pyproject.toml`/`uv.lock` to the provided version. This path is handy when you have already prepared the release commit and only need the metadata updates.

usage: `uv-ship version [options] {VERSION}`

#### options:
  `--dirty` Allow dirty working directory.
  `--help` Show this message and exit.

---

### `uv-ship log`
Builds a changelog section from commits since the latest Git tag. Use `--latest` to preview without writing, or `--save` to persist the top section of your configured changelog file.

usage: `uv-ship log [options]`

#### options:
  `--latest` Show all commits since the last tag.
  `--save` Save changes to the changelog.
  `--help` Show this message and exit.

---

## Working with changelogs
- The reader targets the configured `changelog-path` (default: `CHANGELOG`); ensure the file exists.
- Generated sections take the form `## vX.Y.Z — [YYYY-MM-DD]`, with bullet formatting normalised for Markdown.
- When refreshing, the tool compares the newest Git tag against the latest changelog heading:
  - If they match, the section is replaced.
  - Otherwise, the new section is inserted at the top of the file.
- `uv-ship log --latest` always prints to the terminal, whereas `--save` writes the content unless `--dry-run` is active.
