# OrcaSlicer profiles: E3V2-SpritePro-Wifi

These are standalone OrcaSlicer user presets, tested with Orca 2.4.2. Each one has `"inherits": ""`, so it doesn't depend on a system or parent preset.

- `machine/`: "Creality Ender-3 V2 (Sprite Pro, Fast)" printers for 0.2, 0.4, 0.6, 0.8 and 1.0 mm nozzles.
- `process/`: Fine, Optimal, Standard and Draft for each nozzle, built from the tuned 0.20mm Standard 0.4 profile. Each process only appears on the printer with its own nozzle size.
  - Layer heights are 0.3, 0.375, 0.5 and 0.6 times the nozzle size.
  - Line widths are scaled by nozzle/0.4.
  - Top and bottom layer counts keep shells about 1.0 mm and 0.8 mm thick.
- The filament profiles are general, so they live in `printer-config/orca-profiles/filament/`.

The 0.2, 0.6, 0.8 and 1.0 processes are calculated starting points. Test-print them before relying on them.

## Install

Quit Orca. Copy `machine/`, `process/` and `../../orca-profiles/filament/` into `~/Library/Application Support/OrcaSlicer/user/default/`. The printers run `~/Scripts/orca/orca-marlin-thumb.sh` as a post-processing script, and a copy of it is in `printer-config/tools/`.
