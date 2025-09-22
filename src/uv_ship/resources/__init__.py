import importlib.resources as resources
import json

# register fonts supplied with package
path = resources.files('uv_ship.resources')
for cont in path.iterdir():
    
    if cont.name == 'symbols.json':
        with open(cont, 'r') as f:
            symbols = json.load(f)
    
    if cont.name == 'ansi.json':
        with open(cont, 'r') as f:
            ansi_codes = json.load(f)


class Symbols:
    def __init__(self, symbols):
        self.symbols = symbols
        for key, value in symbols.items():
            setattr(self, key, value)


class Ansi:
    def __init__(self, ansi_codes):
        self.ansi_codes = ansi_codes
        for key, value in ansi_codes.items():
            setattr(self, key, value)


sym = Symbols(symbols)
ac = Ansi(ansi_codes)
