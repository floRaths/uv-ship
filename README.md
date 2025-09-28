# uv-ship
<div style="margin-top:-3rem; display:block;">
a CLI-tool for shipping with uv
</div>

---
`uv-ship` is a lightweight companion to [`uv`](https://docs.astral.sh/uv/) that removes the risky parts of cutting a release. It verifies the repo state, bumps your project metadata, optionally refreshes the changelog, commits, tags & pushes the result, while giving you the chance to review every step.

## Key capabilities
- **Version automation**: drive uv version to bump or set the next release number, keeping pyproject.toml and uv.lock in sync.
- **Preflight checks**: guard your release workflow by verifying branch, tags, and a clean working tree before shipping.
- **Changelog generation**: auto-builds changelog sections from commits since the latest tag.
- **One-shot release**: stage, commit, tag, and push in a single step.
- **Dry-run mode**: preview every action before making changes.

---
## Installation
Add `uv-ship` to a project managed by uv:

```console
uv add uv-ship
```

Or install it as a standalone CLI tool:

```console
uv tool install uv-ship
```

---
## Quick start
1. Ensure your working tree is clean and that you are on the configured release branch.
2. Run `uv-ship next patch` (or `minor` / `major`).
3. Review the changelog preview, confirm the prompts, and watch the tag and push finish.

Prefer to set an explicit version? Use `uv-ship tag 1.2.0` instead of bumping.

Need to inspect the changelog first? Run `uv-ship log --latest` to preview commits since the last tag or `uv-ship log --save` to refresh the configured changelog file.

---
## CLI overview
- `uv-ship next <bump-type>` – bump `pyproject.toml` & `uv.lock`, update the changelog (optional), commit, tag, push.
- `uv-ship tag <version>` – set a specific version without calculating the bump. (Commit/tag/push is currently skipped; this workflow is focused on preparing files.)
- `uv-ship log [--latest] [--save]` – show or persist the changelog section built from commits after the latest tag.

Pass `--dry-run` on the root command to rehearse any of the subcommands without touching disk:

```console
uv-ship --dry-run next minor
```

---
## Requirements
- a project running Python 3.8+
- [uv 0.7.0](https://docs.astral.sh/uv/) or later on your `PATH`
- a Git repository

---

Happy shipping!
