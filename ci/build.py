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
    """The generator parks the nozzle at {X_BED_SIZE+10, Y_MAX_POS-10, 20}, outside the bed. Park inside the
    configured travel instead: 30 mm in from the smaller of the bed size and the max position, never below the
    min position; keep the generator's Z raise. (A runtime clamp to the printer's own limits is added by
    patch_nozzle_park.)"""
    v = {n: int_define(text, n) for n in ("X_BED_SIZE", "Y_BED_SIZE", "X_MAX_POS", "Y_MAX_POS", "X_MIN_POS", "Y_MIN_POS")}
    pat = re.compile(r"(?m)^([ \t]*#define[ \t]+NOZZLE_PARK_POINT[ \t]+)\{([^}]*)\}[^\n]*$")
    m = pat.search(text)
    if not m or None in v.values():
        if active_define(adv_text, "PARK_HEAD_ON_PAUSE"):
            sys.exit("park point: PARK_HEAD_ON_PAUSE is active but NOZZLE_PARK_POINT or a bed/position limit was not found")
        return text, None
    z = m.group(2).split(",")[-1].strip()
    x = max(v["X_MIN_POS"], min(v["X_BED_SIZE"], v["X_MAX_POS"]) - 30)
    y = max(v["Y_MIN_POS"], min(v["Y_BED_SIZE"], v["Y_MAX_POS"]) - 30)
    point = f"{{ {x}, {y}, {z} }}"
    new = f"{m.group(1)}{point}  // CI: inside the configured travel; the generator default parks outside it"
    return text[:m.start()] + new + text[m.end():], point


def patch_spi_mode(conf_h):
    """SPI: read the onboard SD slot in SPI mode (Marlin option SD_SPI_MODE, implemented in this fork).
    The generator's Configuration.h doesn't know it, so switch it on right after SDSUPPORT."""
    if active_define(conf_h, "SD_SPI_MODE"):
        return conf_h
    m = re.search(r"(?m)^[ \t]*#define[ \t]+SDSUPPORT\b[^\n]*$", conf_h)
    if not m:
        sys.exit("SPI: #define SDSUPPORT not found in the generated Configuration.h")
    return conf_h[:m.end()] + "\n#define SD_SPI_MODE  // CI: SPI option, onboard SD slot read in SPI mode" + conf_h[m.end():]


def patch_spi_ignore_startup(adv_text):
    """SPI: don't mount the card while Marlin starts. With the SD-WIFI board in an SD-to-microSD adapter the
    printer did not finish booting in SPI mode; mounting later (menu, or re-inserting the card) works.
    Marlin refuses this together with POWER_LOSS_RECOVERY, so that and its menu item (PLR_TUNE_ITEM) go off
    in SPI builds. (They are off at runtime on this printer anyway: M413 S0.)"""
    if not re.search(r"(?m)^[ \t]*(//[ \t]*)?#define[ \t]+SD_IGNORE_AT_STARTUP\b", adv_text):
        sys.exit("SPI: SD_IGNORE_AT_STARTUP not found in the generated Configuration_adv.h")
    adv_text = re.sub(r"(?m)^([ \t]*)//[ \t]*(#define[ \t]+SD_IGNORE_AT_STARTUP\b)", r"\1\2", adv_text, count=1)
    return adv_text


def patch_spi_no_plr(text):
    for name in ("POWER_LOSS_RECOVERY", "PLR_TUNE_ITEM"):
        text = re.sub(rf"(?m)^([ \t]*)(#define[ \t]+{name}\b[^\n]*)$", r"\1//\2  // CI: off with SPI (SD_IGNORE_AT_STARTUP)", text, count=1)
    return text


def check_spi_source(src):
    """The SPI option only exists in this fork's firmware source; stop if the checkout doesn't have it."""
    pins = src / "pins" / "stm32f1" / "pins_CREALITY_V4.h"
    if "SD_SPI_MODE" not in pins.read_text():
        sys.exit("SPI: this firmware source has no SD_SPI_MODE support. Use firmware_source = this-fork "
                 "and a firmware_ref that contains it (e.g. sd-spi-mode)")


def patch_source(path, old, new, what):
    """Exact-text source patch; fails the build if the upstream code changed under us."""
    text = path.read_text()
    if text.count(old) != 1:
        sys.exit(f"{what}: expected text not found exactly once in {path.name}; upstream changed, update ci/build.py")
    path.write_text(text.replace(old, new, 1))


def patch_nozzle_park(src):
    """Clamp the XY park move to the printer's runtime software endstops (the limits set on the printer), so a
    park point beyond the real travel can never drive the carriage into the frame."""
    f = src / "libs" / "nozzle.cpp"
    t = f.read_text()
    if "park_c" in t:
        return
    head = "      constexpr feedRate_t fr_xy = NOZZLE_PARK_XY_FEEDRATE;\n"
    patch_source(f, head, head + "      xyz_pos_t park_c = park; apply_motion_limits(park_c); // CI: stay inside the soft endstops\n", "park clamp")
    t = f.read_text()
    for old, new in (("do_blocking_move_to_xy(park, fr_xy)", "do_blocking_move_to_xy(park_c, fr_xy)"),
                     ("do_blocking_move_to_x(park.x, fr_xy)", "do_blocking_move_to_x(park_c.x, fr_xy)"),
                     ("do_blocking_move_to_y(park.y, fr_xy)", "do_blocking_move_to_y(park_c.y, fr_xy)")):
        if old not in t:
            sys.exit(f"park clamp: {old!r} not found in nozzle.cpp")
        t = t.replace(old, new)
    f.write_text(t)


