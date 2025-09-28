## Configuration
The CLI reads settings from a `[tool.uv-ship]` table. You can place it in either `uv-ship.toml` or `pyproject.toml` (project root). Use the `--config` option to point to a custom file.

| Key              | Type    | Default     | Description |
|------------------|---------|-------------|-------------|
| `release-branch` | string/false | `"main"` | Branch that must be checked out before shipping. Set to `false` to disable the check. |
| `tag-prefix`     | string  | `"v"`      | Prefix added to the Git tag (e.g. `v1.2.3`). |
| `allow-dirty`    | bool    | `false`     | Allow staged/unstaged changes to proceed. You can override per-run with `--dirty`. |
| `changelog-path` | string  | `"CHANGELOG"` | Relative path to the changelog file that `uv-ship log --save` refreshes. |
| `dry-run`        | bool    | `false`     | Default dry-run mode (overridden by the CLI flag). |
| `preflight-prompt` | bool  | `true`      | Display the final confirmation prompt before running Git commands. |
| `reminders`      | list[str] | `["CHANGELOG.md updated?", "documentation updated?"]` | Optional checklist surfaced during release prompts. |

> If both `uv-ship.toml` and `pyproject.toml` contain a `[tool.uv-ship]` table, `uv-ship` aborts to avoid ambiguous settings.

### Example configuration
```toml
# pyproject.toml
[tool.uv-ship]
release-branch = "dev"
tag-prefix = "rel/"
reminders = ["CHANGELOG.md updated?", "Docs refreshed?"]
allow-dirty = false
```



## Configuration
`uv-ship` reads its settings from a `[tool.uv-ship]` table. It looks in this order:

1. A file passed with `--config`
2. `uv-ship.toml` (project root)
3. `pyproject.toml`
4. Built-in defaults (`src/uv_ship/config/default_config.toml`)

> Do not define `[tool.uv-ship]` in both `uv-ship.toml` and `pyproject.toml`. The CLI aborts to avoid ambiguity.

```toml
[tool.uv-ship]
release-branch = "main"      # Set to false to skip the branch check
allow-dirty = false           # Permit staged/unstaged changes
changelog-path = "CHANGELOG"  # Relative to the repo root
preflight-prompt = true       # Show the final "do you want to proceed?" question
tag-prefix = "v"             # Prepended to the Git tag name
dry-run = false               # Default behaviour (overridden by CLI flag)
reminders = ["CHANGELOG.md updated?", "documentation updated?"]
```
