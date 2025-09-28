## End-to-end workflow
1. **Collect details** – `uv-ship` runs `uv version --dry-run` to discover the package name, current version, and bump target.
2. **Preflight checks**
    - Confirms the active branch matches `release-branch`
    - Warns about unstaged or staged changes (respecting `allow-dirty` or `--dirty`)
    - Guards against local or remote tag conflicts
3. **Changelog assistance** – optional prompt to generate the upcoming section. Accepting it will (when not in dry run) update the configured changelog file.
4. **File updates** – reruns `uv version` so `pyproject.toml` and `uv.lock` contain the new version string.
5. **Ship** – stages the touched files, commits them as `new version: {old} → {new}`, creates the Git tag, and pushes both commit and tag to `origin`.

If you answer anything other than `y`/`yes` to the final confirmation, the process stops without side effects.

## Release flow in detail
1. **Collect facts** – Calls `uv version` in dry-run mode to discover the package name and next version.
2. **Preflight** – Confirms the release branch, detects existing tags locally and remotely, and validates the working tree.
3. **Changelog assist** – Optionally builds a changelog section from commits since the last Git tag and shows the result before saving.
4. **Update project files** – Runs `uv version` again (without `--dry-run`) so `pyproject.toml` and `uv.lock` carry the new version.
5. **Ship** – Stages the changed files, commits them with a standard message, creates the Git tag, and pushes both the commit and the tag.

Every step emits contextual messages with symbols/colours to highlight what happens next. If at any point you respond with anything other than `y`/`yes`, the tool aborts without side effects.
