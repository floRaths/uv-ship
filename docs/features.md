---
toc_depth: 3
---

<br>

# CLI reference

### `uv-ship`

The main entrypoint to access uv-ship features

<span class="acc-2-text">**usage:**</span> `uv-ship [options] command [args]`

> ##### options:
> `--config` Path to config file (inferred if not provided).  
> `--dry-run` Show what would be done without making any changes.  
> `--self` Display uv-ship version.  
> `--help` Show a help message and exit.  

---


## commands
### `uv-ship next`

Calculates the next semantic version (`major`, `minor`, or `patch`), runs the preflight checks, offers to refresh the changelog, updates version metadata, and executes the commit/tag/push sequence unless running as a dry run.

<span class="acc-2-text">**usage:**</span> `uv-ship next [options] RELEASE_TYPE`

possible values:  
`major`, `minor`, `patch`, `stable`

can be paired with pre-release components:  
`alpha`, `beta`, `rc`, `post`, `dev`

to remove pre-release status, pass `stable` as release version


> ##### options:
> `--pre-release` Pre-release component (e.g. alpha, beta).  
> `--dirty` Allow dirty working directory.  
> `--help` Show this message and exit.  

---

### `uv-ship version`
Prepares and ships the provided version. This path allows you to break out of semantic versioning conventions if desired.

<span class="acc-2-text">**usage:**</span> `uv-ship version [options] {VERSION}`

> ##### options:
> `--dirty` Allow dirty working directory.  
> `--help` Show this message and exit.  

---

### `uv-ship calver`
Determines current date and creates a version number in the format `YYYY.m.d` (e.g. 2026.1.13) runs the preflight checks, offers to refresh the changelog, updates version metadata, and executes the commit/tag/push sequence unless running as a dry run.

<span class="acc-2-text">**usage:**</span> `uv-ship calver [options]`

> ##### options:
> `--dirty` Allow dirty working directory.  
> `--help` Show this message and exit.  

---

### `uv-ship log`
Builds a changelog section from commits since the latest Git tag. Use `--latest` to preview without writing, or `--save` to persist the top section of your configured changelog file.

<span class="acc-2-text">**usage:**</span> `uv-ship log [options]`

> ##### options:
> `--latest` Show all commits since the last tag.  
> `--save` Save changes to the changelog.  
> `--help` Show this message and exit.  

---

### `uv-ship status`
Display a status report for the current package.

<span class="acc-2-text">**usage:**</span> `uv-ship status`

> ##### options:
> `--help` Show this message and exit.  

---

## working with changelogs
- The reader targets the configured `changelog-path` (default: `CHANGELOG`); ensure the file exists.
- Generated sections take the form `## vX.Y.Z — [YYYY-MM-DD]`, with bullet formatting normalised for Markdown.
- When refreshing, the tool compares the newest Git tag against the latest changelog heading:
  - If they match, the section is replaced.
  - Otherwise, the new section is inserted at the top of the file.
- `uv-ship log --latest` always prints to the terminal, whereas `--save` writes the content unless `--dry-run` is active.
