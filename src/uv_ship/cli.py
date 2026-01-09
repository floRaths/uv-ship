import datetime

from . import commands as cmd
from . import config as cfg
from . import messages as msg
from . import workflows as wfl
from .resources import rich_click as click

click.rich_click.COMMAND_GROUPS = {
    'uv-ship': [
        {'name': 'commands', 'commands': ['next', 'calver', 'version', 'log', 'status']},
        # {"name": "utilities", "commands": ["log"]},
    ],
}


# region cli
@click.group(
    context_settings=dict(help_option_names=['-h', '--help']), invoke_without_command=True, add_help_option=True
)
# @click.group(invoke_without_command=True)
@click.option('--config', type=click.Path(exists=True), help='Path to config file (inferred if not provided).')
@click.option('--dry-run', is_flag=True, default=False, help='Review changes without touching disk.')
@click.option('--self', is_flag=True, default=False, help='Display uv-ship version.')
@click.pass_context
def cli(ctx, dry_run, config, self):
    if self:
        ver = cmd.ver.get_self_version(short=True)
        click.echo(f'uv-ship {ver[0]}')
    else:
        # Show tagline and set up config
        msg.welcome_message()

        repo_root = cmd.git.get_repo_root()
        uvs_config = cfg.load_config(path=config, cwd=repo_root, cmd_args={'dry_run': dry_run})

        uv_version, _ = cmd.run_command(['uv', 'self', 'version', '--short'], print_stderr=False)
        if not _:
            msg.failure('uv is not installed or not available on PATH.')
        else:
            msg.imsg(f'uv version {uv_version.stdout.split()[0]}', color=msg.ac.DIM)
        # print('')

        if uvs_config['dry_run']:
            msg.dry_run_warning()

        # store config in context so subcommands can use it
        ctx.ensure_object(dict)
        ctx.obj = uvs_config

        # No subcommand given → show help
        if ctx.invoked_subcommand is None:
            click.echo(ctx.get_help())
            # print('')
            ctx.exit()


# region next
@cli.command(name='next')
@click.argument('release-type', type=str, panel='commands')
@click.option('--pre-release', type=str, default=None, help='Pre-release component (e.g. alpha, beta).')
@click.option('--dirty', is_flag=True, default=None, help='Allow dirty working directory.')
@click.pass_context
def cli_next(ctx, release_type, pre_release, dirty):
    """
    bump and ship the next project version.

    \b
    release_types:                major, minor, patch, *stable
    pair with pre-release:        alpha, beta, rc, post, dev (optional)
    \b
    remove pre-release status:    set release_type to 'stable'
    """
    # show summary
    next_step = release_type if not pre_release else f'{release_type} ({pre_release})'
    msg.imsg(f'bumping to the next {next_step} version:', color=msg.ac.BLUE)
    version = cmd.gen.calculate_version(bump_type=release_type, pre_release=pre_release)
    wfl.ship(config=ctx.obj, version=version, allow_dirty=dirty)


# region calver
@cli.command(name='calver')
@click.option('--dirty', is_flag=True, default=None, help='Allow dirty working directory.')
@click.pass_context
def cli_calver(ctx, dirty):
    """
    bump and ship the project with todya's date as version number (calver).

    """
    # show summary
    current_date = datetime.date.today()
    version = current_date.strftime('%Y.%m.%d')
    msg.imsg(f'bumping to the next version {version}:', color=msg.ac.BLUE)
    wfl.ship(config=ctx.obj, version=version, allow_dirty=dirty)


# region version
@cli.command(name='version')
@click.argument('version', type=str, panel='commands')
@click.option('--dirty', is_flag=True, default=None, help='Allow dirty working directory.')
@click.pass_context
def cli_version(ctx, version, dirty):
    """
    set, tag, and ship a specific version.
    """
    msg.imsg('setting a new project version:', color=msg.ac.BLUE)
    wfl.ship(config=ctx.obj, version=version, allow_dirty=dirty)


# region log
@cli.command(name='log')
@click.option(
    '--tag',
    type=str,
    default=None,
    show_default=False,
    help='Tag to use in the changelog (default set in config).',
)
@click.option('--latest', is_flag=True, help='Show all commits since the last tag.')
@click.option('--save', is_flag=True, default=None, help='Save changes to the changelog.')
@click.pass_context
def log(ctx, tag, latest, save):
    """
    build/show the changelog.
    """
    default_tag = ctx.obj.get('unreleased_tag', '[unreleased]')
    new_tag = tag or default_tag

    wfl.cmd_log(config=ctx.obj, new_tag=new_tag, latest=latest, save=save, print_n_sections=3)


# region log
@cli.command(name='status')
@click.pass_context
def status(ctx):
    """
    show project status.
    """
    wfl.cmd_status(config=ctx.obj)


if __name__ == '__main__':
    cli(prog_name='uv-ship')
