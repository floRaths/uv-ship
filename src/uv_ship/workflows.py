from . import changelogger as cl
from . import commands as cmd
from . import messages as msg
from . import preflight as prf
from .resources import ac, sym


def ship(config: dict, version: str, allow_dirty: bool = None, **kwargs):
    # dry run to collect all info first
    package_name, old_version, new_version = cmd.collect_info(version=version)

    print(f'{package_name} {ac.BOLD}{ac.RED}{old_version}{ac.RESET} → {ac.BOLD}{ac.GREEN}{new_version}{ac.RESET}\n')

    # Construct tag and message
    TAG, MESSAGE = cmd.tag_and_message(config['tag_prefix'], current_version=old_version, new_version=new_version)

    config['allow_dirty'] = allow_dirty if allow_dirty is not None else config['allow_dirty']

    # run preflight checks
    prf.run_preflight(config, TAG)

    confirm = input(f'{ac.BLUE}auto update changelog?{ac.RESET} [y/N]: ').strip().lower()
    if confirm in ('y', 'yes'):
        save = not config['dry_run']
        cmd_log(config=config, new_tag=TAG, save=save, show_result=1)
        print('')
        msg.imsg('please consider making manual edits NOW!', icon=sym.item, color=ac.YELLOW)
    else:
        msg.imsg('changelog update skipped by user.', icon=sym.item)

    # show preflight summary
    msg.preflight_complete()

    # Interactive confirmation
    msg.user_confirmation()

    # # TODO test safeguards
    cmd.update_files(config, package_name, new_version)

    cmd.commit_files(config, MESSAGE)

    cmd.create_git_tag(config, TAG, MESSAGE)

    cmd.push_changes(config, TAG)

    msg.success(f'done! new version {new_version} registered and tagged.\n')


def cmd_log(config: dict, new_tag: str, latest: bool = False, save: bool = False, **kwargs):
    clog_content, clog_path = cl.read_changelog(config=config)
    strategy, latest_repo_tag, latest_clog_tag = cl.eval_clog_update_strategy(clog_content, new_tag, print_eval=False)
    # print(f'changelog update strategy: {strategy}')

    if latest:
        print('')
        msg.imsg(f'commits since last tag in repo: {latest_repo_tag}:\n', color=msg.ac.BOLD)
        new_section = cl.prepare_new_section(new_tag, add_date=True)
        print(new_section.strip())

        print('')
        msg.imsg(f'run: `uv-ship log --save` to add this to {config["changelog_path"]}\n', color=msg.ac.BLUE)

    else:
        save = save if not config['dry_run'] else False
        cl.execute_update_strategy(config, clog_path, clog_content, new_tag, strategy, save)
