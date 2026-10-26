#!/usr/bin/env python3
"""Turn workflow_dispatch inputs into a build matrix (JSON on GITHUB_OUTPUT).

Firmware names follow the Special_Configurations Configurator "Auto" rule:
printer-board-leveling[-UBL joined]-[display if not DWIN]-[thermistor if not T1]-features,
and each .bin gets the firmware branch and a UTC date stamp (added by the
workflow): <name>-<branch>-<YYYYMMDD>.bin
"""
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PRESET_DIR = Path("presets")
PRINTERS = {"Ender3V2", "Ender3V2Neo", "Ender3", "Ender3S1", "Ender3MaxNeo", "Ender2Pro", "Ender5Pro", "Aquila"}
BOARDS = {"301F1", "301F4", "422", "423", "427", "CR4NTF4", "G32", "SKRME3V2", "SKRME3V3"}
LEVELING = {"BLT", "AutoLev", "BQMPv2", "EZABLZI", "EZABLZN", "MM", "UBL"}
DISPLAYS = {"DWIN", "CR10DSPLY", "DACAI", "SYNWIT", "TJC"}
THERMISTORS = {"T1", "T5", "T13", "T20"}
FEATURES = {
    "corexy": "CoreXY", "cvlm": "CVLM", "freeflash": "FreeFlash",
    "homeoffs": "HomeOffs", "is": "IS", "la": "LA",
    "locksteppers": "LockSteppers", "mpc": "MPC", "np": "NP",
    "repeat_depth": "Repeat&Depth", "sdreadonly": "SDReadOnly",
    "speaker": "Speaker",
}


def canonical(codes):
    """Order and filter option codes exactly like the Configurator's fill_conf()."""
    codes = set(codes)

    def one(group, label):
        found = sorted(codes & group)
        if len(found) != 1:
            sys.exit(f"need exactly one {label}, got {found or 'none'}")
        return found[0]

    printer, board = one(PRINTERS, "printer"), one(BOARDS, "board")
    leveling = one(LEVELING - {"UBL"} if codes & (LEVELING - {"UBL"}) else {"UBL"}, "leveling")
    display = one(DISPLAYS, "display")
    thermistor = sorted(codes & THERMISTORS)
    out = [printer, board, leveling]
    if "UBL" in codes and leveling != "UBL":
        out.append("UBL")
    if display != "DWIN":
        out.append(display)
    if thermistor and thermistor[0] != "T1":
        out.append(thermistor[0])
    out += sorted(codes & set(FEATURES.values()), key=str.lower)
    return out


def auto_name(modes):
    """Configurator auto_name(): join, then apply its S1 and UBL filters."""
    name = "-".join(modes)
    name = name.replace("-301F", "-F").replace("F1-BLT", "F1").replace("F4-BLT", "F4")
    if "F1-UBL" not in name and "F4-UBL" not in name:
        name = name.replace("-UBL", "UBL")
    return name


def build_item(codes, env, label, source):
    modes = canonical(codes)
    return {"name": auto_name(modes), "label": label, "env": env, "features": modes, **source}


def from_preset(name, source):
    data = json.loads((PRESET_DIR / f"{name}.json").read_text())
    return build_item(data["features"], data["env"], data["label"], source)


def from_form(inputs, source):
    codes = [inputs["printer"], inputs["board"], inputs["display"], inputs["leveling"]]
    if inputs.get("ubl") == "true":
        codes.append("UBL")
    if inputs["thermistor"] != "stock":
        codes.append(inputs["thermistor"])
    codes += [code for key, code in FEATURES.items() if inputs.get(key) == "true"]
    return build_item(codes, inputs["env"], "custom", source)


def resolve_ref(repo, ref):
    """'stable' = the newest New-Year-#### branch of the source repo."""
    if ref.lower() != "stable":
        return ref
    out = subprocess.run(
        ["git", "ls-remote", "--heads", f"https://github.com/{repo}.git", "New-Year-*"],
        capture_output=True, text=True, check=True).stdout
    years = [int(m.group(1)) for m in re.finditer(r"refs/heads/New-Year-(\d+)$", out, re.M)]
    if not years:
        sys.exit(f"no New-Year-#### branch found in {repo}")
    return f"New-Year-{max(years)}"


def main():
    raw = json.loads(os.environ.get("INPUTS_JSON") or "{}") or {}
    inputs = {k: (str(v).lower() if isinstance(v, bool) else str(v)) for k, v in raw.items()}
    # Scheduled/no-input runs build every preset from upstream.
    preset = inputs.get("preset", "ALL")
    repo = os.environ.get("GITHUB_REPOSITORY", "rasj81/MRiscoC-Ender3V2S1")
    use_fork = inputs.get("firmware_source") == "this-fork"
    source = {
        "source_repo": repo if use_fork else "mriscoc/Ender3V2S1",
        "firmware_ref": "",
        "date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d"),
    }
    source["firmware_ref"] = resolve_ref(source["source_repo"], inputs.get("firmware_ref", "").strip())
    if preset == "ALL":
        include = [from_preset(p.stem, source) for p in sorted(PRESET_DIR.glob("*.json"))]
    elif preset == "custom":
        include = [from_form(inputs, source)]
    else:
        include = [from_preset(preset, source)]
    matrix = json.dumps({"include": include})
    print(matrix)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"matrix={matrix}\n")


if __name__ == "__main__":
    main()
