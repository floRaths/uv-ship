import argparse

from .main import main


def uv_ship_cli():
    parser = argparse.ArgumentParser(description='Bump version, create git tag, and push changes.')
    parser.add_argument('bump', choices=['major', 'minor', 'patch'], help='Type of version bump.')
    parser.add_argument('--config', default=None, help='Path to the config file.')
    parser.add_argument('--allow-dirty', action='store_true', help='Allow dirty working directory.')

    args = parser.parse_args()

    main(bump=args.bump, config_path=args.config, allow_dirty=args.allow_dirty)
