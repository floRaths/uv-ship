<!-- --8<-- "README.md" -->
<br>

# uv-ship
<div style="margin-top:-3rem; display:block;">
  <span class="acc-2-text">a CLI-tool for shipping with uv</span>
</div>

<br>

`uv-ship` is a lightweight companion to [uv](https://docs.astral.sh/uv/) that removes the risky parts of cutting a release. It verifies the repo state, bumps your project metadata and optionally refreshes the changelog. It then commits, tags & pushes the result, while giving you the chance to review every step.

---

## Key Capabilities
- **version automation**: drive `uv version` to bump or set the next release number, keeping `pyproject.toml` and `uv.lock` in sync.
- **preflight checks**: guard your release workflow by verifying branch, tags, and a clean working tree before shipping.
- **changelog generation**: auto-builds changelog sections from commits since the latest tag.
- **one-shot release**: stage, commit, tag, and push in a single step.
- **dry-run mode**: preview every action before making changes.


---
## Quick Start

1. [Install](installation.md) as a standalone CLI tool (recommended):
``` console
$ uv tool install uv-ship
```

2. Set up basic [configurations](config.md) by placing a `[tool.uv-ship]` table in your `pyproject.toml`.

3. Run `uv-ship --dry-run next minor`

4. Review the changelog preview, confirm the prompts, and watch the tag and push finish.

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
## Troubleshooting
- **Not inside a Git repository** – Run the CLI from within your project checkout.
- **Not on release branch** – Update your [tool.uv-ship] config or check out the correct branch before retrying.
- **Tag already exists** – uv-ship will not overwrite tags. Delete or rename the existing tag locally and remotely, then rerun.
- **Dirty working tree** – Inspect changes with git status --short. Either clean up, or if intentional, pass --dirty (per run) or set allow-dirty = true.
- **uv not found / fails** – Ensure the uv executable is installed, available in your PATH, and that your project has a valid pyproject.toml.



---
## License
This project is licensed under the MIT license.

---

happy shipping!
