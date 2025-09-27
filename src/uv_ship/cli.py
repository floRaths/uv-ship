import click
from click import Choice, Path

from . import cmd_log, cmd_next, cmd_tag


@click.group(invoke_without_command=True)
@click.option('--config', type=Path(exists=True), help='Path to config file (inferred if not provided).')
@click.option('--dry-run', is_flag=True, default=False, help='Show what would be done without making any changes.')
@click.pass_context
def cli(ctx, dry_run, config):
    """uv-ship: a CLI-tool for shipping with uv"""

    # store dry-run in context so subcommands can use it
    ctx.ensure_object(dict)
    ctx.obj['dry_run'] = dry_run
    ctx.obj['config'] = config

    # No subcommand given → show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()


@cli.command(name='next')
@click.argument('bump-type', type=Choice(['patch', 'minor', 'major'], case_sensitive=False))
@click.option('--dirty', is_flag=True, default=None, help='Allow dirty working directory.')
@click.pass_context
def cli_next(ctx, bump_type, dirty):
    """
    \033[34mbump and ship the next project version.\033[0m

    \b
    Possible values:
      \033[32mmajor, minor, patch\033[0m, stable, alpha, beta, rc, post, dev\033[0m
    """
    cmd_next.workflow(bump_type=bump_type, allow_dirty=dirty, config=ctx.obj['config'], dry_run=ctx.obj['dry_run'])


@cli.command(name='tag')
@click.argument('version', type=str)
@click.option('--dirty', is_flag=True, default=None, help='Allow dirty working directory.')
@click.pass_context
def cli_tag(ctx, version, dirty):
    """
    \033[34mtag and ship a specific version.\033[0m
    """
    cmd_tag.workflow(version=version, allow_dirty=dirty, config=ctx.obj['config'], dry_run=ctx.obj['dry_run'])


@cli.command(name='log')
@click.option('--latest', is_flag=True, help='Show all commits since the last tag.')
@click.option('--save', is_flag=True, default=None, help='Save changes to the changelog.')
@click.pass_context
def log(ctx, latest, save):
    """
    \033[34mbuild/show the changelog.\033[0m
    """
    cmd_log.workflow(latest=latest, save=save, config=ctx.obj['config'], dry_run=ctx.obj['dry_run'])


if __name__ == '__main__':
    cli(prog_name='uv-ship')
