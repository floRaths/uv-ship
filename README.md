# uv-ship
<div style="margin-top:-3rem; display:block;">
a CLI-tool for shipping with uv
</div>

`uv-ship` is a lightweight companion to [uv](https://docs.astral.sh/uv/) that removes the risky parts of cutting a release. It verifies the repo state, bumps your project metadata and optionally refreshes the changelog. It then commits, tags & pushes the result, while giving you the chance to review every step.

## key capabilities
- **Version automation**: drive uv version to bump or set the next release number, keeping pyproject.toml and uv.lock in sync.
- **Preflight checks**: guard your release workflow by verifying branch, tags, and a clean working tree before shipping.
- **Changelog generation**: auto-builds changelog sections from commits since the latest tag.
- **One-shot release**: stage, commit, tag, and push in a single step.
- **Dry-run mode**: preview every action before making changes.

---
## installation
Add `uv-ship` to a project managed by uv:

```console
uv add uv-ship
```

Or install it as a standalone CLI tool:

```console
uv tool install uv-ship
```

---
## quick start
1. Ensure your working tree is clean and that you are on the configured release branch.
2. Run `uv-ship next patch` (or `minor` / `major`).
3. Review the changelog preview, confirm the prompts, and watch the tag and push finish.

Prefer to set an explicit version? Use `uv-ship version 1.2.0` instead of bumping.

Need to inspect the changelog first? Run `uv-ship log --latest` to preview commits since the last tag or `uv-ship log --save` to refresh the configured changelog file.
