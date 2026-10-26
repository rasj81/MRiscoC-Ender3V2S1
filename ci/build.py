#!/usr/bin/env python3
"""Generate Marlin config files with the Special_Configurations generator,
install them into this checkout, and verify the result before compiling."""
import argparse
import re
import shutil
import sys
from pathlib import Path

# Option code -> a #define that must be active in the generated config.
EXPECT = {
    "BLT": ("BLTOUCH", None),
    "UBL": ("AUTO_BED_LEVELING_UBL", None),
    "LA": ("LIN_ADVANCE", None),
    "IS": ("INPUT_SHAPING_X", None),
    "MPC": ("MPCTEMP", None),
    "T13": ("TEMP_SENSOR_0", "13"),
    "T1": ("TEMP_SENSOR_0", "1"),
    "T5": ("TEMP_SENSOR_0", "5"),
    "T20": ("TEMP_SENSOR_0", "20"),
}


def active_define(text, name, value=None):
    pattern = rf"(?m)^[ \t]*#define[ \t]+{name}\b[ \t]*([^\s/]*)"
    m = re.search(pattern, text)
    if not m:
        return False
    return value is None or m.group(1) == value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True, help="path to Special_Configurations checkout")
    ap.add_argument("--target", default=".", help="firmware checkout to install the configs into")
    ap.add_argument("--name", required=True)
    ap.add_argument("--features", required=True, help="comma-separated option codes")
    args = ap.parse_args()

    features = [f for f in args.features.split(",") if f]
    gen = Path(args.gen).resolve()
    target = Path(args.target).resolve()
    sys.path.insert(0, str(gen))
    import os
    os.chdir(gen)
    import CreateConfigs

    if CreateConfigs.Generate(args.name, features):
        print((gen / args.name / "log.txt").read_text())
        sys.exit("generator reported an error")

    out = gen / args.name
    cfg = (out / "Configuration.h").read_text() + (out / "Configuration_adv.h").read_text()
    missing = []
    for code in features:
        if code in EXPECT:
            define, value = EXPECT[code]
            if not active_define(cfg, define, value):
                missing.append(f"{code}: {define} {value or ''} not active")
    if missing:
        sys.exit("sanity check failed:\n  " + "\n  ".join(missing))

    repo = target
    for fname in ("Configuration.h", "Configuration_adv.h", "Version.h"):
        shutil.copy(out / fname, repo / "Marlin" / fname)
    shutil.copy(out / "platformio.ini", repo / "platformio.ini")
    m = re.search(r"(?m)^[ \t]*#define[ \t]+TEMP_SENSOR_0[ \t]+(\S+)", cfg)
    print(f"OK {args.name}: options={features} TEMP_SENSOR_0={m.group(1) if m else '?'}")


if __name__ == "__main__":
    main()
