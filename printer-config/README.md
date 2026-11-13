# printer-config

This folder holds my own printer material that isn't part of the mriscoc firmware. The firmware and its build setup (`Marlin/`, `presets/`, `ci/`, `.github/workflows/`, `docs/CI-FIRMWARE.md`) stay at the repo root.

## General (any printer)

| Path | What's in it |
|---|---|
| `orca-profiles/filament/` | OrcaSlicer filament profiles: Inland PLA+, Inland PETG+, DEEPLEE PLA Pro |
| `docs/GCODE-PREVIEW.md` | How to get G-code thumbnails showing on the mriscoc display |
| `tools/orca-marlin-thumb.sh` | Orca post-processing script for those thumbnails |
| `tools/check_retracts.py` | Flags retracts deeper than a limit in a sliced file |
| `tools/flatten.py`, `tools/nozzles.py` | Helpers used to flatten Orca presets and generate nozzle variants |

## Builds

| Folder | Hardware |
|---|---|
| `E3V2-SpritePro-Wifi/` | Ender-3 V2 with Sprite Pro direct drive, CR Touch and WiFi |
