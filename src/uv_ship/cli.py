import click
from click import Choice, Path

from . import cmd_next, cmd_tag


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """uv-ship: a CLI-tool for shipping with uv."""

    # No subcommand given → show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()  # ← ensures it stops cleanly after showing help


@cli.command(name='next')
@click.argument('bump-type', type=Choice(['patch', 'minor', 'major', '(dev,...)'], case_sensitive=False))
@click.option('--config', type=Path(exists=True), help='Path to config file (inferred if not provided).')
@click.option('--dry-run', is_flag=True, help='Show what would be done without making any changes.')
@click.option('--dirty', is_flag=True, help='Allow dirty working directory.')
def cli_next(bump_type, config, dry_run, dirty):
    """
    \033[32m\033[1mnext:\033[0m bump and ship the next project version.

    \b
    Possible values:
      \033[34mmajor, minor, patch\033[0m, stable, alpha, beta, rc, post, dev\033[0m
    """
    cmd_next.next_workflow(bump_type=bump_type, config=config, dry_run=dry_run, allow_dirty=dirty)


@cli.command(name='tag')
@click.argument('version', type=str)
@click.option('--config', type=Path(exists=True), help='Path to config file.')
@click.option('--dry-run', is_flag=True, help='Show what would be done without making any changes.')
@click.option('--dirty', is_flag=True, help='Allow dirty working directory.')
def cli_tag(version, config, dry_run, dirty):
    """tag and ship a specific version."""
    cmd_tag.tag_workflow(version=version, config=config, dry_run=dry_run, dirty=dirty)


@cli.command()
def log():
    """build/show the changelog."""
    click.echo('Showing changelog...')


if __name__ == '__main__':
    cli(prog_name='uv-ship')
