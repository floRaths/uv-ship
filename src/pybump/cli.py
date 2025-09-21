import argparse

from .main import main


def pybump_cli():
    parser = argparse.ArgumentParser(description='Bump version, create git tag, and push changes.')
    parser.add_argument('bump', choices=['major', 'minor', 'patch'], help='Type of version bump.')
    args = parser.parse_args()

    bump = args.bump

    main(bump)
