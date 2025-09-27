import click
from click import Choice, Path

from . import cmd_log, cmd_next, cmd_tag

dry_run_notice = 'Show what would be done without making any changes.'


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """uv-ship: a CLI-tool for shipping with uv."""

    # No subcommand given → show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()  # ← ensures it stops cleanly after showing help


@cli.command(name='next')
@click.argument('bump-type', type=Choice(['patch', 'minor', 'major'], case_sensitive=False))
@click.option('--config', type=Path(exists=True), help='Path to config file (inferred if not provided).')
@click.option('--dry-run', is_flag=True, help=dry_run_notice)
@click.option('--dirty', is_flag=True, help='Allow dirty working directory.')
def cli_next(bump_type, config, dry_run, dirty):
    """
    \033[34mbump and ship the next project version.\033[0m

    \b
    Possible values:
      \033[32mmajor, minor, patch\033[0m, stable, alpha, beta, rc, post, dev\033[0m
    """
    cmd_next.workflow(bump_type=bump_type, config=config, dry_run=dry_run, allow_dirty=dirty)


@cli.command(name='tag')
@click.argument('version', type=str)
@click.option('--config', type=Path(exists=True), help='Path to config file.')
@click.option('--dry-run', is_flag=True, default=False, help=dry_run_notice)
@click.option('--dirty', is_flag=True, default=False, help='Allow dirty working directory.')
def cli_tag(version, config, dry_run, dirty):
    """
    \033[34mtag and ship a specific version.\033[0m
    """
    cmd_tag.workflow(version=version, config=config, dry_run=dry_run, dirty=dirty)


@cli.command(name='log')
@click.option('--latest', is_flag=True, help='Show all commits since the last tag.')
@click.option('--save', is_flag=True, default=False, help='Save changes to the changelog.')
@click.option('--dry-run', is_flag=True, default=False, help=dry_run_notice)
def log(latest, save, dry_run):
    """
    \033[34mbuild/show the changelog.\033[0m
    """
    cmd_log.workflow(latest=latest, save=save, dry_run=dry_run)


if __name__ == '__main__':
    cli(prog_name='uv-ship')
