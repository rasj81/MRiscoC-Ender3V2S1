#!/usr/bin/env python3
"""Check a sliced .gcode file for retractions longer than a limit (default 2 mm).

Why: on a direct-drive hotend a long retract can pull molten plastic into the cool zone and clog it.
No Marlin command caps retraction, so this checks the file the slicer exported.

What it measures
- Every G0/G1 move with an E value, in relative (M83) or absolute (M82) extruder mode; G92 E resets are followed.
- "Depth": how far the filament is currently pulled back from the primed position. Retracts split over several
  moves (for example during a wipe) add up; extrusion and unretracts reduce it. The report uses the deepest value.
- Firmware retraction: M207 S<length> above the limit, and G10 use (reported, because the length is then set by M207).

Usage
  python3 tools/check_retracts.py print.gcode            # exit 1 if any retract is deeper than 2 mm
  python3 tools/check_retracts.py print.gcode --max 1.5
  python3 tools/check_retracts.py print.gcode --warn-only # always exit 0

Orca Slicer: Process settings > Others > Post-processing scripts, one line: python3 /full/path/to/check_retracts.py
(Orca appends the G-code path). A failing exit makes Orca report an error.
"""
import argparse
import re
import sys

MOVE = re.compile(r"^G[01]\b", re.I)
E_WORD = re.compile(r"\bE(-?\d*\.?\d+)", re.I)
S_WORD = re.compile(r"\bS(-?\d*\.?\d+)", re.I)


def check(path, limit):
    relative = False          # M82 absolute (default) / M83 relative
    e_pos = 0.0               # absolute-mode extruder position
    depth = 0.0               # current pulled-back amount (mm)
    worst = (0.0, 0)          # (depth, line number)
    over = []                 # (line number, depth) each time the depth first exceeds the limit
    flagged = False
    fw_retract_used = 0
    fw_len = []               # (line, M207 length)
    with open(path, errors="replace") as fh:
        for n, raw in enumerate(fh, 1):
            line = raw.split(";", 1)[0].strip()
            if not line:
                continue
            up = line.upper()
            if up.startswith("M83"):
                relative = True
            elif up.startswith("M82"):
                relative = False
            elif up.startswith("G92"):
                m = E_WORD.search(line)
                if m:
                    e_pos = float(m.group(1))
            elif up.startswith("G10") and not up.startswith("G10 L"):
                fw_retract_used += 1
            elif up.startswith("M207"):
                m = S_WORD.search(line)
                if m:
                    fw_len.append((n, float(m.group(1))))
            elif MOVE.match(line):
                m = E_WORD.search(line)
                if not m:
                    continue
                val = float(m.group(1))
                delta = val if relative else val - e_pos
                if not relative:
                    e_pos = val
                if delta < 0:
                    depth += -delta
                else:
                    depth = max(0.0, depth - delta)
                if depth > worst[0]:
                    worst = (depth, n)
                if depth > limit + 1e-6 and not flagged:
                    over.append((n, depth))
                    flagged = True
                if depth <= limit + 1e-6:
                    flagged = False
    return worst, over, fw_retract_used, fw_len


def main():
    ap = argparse.ArgumentParser(description="Report retractions longer than a limit in a G-code file.")
    ap.add_argument("gcode")
    ap.add_argument("--max", type=float, default=2.0, help="longest allowed retract in mm (default 2.0)")
    ap.add_argument("--warn-only", action="store_true", help="print problems but always exit 0")
    a = ap.parse_args()
    worst, over, fw_used, fw_len = check(a.gcode, a.max)
    problems = []
    for n, d in over[:10]:
        problems.append(f"line {n}: retracted {d:.2f} mm (limit {a.max:g} mm)")
    if len(over) > 10:
        problems.append(f"... and {len(over) - 10} more")
    for n, v in fw_len:
        if v > a.max + 1e-6:
            problems.append(f"line {n}: M207 firmware retract length {v:g} mm (limit {a.max:g} mm)")
    print(f"deepest retract: {worst[0]:.2f} mm (line {worst[1]}); limit {a.max:g} mm; "
          f"firmware retracts (G10): {fw_used}")
    for p in problems:
        print("  PROBLEM:", p)
    if problems and not a.warn_only:
        sys.exit(1)
    print("OK" if not problems else "problems found (warn-only)")


if __name__ == "__main__":
    main()
