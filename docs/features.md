## CLI overview
- `uv-ship next <bump-type>` – bump `pyproject.toml` & `uv.lock`, update the changelog (optional), commit, tag, push.
- `uv-ship tag <version>` – set a specific version without calculating the bump. (Commit/tag/push is currently skipped; this workflow is focused on preparing files.)
- `uv-ship log [--latest] [--save]` – show or persist the changelog section built from commits after the latest tag.

Pass `--dry-run` on the root command to rehearse any of the subcommands without touching disk:

```console
uv-ship --dry-run next minor
```

ALT
## Command tour
### `uv-ship next <bump-type>`
Calculates the next semantic version (`major`, `minor`, or `patch`), runs the preflight checks, offers to refresh the changelog, updates version metadata, and (unless in dry run) commits, tags, and pushes.

### `uv-ship tag <version>`
Sets `pyproject.toml`/`uv.lock` to an explicit version after running the same validation flow. This path is useful if you curate the release commit yourself.

### `uv-ship log [--latest] [--save]`
Builds a changelog section from commits since the latest Git tag. Use `--latest` to preview without writing, or `--save` to persist the top section of your configured changelog file.

Start every invocation with `uv-ship --dry-run …` if you just want to see the script of actions.

Pass `--dirty` to `uv-ship next`/`uv-ship tag` for a one-off override of the `allow-dirty` setting.


## Working with changelogs
- The changelog reader points to `changelog-path`; make sure the file exists (default: `CHANGELOG`).
- Generated sections take the form `## {tag} — [YYYY-MM-DD]` with normalised bullet lists.
- When updating, the tool compares the latest Git tag with the latest changelog heading:
  - If they match, the section is replaced.
  - If not, the new section is inserted at the top.
- `uv-ship log --latest` always prints to the terminal, whereas `--save` writes the changes (unless `--dry-run` is active).


## Working with changelogs
The changelog routines look at the most recent Git tag and gather commit summaries since that point. When you save (`uv-ship log --save` or accept the prompt in `uv-ship next`):

- A new section using the target tag (or the literal `latest`) is written at the top of the changelog file.
- Dates are embedded automatically (`## v1.2.3 — [YYYY-MM-DD]`).
- Bullet formatting is normalised so every entry renders well in Markdown.
- If the latest changelog section already matches the latest Git tag, the content is replaced instead of duplicated.

The default changelog path is simply `CHANGELOG`; set `changelog-path` if your project uses a different filename.
