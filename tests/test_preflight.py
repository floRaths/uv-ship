import uv_ship
from uv_ship import messages as msg
from uv_ship.preflight import run_preflight

config = uv_ship.cfg.load_config(path='tests/test_config.toml')

try:
    run_preflight(config=config, TAG='_', skip_input=True)
    print('')
    msg.success('all preflight tests passed!')

except Exception as e:
    raise RuntimeError(f'>> preflight tests failed: {e}')
