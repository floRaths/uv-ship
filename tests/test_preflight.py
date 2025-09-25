import uv_ship
from uv_ship.preflight import run_preflight

config = uv_ship.cfg.load_config()
run_preflight(config=config, TAG='_', skip_input=True)
