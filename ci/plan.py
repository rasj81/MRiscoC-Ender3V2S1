#!/usr/bin/env python3
"""Turn workflow_dispatch inputs into a build matrix (JSON on GITHUB_OUTPUT)."""
import json
import os
import sys
from pathlib import Path

PRESET_DIR = Path("presets")
FEATURES = {
    "corexy": "CoreXY", "cvlm": "CVLM", "freeflash": "FreeFlash",
    "homeoffs": "HomeOffs", "is": "IS", "la": "LA",
    "locksteppers": "LockSteppers", "mpc": "MPC", "np": "NP",
    "repeat_depth": "Repeat&Depth", "sdreadonly": "SDReadOnly",
    "speaker": "Speaker",
}


def load_preset(name):
    data = json.loads((PRESET_DIR / f"{name}.json").read_text())
    return {"name": data["machine_name"], "env": data["env"], "features": data["features"]}


def custom(inputs):
    modes = [inputs["printer"], inputs["board"], inputs["display"], inputs["leveling"]]
    if inputs.get("ubl") == "true" and inputs["leveling"] != "UBL":
        modes.append("UBL")
    if inputs["thermistor"] != "stock":
        modes.append(inputs["thermistor"])
    modes += [code for key, code in FEATURES.items() if inputs.get(key) == "true"]
    name = inputs.get("machine_name") or "Custom"
    return {"name": name.replace(" ", "-"), "env": inputs["env"], "features": modes}


def main():
    raw = json.loads(os.environ.get("INPUTS_JSON") or "{}") or {}
    inputs = {k: (str(v).lower() if isinstance(v, bool) else str(v)) for k, v in raw.items()}
    # Scheduled runs have no inputs: build every preset from upstream.
    preset = inputs.get("preset", "ALL")
    if preset == "ALL":
        include = [load_preset(p.stem) for p in sorted(PRESET_DIR.glob("*.json"))]
    elif preset == "custom":
        include = [custom(inputs)]
    else:
        include = [load_preset(preset)]
    source = "this-fork" if inputs.get("firmware_source") == "this-fork" else "upstream-latest"
    repo = os.environ.get("GITHUB_REPOSITORY", "rasj81/MRiscoC-Ender3V2S1")
    for item in include:
        item["source_repo"] = repo if source == "this-fork" else "mriscoc/Ender3V2S1"
    matrix = json.dumps({"include": include})
    print(matrix)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"matrix={matrix}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
