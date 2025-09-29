<!-- --8<-- "README.md" -->
# uv-ship
<div style="margin-top:-3rem; display:block;">
  <a class="uv-link" href="">a CLI-tool for shipping with uv</a>
</div>

<br>


`uv-ship` is a lightweight companion to [uv](https://docs.astral.sh/uv/) that removes the risky parts of cutting a release. It verifies the repo state, bumps your project metadata and optionally refreshes the changelog. It then commits, tags & pushes the result, while giving you the chance to review every step.

---

## key capabilities
- **version automation**: drive `uv version` to bump or set the next release number, keeping `pyproject.toml` and `uv.lock` in sync.
- **preflight checks**: guard your release workflow by verifying branch, tags, and a clean working tree before shipping.
- **changelog generation**: auto-builds changelog sections from commits since the latest tag.
- **one-shot release**: stage, commit, tag, and push in a single step.
- **dry-run mode**: preview every action before making changes.

---
## installation
install it as a standalone CLI tool into a dedicated environment:

```console
uv tool install uv-ship
```

or add `uv-ship` as a dependency to a uv mangaged project:

```console
uv add uv-ship
```

---
## quick start

after installation, set up basic [configurations](config) by placing a `[tool.uv-ship]` table in your `pyrproject.toml`.

1. Ensure your working tree is clean and that you are on the configured release branch.
2. Run `uv-ship next patch` (or `minor` / `major`).
3. Review the changelog preview, confirm the prompts, and watch the tag and push finish.

Prefer to set an explicit version? Use `uv-ship version 1.2.0` instead of bumping.

Need to inspect the changelog first? Run `uv-ship log --latest` to preview commits since the last tag or `uv-ship log --save` to refresh the configured changelog file.

---
## CLI overview
- `uv-ship next <bump-type>` – bump `pyproject.toml` & `uv.lock`, update the changelog (optional), commit, tag, push.
- `uv-ship version <version>` – set a specific version without calculating the bump.
- `uv-ship log [--latest] [--save]` – show/update the changelog section built from commits after the latest tag.

Pass `--dry-run` on the root command to rehearse any of the subcommands without touching disk:

```console
uv-ship --dry-run next minor
```

---
## troubleshooting
- **Not inside a Git repository** – Run the CLI from within your project checkout.
- **Not on release branch** – Update your [tool.uv-ship] config or check out the correct branch before retrying.
- **Tag already exists** – uv-ship will not overwrite tags. Delete or rename the existing tag locally and remotely, then rerun.
- **Dirty working tree** – Inspect changes with git status --short. Either clean up, or if intentional, pass --dirty (per run) or set allow-dirty = true.
- **uv not found / fails** – Ensure the uv executable is installed, available in your PATH, and that your project has a valid pyproject.toml.

---
## requirements
- a project running Python 3.10+
- [uv 0.7.0](https://docs.astral.sh/uv/) or later on your `PATH`
- a Git repository

---

happy shipping!
