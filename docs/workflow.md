# release workflow

`uv-ship` wraps the essentials of a release into five predictable stages. The flow is the same whether you bump with `uv-ship next` or set an explicit version with `uv-ship version`.

at a glance:
```
uv-ship next patch
└─ preview → preflight → changelog → update files → commit/tag/push
```

---

## 1. preview the version change
- Prints a colour-coded summary so you can sanity-check the bump before anything changes on disk.

## 2. run preflight checks
- **branch guard** – compares the active branch with `release-branch` and aborts if they differ (unless you set it to `false`).
- **tag safety** – checks both local and remote tags for conflicts with the tag that will be generated (`{tag-prefix}{version}`).
- **working tree status** – inspects Git status and blocks/warns when uncommited changes are present. Override per run with `--dirty` or permanently with `allow-dirty = true` in the config.

## 3. edit changelog (optional)
- offers to auto-build the next changelog section from commits messages since the previous tag.
!!! note
    you will have the chance to tidy up the section before the workflow proceeds with committing the file.

## 4. apply version changes
- under the hood, `uv-ship` simply calls `uv version` which updates `pyproject.toml` and `uv.lock` to the new version string.

## 5. ship it
- stages the updated files (`pyproject.toml`, `uv.lock`, and `CHANGELOG`).
- commits with the message `new version: {old} → {new}`.
- creates the Git tag and pushes both the commit and the tag to `origin`.

---

## interactive safeguards
- Use `--dry-run` at the root command to simulate the entire workflow without writing.
- Every destructive step (changelog save, file updates, push) is hidden behind an interactive confirmation.
Reply with anything other than `y` or `yes` to abort safely.
