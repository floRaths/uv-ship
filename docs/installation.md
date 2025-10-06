<br>

# Installation

## Requirements

uv-ship is a CLI tool that aims to add repository interfacing functionality to uv. The minimum requirements are therefore:

- [uv 0.7.0](https://docs.astral.sh/uv/) or later on your `PATH`
- a python project that is managed with uv
- a Git repository

---
## Standalone CLI installation

It is recommended to install uv-ship as a standalone [uv tool](https://docs.astral.sh/uv/guides/tools/), where it can run in a dedicated environment:

```console
$ uv tool install uv-ship
```

You can update to the latest version via:
```console
$ uv tool update uv-ship
```


## Usage as a project dependency

Alternatively you can add uv-ship as a dependency to your project as long at it runs python 3.10+. 

```console
$ uv add uv-ship
```

---
