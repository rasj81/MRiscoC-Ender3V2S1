# OrcaSlicer profiles: Ender-3 V2 + Sprite Pro

These are standalone OrcaSlicer user presets, tested with Orca 2.4.2. Each one has `"inherits": ""`, so it carries every setting itself and doesn't depend on a system or parent preset.

## Contents

- `machine/`: "Creality Ender-3 V2 (Sprite Pro, Fast)" printers for 0.2, 0.4, 0.6, 0.8 and 1.0 mm nozzles.
- `process/`: Fine, Optimal, Standard and Draft processes for each nozzle. They're all built from the tuned 0.20mm Standard 0.4 profile, and each one is only compatible with the printer for its own nozzle size.
  - Layer heights are 0.3, 0.375, 0.5 and 0.6 times the nozzle size.
  - Line widths are scaled by nozzle/0.4.
  - Top and bottom layer counts keep shells about 1.0 mm and 0.8 mm thick.
- `filament/`: Inland PLA+, Inland PETG+ and DEEPLEE PLA Pro (Amazon). They're compatible with all the printers above.
- `tools/flatten.py`: merges a preset's inheritance chain into the preset itself.
- `tools/nozzles.py`: generates the nozzle variants.

The 0.2, 0.6, 0.8 and 1.0 processes are calculated starting points. Test-print them before relying on them.

## Install

Quit Orca, then copy the three folders into `~/Library/Application Support/OrcaSlicer/user/default/`. The machine profiles call `~/Scripts/orca/orca-marlin-thumb.sh` as a post-process script.

`tools/` holds the scripts that did the first flatten and generated the nozzle variants. The final rename to the "(Sprite Pro, Fast)" names was done separately, so running these scripts again won't reproduce the exact file names here.
