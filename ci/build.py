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


def int_define(text, name):
    m = re.search(rf"(?m)^[ \t]*#define[ \t]+{name}[ \t]+(\d+)", text)
    return int(m.group(1)) if m else None


def patch_park_point(text, adv_text):
    """The generator parks the nozzle at {X_BED_SIZE+10, Y_MAX_POS-10, 20}. That is beyond the real travel of an
    Ender 3 V2 with a Sprite Pro (measured 220 x 220), and Marlin's park move is not clamped by the soft
    limits, so pause, M600 and the runout script would drive the carriage into the frame. Park inside the bed
    instead: 20 mm in from the bed size, at most 200, keeping the generator's Z raise."""
    xb, yb = int_define(text, "X_BED_SIZE"), int_define(text, "Y_BED_SIZE")
    pat = re.compile(r"(?m)^([ \t]*#define[ \t]+NOZZLE_PARK_POINT[ \t]+)\{([^}]*)\}[^\n]*$")
    m = pat.search(text)
    if not m or xb is None or yb is None:
        if active_define(adv_text, "PARK_HEAD_ON_PAUSE"):
            sys.exit("park point: PARK_HEAD_ON_PAUSE is active but NOZZLE_PARK_POINT or the bed size was not found")
        return text, None
    z = m.group(2).split(",")[-1].strip()
    x, y = min(200, xb - 20), min(200, yb - 20)
    point = f"{{ {x}, {y}, {z} }}"
    new = f"{m.group(1)}{point}  // CI: inside the real travel; the generator default parks outside it"
    return text[:m.start()] + new + text[m.end():], point


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True, help="path to Special_Configurations checkout")
    ap.add_argument("--target", default=".", help="firmware checkout to install the configs into")
    ap.add_argument("--name", required=True, help="Configurator-style name (used for the .bin)")
    ap.add_argument("--machine-name", default=None, help="name inside the firmware, 32 chars max")
    ap.add_argument("--features", required=True, help="comma-separated option codes")
    args = ap.parse_args()

    features = [f for f in args.features.split(",") if f]
    mname = args.machine_name or args.name
    if len(mname) > 32:
        sys.exit(f"machine name {mname!r} is {len(mname)} chars; Marlin allows 32 at most")
    gen = Path(args.gen).resolve()
    target = Path(args.target).resolve()
    sys.path.insert(0, str(gen))
    import os
    os.chdir(gen)
    import CreateConfigs

    if CreateConfigs.Generate(mname, features):
        print((gen / mname / "log.txt").read_text())
        sys.exit("generator reported an error")

    out = gen / mname
    conf_h = (out / "Configuration.h").read_text()
    conf_adv = (out / "Configuration_adv.h").read_text()
    conf_h, park = patch_park_point(conf_h, conf_adv)
    (out / "Configuration.h").write_text(conf_h)
    cfg = conf_h + conf_adv
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
    print(f"OK {mname} (file name {args.name}): options={features} TEMP_SENSOR_0={m.group(1) if m else '?'} NOZZLE_PARK_POINT={park or 'unchanged'}")


if __name__ == "__main__":
    main()
