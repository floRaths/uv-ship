import os

# import tomli as tomllib
import tomllib
from pathlib import Path


def load_config(path: str | None = None, cwd: str = os.getcwd()):
    """
    Load uv-bump configuration with the following precedence:
    1. Explicit path (if provided)
    2. uv-bump.toml (in cwd)
    3. pyproject.toml (in cwd, must contain [tool.uv-bump])

    Rules:
    - If both uv-bump.toml and pyproject.toml contain [tool.uv-bump], raise an error.
    - If no [tool.uv-bump] is found, prompt for a config path.
    """

    def _get_settings_from_toml(file: Path):
        if not file.exists():
            return None
        with open(file, 'rb') as f:
            data = tomllib.load(f)
        return data.get('tool', {}).get('uv-bump')

    if not isinstance(cwd, Path):
        cwd = Path(cwd)

    # 1. If user provides a custom path → always use that
    if path:
        config_file = Path(path)
        if not config_file.exists():
            print(f'❌ Config file "{config_file}" not found.')
            return None
        settings = _get_settings_from_toml(config_file)
        if not settings:
            print(f'❌ No [tool.uv-bump] table found in "{config_file}".')
            return None
        print(f'Loaded config from "{config_file}".')
        return settings

    # 2. No custom path → check default files in cwd
    uv_bump_file = cwd / 'uv-bump.toml'
    pyproject_file = cwd / 'pyproject.toml'

    if not uv_bump_file.exists() and not pyproject_file.exists():
        print('❌ Could not find "uv-bump.toml" or "pyproject.toml". Please provide a config path.')
        return None

    uv_bump_settings = _get_settings_from_toml(uv_bump_file)
    pyproject_settings = _get_settings_from_toml(pyproject_file)

    if uv_bump_settings and pyproject_settings:
        print(
            '❌ Conflict: Both "uv-bump.toml" and "pyproject.toml" contain a [tool.uv-bump] table. '
            'Please remove one or specify a config path explicitly.'
        )
        return None

    if uv_bump_settings:
        print(f'Loaded config from "{uv_bump_file.name}".')
        return uv_bump_settings

    if pyproject_settings:
        print(f'Loaded config from "{pyproject_file.name}".')
        return pyproject_settings

    # 3. Neither file has [tool.uv-bump]
    print('❌ No [tool.uv-bump] table found in "uv-bump.toml" or "pyproject.toml".\n👉 Please provide a config path.')
    return None
