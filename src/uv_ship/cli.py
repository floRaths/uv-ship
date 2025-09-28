import click
from click import Choice, Path

from . import commands as cmd
from . import config as cfg
from . import messages as msg
from . import workflows as wfl


# region cli
@click.group(invoke_without_command=True)
@click.option('--config', type=Path(exists=True), help='Path to config file (inferred if not provided).')
@click.option('--dry-run', is_flag=True, default=False, help='Show what would be done without making any changes.')
@click.pass_context
def cli(ctx, dry_run, config):
    # Show tagline and set up config
    msg.welcome_message()

    repo_root = cmd.get_repo_root()
    uvs_config = cfg.load_config(path=config, cwd=repo_root, cmd_args={'dry_run': dry_run})
    print('')

    if uvs_config['dry_run']:
        msg.dry_run_warning()

    # store config in context so subcommands can use it
    ctx.ensure_object(dict)
    ctx.obj = uvs_config

    # No subcommand given → show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        print('')
        ctx.exit()


# region next
@cli.command(name='next')
@click.argument('bump-type', type=Choice(['major', 'minor', 'patch'], case_sensitive=False))
@click.option('--dirty', is_flag=True, default=None, help='Allow dirty working directory.')
@click.pass_context
def cli_next(ctx, bump_type, dirty):
    """
    \033[34mbump and ship the next project version.\033[0m

    \b
    Possible values:
      \033[32mmajor, minor, patch\033[0m
      \033[2mnot yet supported: stable, alpha, beta, rc, post, dev\033[0m
    """
    wfl.cmd_next(config=ctx.obj, bump_type=bump_type, allow_dirty=dirty)


# region version
@cli.command(name='version')
@click.argument('version', type=str)
@click.option('--dirty', is_flag=True, default=None, help='Allow dirty working directory.')
@click.pass_context
def cli_version(ctx, version, dirty):
    """
    \b
    \033[34mset, tag, and ship a specific version.\033[0m
    """
    wfl.cmd_version(config=ctx.obj, version=version, allow_dirty=dirty)


# region log
@cli.command(name='log')
@click.option('--latest', is_flag=True, help='Show all commits since the last tag.')
@click.option('--save', is_flag=True, default=None, help='Save changes to the changelog.')
@click.pass_context
def log(ctx, latest, save):
    """
    \033[34mbuild/show the changelog.\033[0m
    """
    wfl.cmd_log(config=ctx.obj, latest=latest, save=save)


if __name__ == '__main__':
    cli(prog_name='uv-ship')
