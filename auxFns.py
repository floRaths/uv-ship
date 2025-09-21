import subprocess


def get_proj_version():
    result = subprocess.run(['uv', 'version', '--short'], capture_output=True, text=True)
    return result.stdout

def bump_proj_version(which):
    subprocess.run(['uv', 'version', "--bump", which])