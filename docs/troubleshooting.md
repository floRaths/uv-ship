## Troubleshooting
- **`not inside a Git repository`** – Make sure you are running the CLI somewhere under your project checkout.
- **`tag … already exists`** – Delete or rename the tag locally/remotely before retrying.
- **`uv` command fails** – Confirm the `uv` executable is available and that your project has a valid `pyproject.toml`.
- **Unexpected dirty working tree warning** – Use `git status --short` to inspect staged (`XY` column) and unstaged changes before proceeding.

## Troubleshooting
- **Not on release branch** – Update your `[tool.uv-ship]` config or check out the correct branch before retrying.
- **Tag already exists** – The tool refuses to overwrite remote tags. Delete/rename the existing tag (locally and remotely) and rerun.
- **Dirty working tree** – Either pass `--dirty` (per run) or set `allow-dirty = true` if you really intend to ship with pending changes.
- **`uv` not found** – Make sure `uv` is installed and discoverable. `uv-ship` shells out directly; the command must succeed.
