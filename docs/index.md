# uv-ship
<span style="margin-top:-3rem; display:block;">a release workflow streamliner for uv managed python projects</span>
<!-- <br> -->

---

## purpose
uv-ship is a simple tool designed to streamline and error-proof version release tasks in uv managed projects.
It wraps `uv version --bump` commands with extended functionality to complete the release workflow.

## uv-ship runs in three stages:

#### 1. preflight checks
- ensures that the correct branch is checked out and new tags don't conflict
- will warn/abort if your working tree is not clean
- can post reminders to make sure important release items are completed
*"CHANGELOG.md updated?"*

#### 2. update the files
- updates pyproject.toml and uv.lock by calling `uv version --bump <bump_type>`

#### 3. tag and commit the changes

- stages and commits the changed files
- tags the commit with the new version
- pushes those changes to the remote repository

---

## requirements
As the name suggests, uv-ship is designed to complement the 'uv' project manager.
You can learn how to install and use uv [here](https://docs.astral.sh/uv/).
It is lightweight with just **1** dependency!

## installation
uv-ship is available on [PyPI](https://pypi.org/project/uv-ship/). To add it to your project:
```console
$ uv add uv-ship
```
Or if you want to install uv-ship independent of your project:
```console
$ uv tool install uv-ship
```
---

## configuration
uv-ship reads its configuration from a `[tool.uv-ship]` table in a toml file. By default it will look for such a table in uv-ship.toml or pyproject.toml in the project root.
Alternatively an explicit config path can be supplied

``` toml
# pyproject.toml
[tool.uv-ship]
release_branch = "master"
tag_prefix = "v"
reminders = ['updated CHANGELOG.md?', 'updated documentation?']
allow_dirty = true
```
