# configuration

uv-ship reads user defined settings from a `[tool.uv-ship]` table in a toml file. By default, it will look for such a table in either `uv-ship.toml` or `pyproject.toml` in your project root. Optionally, you can use the `--config` flag to point to a custom file. If no config is provided, uv-ship will fall back to its default settings.

??? quote "the config source is reported every time you invoke `uv-ship`"

    ``` console
    $ uv-ship

    uv-ship - a CLI-tool for shipping with uv
    config source: "pyproject.toml"
    ```

## example configuration
```toml
# pyproject.toml
[tool.uv-ship]
release-branch = "main"
tag-prefix = "v"
allow-dirty = false
changelog-path = "CHANGELOG"
```

!!! note
    If both `uv-ship.toml` and `pyproject.toml` contain a `[tool.uv-ship]` table, the CLI aborts to avoid ambiguous settings.


## available settings
| Key              | Type    | Default     | Description |
|------------------|---------|-------------|-------------|
| `release-branch` | string/false | `"main"` | Branch that must be checked out before shipping. Set to `false` to disable the check. |
| `tag-prefix`     | string  | `"v"`      | Prefix added to the Git tag (e.g. `v1.2.3`). |
| `allow-dirty`    | bool    | `false`     | Allow staged/unstaged changes to proceed. You can override per-run with `--dirty`. |
| `changelog-path` | string  | `"CHANGELOG"` | Relative path to the changelog file that the changelog feature reads and refreshes. |
| `dry-run`        | bool    | `false`     | Default dry-run mode (overridden by the CLI flag). |
