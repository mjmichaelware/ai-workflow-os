import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('generated_app', Path(__file__).resolve().parents[1] / 'app.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod.health_payload()['ok'] is True
print('PASS generated app smoke test')
