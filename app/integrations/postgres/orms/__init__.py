import importlib
from pathlib import Path


current_dir = Path(__file__).parent

for file in current_dir.rglob('*.py'):
    if file.name != '__init__.py':
        module_name = file.relative_to(current_dir).with_suffix('').as_posix().replace('/', '.')
        importlib.import_module(f'.{module_name}', package=__name__)

