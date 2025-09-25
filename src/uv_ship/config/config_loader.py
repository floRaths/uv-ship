import importlib.resources as resources
import os
from pathlib import Path

import tomli as tomllib

from .. import messages as msg
from ..resources import sym


def _get_settings_from_toml(file: Path):
    if not file.exists():
        return None
    with open(file, 'rb') as f:
        data = tomllib.load(f)
    return data.get('tool', {}).get('uv-ship')


def load_config(path: str | None = None, cwd: str = os.getcwd(), cmd_args: dict = {}):
    """
    Load uv-ship configuration with the following precedence:
    1. Explicit path (if provided)
    2. uv-ship.toml (in cwd)
    3. pyproject.toml (in cwd, must contain [tool.uv-ship])

    Rules:
    - If both uv-ship.toml and pyproject.toml contain [tool.uv-ship], raise an error.
    - If no [tool.uv-ship] is found, prompt for a config path.
    """

    if not isinstance(cwd, Path):
        cwd = Path(cwd)

    def_path = resources.files('uv_ship.config')
    for cont in def_path.iterdir():
        if cont.name == 'default_config.toml':
            default_settings = _get_settings_from_toml(cont)

    # 1. If user provides a custom path → always use that
    if path:
        config_file = Path(path)
        if not config_file.exists():
            print(f'{sym.negative} Config file "{config_file}" not found.')
            return None
        settings = _get_settings_from_toml(config_file)
        if not settings:
            print('failed to load config!')
            msg.failure(f'no [tool.uv-ship] table found in "{config_file}".')
            return None

        source = config_file

    else:
        # 2. No custom path → check default files in cwd
        uv_bump_file = cwd / 'uv-ship.toml'
        pyproject_file = cwd / 'pyproject.toml'

        if not uv_bump_file.exists() and not pyproject_file.exists():
            print(f'{sym.negative} Could not find "uv-ship.toml" or "pyproject.toml". Please provide a config path.')
            return None

        uv_bump_settings = _get_settings_from_toml(uv_bump_file)
        pyproject_settings = _get_settings_from_toml(pyproject_file)

        if uv_bump_settings and pyproject_settings:
            print(
                f'{sym.negative} Conflict: Both "uv-ship.toml" and "pyproject.toml" contain a [tool.uv-ship] table. '
                'Please remove one or specify a config path explicitly.'
            )
            return None

        if uv_bump_settings:
            settings = uv_bump_settings
            source = uv_bump_file.name

        if pyproject_settings:
            settings = pyproject_settings
            source = pyproject_file.name

        if not (uv_bump_settings or pyproject_settings):
            source = 'default'
            settings = {}
            # print(
            #     f'{sym.item} no [tool.uv-ship] config provided in "uv-ship.toml" or "pyproject.toml".\nusing default settings.'
            # )
            # return None

    print(f'config source: "{source}"')
    default_settings.update(settings)

    default_settings = {k.replace('-', '_'): v for k, v in default_settings.items()}

    config = default_settings if default_settings else exit(1)

    # args = {k.replace('-', '_'): v for k, v in config.items()}
    config.update(cmd_args)

    config['repo_root'] = str(cwd)

    return config