def patch_retract_cap(src):
    """DD: cap the firmware retract length at MAX_RETRACT_MM (M207 S and the EEPROM value both go through it)."""
    f = src / "feature" / "fwretract.cpp"
    patch_source(f, "if (parser.seenval('S')) settings.retract_length        = parser.value_axis_units(E_AXIS);",
                 f"if (parser.seenval('S')) settings.retract_length        = _MIN(parser.value_axis_units(E_AXIS), {MAX_RETRACT_MM}f); // CI: DD cap",
                 "retract cap")


PAUSE_RETRACT_MM = "1.0"  # DD: pause/M600 initial retract (generator default 2)
MAX_RETRACT_MM = "2.0"    # DD: hard cap on the firmware retract length (M207 S), source patch


def patch_pause_retract(adv_text):
    """Set the initial retract of pause and filament change (generator default 2 mm) to PAUSE_RETRACT_MM."""
    pat = re.compile(r"(?m)^([ \t]*#define[ \t]+PAUSE_PARK_RETRACT_LENGTH[ \t]+)[\d.]+")
    if not pat.search(adv_text):
        if active_define(adv_text, "ADVANCED_PAUSE_FEATURE"):
            sys.exit("pause retract: ADVANCED_PAUSE_FEATURE is active but PAUSE_PARK_RETRACT_LENGTH was not found")
        return adv_text, None
    return pat.sub(lambda m: m.group(1) + PAUSE_RETRACT_MM, adv_text, count=1), PAUSE_RETRACT_MM


FWRETRACT_DEFAULTS = {  # DD: direct-drive firmware retraction defaults (generator ships Bowden values: 5 mm, 40 mm/s, 0.2 mm raise)
    "RETRACT_LENGTH": "0.8",
    "RETRACT_FEEDRATE": "40",
    "RETRACT_ZRAISE": "0",
    "RETRACT_RECOVER_FEEDRATE": "40",
}


def patch_fwretract(adv_text):
    """Replace the generator's Bowden firmware-retraction defaults (5 mm, 40 mm/s, 0.2 mm raise)."""
    if not active_define(adv_text, "FWRETRACT"):
        return adv_text, None
    for name, value in FWRETRACT_DEFAULTS.items():
        pat = re.compile(rf"(?m)^([ \t]*#define[ \t]+{name}[ \t]+)[\d.]+")
        if not pat.search(adv_text):
            sys.exit(f"firmware retraction: FWRETRACT is active but {name} was not found")
        adv_text = pat.sub(lambda m: m.group(1) + value, adv_text, count=1)
    return adv_text, ", ".join(f"{k}={v}" for k, v in FWRETRACT_DEFAULTS.items())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True, help="path to Special_Configurations checkout")
    ap.add_argument("--target", default=".", help="firmware checkout to install the configs into")
    ap.add_argument("--name", required=True, help="Configurator-style name (used for the .bin)")
    ap.add_argument("--machine-name", default=None, help="name inside the firmware, 32 chars max")
    ap.add_argument("--features", required=True, help="comma-separated option codes")
    args = ap.parse_args()

    features = [f for f in args.features.split(",") if f]
    dd = "DD" in features
    spi = "SPI" in features
    features = [f for f in features if f not in ("DD", "SPI")]  # CI-side options: the generator does not know them
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
    if spi:
        check_spi_source(target / "Marlin" / "src")
        conf_h = patch_spi_mode(conf_h)
        conf_adv = patch_spi_no_plr(patch_spi_ignore_startup(conf_adv))
        conf_h = patch_spi_no_plr(conf_h)
    pause_retract = fwr = None
    if dd:
        conf_adv, pause_retract = patch_pause_retract(conf_adv)
        conf_adv, fwr = patch_fwretract(conf_adv)
    (out / "Configuration.h").write_text(conf_h)
    (out / "Configuration_adv.h").write_text(conf_adv)
    cfg = conf_h + conf_adv
    missing = []
    if spi and not active_define(cfg, "SD_SPI_MODE"):
        missing.append("SPI: SD_SPI_MODE not active")
    if spi and not active_define(cfg, "SD_IGNORE_AT_STARTUP"):
        missing.append("SPI: SD_IGNORE_AT_STARTUP not active")
    if spi and (active_define(cfg, "POWER_LOSS_RECOVERY") or active_define(cfg, "PLR_TUNE_ITEM")):
        missing.append("SPI: POWER_LOSS_RECOVERY / PLR_TUNE_ITEM still active")
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
    if active_define(cfg, "PARK_HEAD_ON_PAUSE") or active_define(conf_adv, "ADVANCED_PAUSE_FEATURE"):
        patch_nozzle_park(repo / "Marlin" / "src")
    if dd and active_define(cfg, "FWRETRACT") or dd and active_define(conf_adv, "FWRETRACT"):
        patch_retract_cap(repo / "Marlin" / "src")
    m = re.search(r"(?m)^[ \t]*#define[ \t]+TEMP_SENSOR_0[ \t]+(\S+)", cfg)
    print(f"OK {mname} (file name {args.name}): options={features} DD={dd} SPI={spi} TEMP_SENSOR_0={m.group(1) if m else '?'} NOZZLE_PARK_POINT={park or 'unchanged'} PAUSE_PARK_RETRACT_LENGTH={pause_retract or 'unchanged'} FWRETRACT=[{fwr or 'off'}]")


if __name__ == "__main__":
    main()
