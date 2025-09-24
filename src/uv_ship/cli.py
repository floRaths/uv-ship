import click

from . import bump as cmd_bump


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """uv-ship: a CLI-tool for shipping with uv."""

    # No subcommand given → show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument('bump-type', type=click.Choice(['patch', 'minor', 'major'], case_sensitive=False))
@click.option('--config', type=click.Path(exists=True), help='Path to config file.')
@click.option('--dirty', is_flag=True, help='Allow dirty working directory.')
def bump(bump_type, config, dirty):
    """bump and ship the project version."""
    cmd_bump.bump(bump_type=bump_type, config=config, dirty=dirty)


@cli.command()
def log():
    """build/show the changelog."""
    click.echo('Showing changelog...')


@cli.command()
def this():
    """tag and ship the current state."""
    click.echo('Showing info about this project...')


if __name__ == '__main__':
    cli(prog_name='uv-ship')
