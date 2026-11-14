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

## Turbo set

`machine/` and `process/` also hold a "(Sprite Pro, Turbo)" copy of every printer and process, made by `printer-config/tools/turbo.py` from the Fast files (the Fast files are unchanged). Turbo filaments ("Inland PLA+ (Turbo)" and so on) are in `printer-config/orca-profiles/filament/` and only appear on the Turbo printers.

- Walls (outer/inner, mm/s): 0.2: 150/180, 0.4: 150/200, 0.6: 120/160, 0.8: 90/120, 1.0: 70/100. Sparse infill matches the inner wall; solid infill matches the outer wall; travel 250.
- Accelerations (mm/s²): default 4000, inner wall 4000, outer wall 2500, top surface 2000, travel 5000, first layer 500.
- Printer limits: max X/Y/extruding/travel acceleration 5000, max X/Y speed 500, and "Emit limits to G-code" is on, so each Turbo print sends M201/M203/M204/M205 (the EEPROM caps X/Y at 3000).
- Turbo filaments raise max volumetric speed (PLA+ 18, DEEPLEE 17, PETG+ 14 mm³/s) and nozzle temperature (PLA 220 °C, PETG 245 °C). Orca slows any move that would go over that flow, so the bigger nozzles are flow-limited well below the speeds above.
- `printer_model` is "Creality Ender-3 V2" (not the doubled "Creality Creality") so a save in Orca can't point `inherits` at a missing parent.
- OctoPrint host and API key are blank here; they're set only in the installed copies.

None of the Turbo profiles has been printed yet. Expect ringing at these accelerations until input shaping is retuned.
