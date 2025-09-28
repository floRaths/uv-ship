from . import changelogger as cl
from . import commands as cmd
from . import messages as msg
from . import preflight as prf
from .resources import ac, sym


def cmd_next(config: dict, bump_type: str, allow_dirty: bool = None, **kwargs):
    # dry run to collect all info first
    package_name, current_version, new_version = cmd.collect_info(bump=bump_type)

    config['allow_dirty'] = allow_dirty if allow_dirty is not None else config['allow_dirty']

    # show summary
    print(f'bumping to the next {ac.ITALIC}{bump_type}{ac.RESET} version:')
    print('')
    print(f'{package_name} {ac.BOLD}{ac.RED}{current_version}{ac.RESET} → {ac.BOLD}{ac.GREEN}{new_version}{ac.RESET}\n')

    # Construct tag and message
    TAG, MESSAGE = cmd.tag_and_message(config['tag_prefix'], current_version=current_version, new_version=new_version)

    # run preflight checks
    prf.run_preflight(config, TAG)

    confirm = input(f'{ac.BLUE}auto update changelog?{ac.RESET} [y/N]: ').strip().lower()
    if confirm in ('y', 'yes'):
        save = not config['dry_run']
        cl.update_changelog(config=config, tag=TAG, save=save, show_result=1)
        print('')
        msg.imsg('please consider making manual edits NOW!', icon=sym.item, color=ac.YELLOW)
    else:
        msg.imsg('changelog update skipped by user.', icon=sym.item)

    # show preflight summary
    msg.preflight_complete()

    # Interactive confirmation
    msg.user_confirmation()

    # # TODO test safeguards
    cmd.update_files(config, package_name)

    cmd.commit_files(config, MESSAGE)

    cmd.create_git_tag(config, TAG, MESSAGE)

    cmd.push_changes(config, TAG)

    msg.success(f'done! new version {new_version} registered and tagged.\n')


def cmd_version(config: dict, version: str, allow_dirty: bool = False, **kwargs):
    # dry run to collect all info first
    package_name, current_version = cmd.collect_info(version=version)

    config['allow_dirty'] = allow_dirty if allow_dirty is not None else config['allow_dirty']

    # show summary
    # print_command_summary(config, package_name, current_version, version)
    msg.imsg(f'setting project {package_name} to version {version}:', color=ac.BLUE)
    print(f'{package_name} {ac.BOLD}{ac.RED}{current_version}{ac.RESET} → {ac.BOLD}{ac.GREEN}{version}{ac.RESET}\n')

    # Construct tag and message
    TAG, MESSAGE = cmd.tag_and_message(config['tag_prefix'], new_version=version, current_version=current_version)

    # run preflight checks
    prf.run_preflight(config, TAG)

    # show preflight summary
    msg.preflight_complete()

    # Interactive confirmation
    msg.user_confirmation()

    # # TODO test safeguards
    cmd.update_files(config, package_name)

    cmd.commit_files(config, MESSAGE)

    cmd.create_git_tag(config, TAG, MESSAGE)

    cmd.push_changes(config, TAG)

    msg.success(f'done! new version {version} registered and tagged.\n')


def cmd_log(config: dict, latest: bool = False, save: bool = False, **kwargs):
    res, _ = cmd.run_command(['git', 'describe', '--tags', '--abbrev=0'])
    prev_tag = res.stdout.strip()

    new_tag = 'latest'

    if latest and not save:
        print('')
        msg.imsg(f'commits since last tag {prev_tag}:\n', color=msg.ac.BOLD)

        new_section = cl.prepare_new_section(new_tag, level=2, add_date=True)
        print(new_section)

        msg.imsg('run: `uv-ship log --save` to add this to CHANGELOG\n', color=msg.ac.BLUE)

    else:
        save = save if not config['dry_run'] else False
        cl.update_changelog(config=config, tag=new_tag, save=save, show_result=3)
