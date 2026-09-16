"""Validate the repository structure and manifest invariants."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "varta_modbus"

manifest = json.loads((INTEGRATION / "manifest.json").read_text())
assert manifest["domain"] == "varta_modbus"
assert manifest["config_flow"] is True
assert (INTEGRATION / "config_flow.py").is_file()
assert (INTEGRATION / "translations" / "en.json").is_file()
assert not (INTEGRATION / "strings.json").exists(), "custom integrations must not ship strings.json"
assert (INTEGRATION / "vendor" / "varta_modbus" / "device.py").is_file()
assert (INTEGRATION / "vendor" / "varta_modbus" / "model.py").is_file()

model = (INTEGRATION / "vendor" / "varta_modbus" / "model.py").read_text()
for register in ("integer(1074", "integer(1075"):
    assert register in model
assert model.count("writable=True") >= 2

print("VARTA Modbus repository structure: OK")
