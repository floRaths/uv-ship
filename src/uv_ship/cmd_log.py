from . import changelogger as cl
from . import commands as cmd
from . import config as cfg
from . import messages as msg


def workflow(**kwargs):
    config = cfg.load_config(path=kwargs['config'])

    if kwargs['dry_run']:
        msg.imsg('\n>> THIS IS A DRY RUN - NO CHANGES WILL BE MADE <<', color=msg.ac.DIM)

    res, _ = cmd.run_command(['git', 'describe', '--tags', '--abbrev=0'])
    prev_tag = res.stdout.strip()

    new_tag = 'latest'

    if kwargs['latest'] and not kwargs['save']:
        print('')
        msg.imsg(f'commits since last tag {prev_tag}:\n', color=msg.ac.BOLD)

        new_section = cl.prepare_new_section(new_tag, level=2, add_date=True)
        print(new_section)

        msg.imsg('run: `uv-ship log --save` to add this to CHANGELOG\n', color=msg.ac.BLUE)

    else:
        save = kwargs['save'] if not kwargs['dry_run'] else False
        cl.update_changelog(config=config, tag=new_tag, save=save, show_result=3)
