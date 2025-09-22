#
# uv-ship
<span style="margin-top:-3rem; display:block;">A light tag and release tool for uv managed python projects</span>
<br>

## what is does:  
uv-ship is a simple tool designed to streamline and error-proof version release tasks in uv managed projects.
It wraps `uv version --bump` commands with extended functionality to complete the release workflow.  
It is lightweight with **0 dependencies**!

#### preflight checks
- ensures that the correct branch is checked out
- ensures that there are no conflicts with version tags
- will warn you if your working tree is not clean
- can post reminders to make sure the version is actually ready  
i.e: "CHANGELOG.md updated?"

#### update tasks
- updates pyproject.toml and uv.lock by calling `uv version --bump <bump_type>`
- staged and commits those changes
- tags the commit with the new version
- pushes those changes to the remote repository

#### guardrails
The process with abort (and if necessary revert) if things fail along the way.  
Saving you time cleaning up


## config
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

