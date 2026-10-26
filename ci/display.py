#!/usr/bin/env python3
"""Copy the display assets that match the selected display into the build output.

Layout follows the firmware repo's "display assets" folder. Missing paths (older
branches may differ) produce a warning, never a failed build.
"""
import argparse
import shutil
import sys
from pathlib import Path

INSTALL = """DISPLAY FIRMWARE / ICONS ({display})
{what}

Most users do not need this: the stock icon set works without updating the
display. Install only to change icon set or when the notes below say an update
is needed.

How to install (from the firmware repo's display assets notes)
1. Use a microSD card of 8 GB or less, formatted MBR, FAT32, 4 KB allocation unit.
2. Copy ONLY the folder named below to the root of the card.
3. Power off the printer, open the screen unit and insert the card in its slot.
4. Power on. The display changes from blue to orange when it is done.
5. Power off, remove the card, reassemble.
"""

# display -> list of (source path inside "display assets", destination under out/)
ASSETS = {
    "DWIN": [("stock/DWIN_SET", "stock/DWIN_SET"),
             ("Giadej compilation/DWIN_SET", "giadej/DWIN_SET")],
    "DACAI": [("stock/private", "stock/private"),
              ("Giadej compilation/private", "giadej/private"),
              ("dacai_update.zip", "dacai_update.zip")],
    "TJC": [("tjc_update.zip", "tjc_update.zip")],
}
NOTES = {
    "DWIN": "DWIN_SET folders: stock icons, or the Giadej icon set (DWIN and DACAI only).",
    "DACAI": "private folders: stock or Giadej. dacai_update.zip is the screen firmware "
             "update needed for G-code preview on some units.",
    "TJC": "tjc_update.zip (contains TJC_SET) is needed on some units to boot and show "
           "G-code preview. TJC also needs its special firmware compile.",
    "SYNWIT": "No display files are documented for this screen in the firmware repo.",
    "CR10DSPLY": "Monochrome LCD: it has no display firmware to install.",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fw", required=True)
    ap.add_argument("--display", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    base = Path(args.fw) / "display assets"
    for src, dst in ASSETS.get(args.display, []):
        s, d = base / src, out / dst
        if not s.exists():
            print(f"::warning::display asset not found on this branch: {src}")
            continue
        if s.is_dir():
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(s, d)
    what = NOTES.get(args.display, "No display files for this option.")
    (out / "README-DISPLAY.txt").write_text(INSTALL.format(display=args.display, what=what))
    print(f"display assets for {args.display}: {sorted(p.name for p in out.iterdir())}")


if __name__ == "__main__":
    sys.exit(main())
