import importlib.resources as resources
import json

# register fonts supplied with package
path = resources.files('pybump.resources')
for cont in path.iterdir():
    if cont.name == 'symbols.json':
        with open(cont, 'r') as f:
            symbols = json.load(f)


class Symbols:
    def __init__(self, symbols):
        self.symbols = symbols
        for key, value in symbols.items():
            setattr(self, key, value)


sym = Symbols(symbols)
