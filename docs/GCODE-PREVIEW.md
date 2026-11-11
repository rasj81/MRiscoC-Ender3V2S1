# G-code thumbnail preview (Orca Slicer to the printer screen)

How to get a thumbnail on the printer's screen (Ender 3 V2 with Sprite Pro, SPI build) from Orca Slicer without the Python script. Written 2026-11-11.

## How it works
- The firmware has the preview feature compiled in (`HAS_GCODE_PREVIEW 1` in the fork's `Marlin/Configuration.h`, inside the `PROUI_EX` block). The code that reads the thumbnail is closed source: only `gcode_preview.h` is in the repo; the rest ships precompiled in `Marlin/lib/proui/stm32f1/libproui_*.a`. We cannot change it here.
- The screen shows a **JPEG thumbnail, base64-coded, maximum 20 KB**, embedded in the G-code.
- Orca writes the tag as `thumbnail_JPG` (capitals). Per mriscoc discussion #1184 and issue #1176 (Orca 1.8.1, 2023), the firmware only recognises lowercase `thumbnail_jpg`. `gcode/orca-marlin-thumb.sh` changes the case after slicing, and only on files sliced for Marlin 2, so Bambu and other profiles are left alone.
- The official route is mriscoc's Python script (`slicer scripts/prusa-superslicer/professionalfirmware.py` in the upstream repo, wiki page "How to generate a gcode preview"). It also puts print info next to the thumbnail. This shell script gives the picture only.

## Status: what is and is not verified
- Verified: the shell script's behaviour on test files (Marlin 2 file changed, other flavor untouched, missing file ignored); the firmware default config enables the preview.
- **Not yet verified on the printer:** that the lowercase edit makes your screen show the preview, that Orca's current version still writes exactly `thumbnail_JPG`, and that Orca still writes `; gcode_flavor = marlin2` in the settings block at the end of the file. Check these in step 5 below.

## Orca setup
1. Switch to **Expert** mode (top right) so the settings are visible.
2. **Printer settings > Basic information:** set **G-code flavor** to **Marlin 2**. The script only acts on this flavor.
3. **Printer settings > General > G-code thumbnails:** enter `230x180` (use `180x180` for a TJC screen), format **JPG**.
4. Put the script somewhere permanent, for example `~/bin/orca-marlin-thumb.sh`, and run `chmod +x` on it. Then in the **Process** profile used for the Ender, open **Others > Post-processing scripts** (turn on Advanced) and enter the full script path (for example `/Users/<you>/bin/orca-marlin-thumb.sh`). Attach it only to the Ender process profile; Orca stores the setting per profile.
5. Slice, export the G-code, and open it in a text editor:
   - near the top, the thumbnail block should read `; thumbnail_jpg begin 230x180 <bytes>` (lowercase) and the byte count should be under 20,000;
   - near the bottom, the settings block should contain the line `; gcode_flavor = marlin2`.
   If the tag has different text, or the flavor line is different, edit the `grep` and `sed` patterns in the script to match.

## On the printer
1. The SPI firmware build already includes the preview feature; no menu setting is needed. Use a build from this repo's default configuration.
2. Copy the G-code to the card as a normal file (the SD-WIFI card or by hand). File names must use plain characters only (no Chinese, Russian or other special characters). Do not push the file through OctoPrint, which can strip the thumbnail.
3. Open the file list on the printer and select the file; the preview shows before you start.
4. **Display check before blaming Orca:** print or open mriscoc's demo file, `SimpleCuraTest.gcode` (upstream repo, `slicer scripts/cura/`). If that shows a preview, the firmware and screen are fine and the problem is in the G-code. If it does not, the screen unit may need an update: DACAI screens may need the display firmware from upstream `display assets/dacai_update.zip`.

## Troubleshooting
| Symptom | Likely cause |
|---|---|
| "No thumbnail" on the printer | Tag still `thumbnail_JPG`; script not attached to this profile; script not executable; flavor not Marlin 2 |
| Script does not run | Path wrong or has spaces unquoted; `chmod +x` missing; Orca needs the full path |
| Thumbnail missing only on detailed models | JPEG over 20 KB; try a smaller size such as `180x180` |
| QR-code-like glitch screen | Display asset font mismatch; see upstream wiki "How to update the display" |
| Works in Orca preview but not on the printer | Wrong size for the screen type (230x180 vs 180x180) |

## If the lowercase edit does not work
Use the upstream script instead: install Python 3 and Pillow (`pip3 install Pillow`), save `professionalfirmware.py`, and put `/path/to/python3 /path/to/professionalfirmware.py;` in the same **Post-processing scripts** box.
