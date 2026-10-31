# Ender 3 V2 Project Ferrari (profile)

Working profile for the Ender 3 V2 with Sprite Pro direct drive, CR Touch, dual Z, 0.4 mm stainless nozzle, running the `ender3v2-sprite` firmware from this fork. Created 2026-10-31. Status per line: **measured** (calibrated on this printer), **set** (chosen, not yet validated by prints), **pending** (needs a test or the printer's `M503`).

General reference for the printer: `docs/PRINTER-SETTINGS.md`. G-code files: `gcode/start.gcode`, `gcode/end.gcode`. Retract checker: `tools/check_retracts.py` (nothing above 2 mm).

## Printer hardware and firmware
| Item | Value | Status |
|---|---|---|
| Nozzle | 0.4 mm stainless | set |
| Extruder E steps/mm | 424.9 | measured 2026-10-30 (120 mm mark, 100 mm extrude, no change) |
| Probe offsets X / Y / Z | -31.2 / -42.1 / -2.82 | measured 2026-10-27 (re-measure after the Z rebuild) |
| Bed size and limits | 220 x 220, Z max 230 | set |
| Leveling | UBL 6x6 mesh, built warm, `M420 S1 Z10` | set |
| Firmware retraction | `M207 S0.8 F2100 Z0`, `M208 S0 F2100` (set in start G-code); capped at 2 mm in firmware (DD build) | set |
| Orca G-code flavor | Marlin 2 | set |

## Filament: red PLA+ (brand blend)
| Setting | Value | Status |
|---|---|---|
| Nozzle temperature | 210 other layers, 215 first layer | measured (tower 190-230, 5 C steps) |
| Bed temperature | 60 / 60 (smooth PEI) | set |
| Max volumetric speed | 13 mm3/s | measured (tower failed at 20.5 mm = 15.25 mm3/s, set at about 85 %) |
| Linear Advance K (pressure advance) | 0.03 | measured (pattern, 0 to 0.1 step 0.005, owner's pick) |
| Flow ratio | 0.955 provisional (pass 1 picked between 0 and -5 from 0.98) | pending pass 2 |
| Initial layer flow | not measured | pending |
| Retraction (slicer) | 0.8 mm at 35 mm/s, never above 2 mm | pending retraction test |
| Filament diameter | 1.73 / 1.74 / 1.76 (avg 1.743) | measured |

## Process: speeds (mm/s), 0.2 mm layer
| Setting | Value | Status |
|---|---|---|
| Initial layer / initial layer infill | 25 / 30 | set |
| Outer wall / inner wall / small perimeters | 50 / 70 / 50 % | set |
| Sparse infill / internal solid infill | 80 / 80 | set |
| Top surface | 50 | set |
| Gap infill / bridge / support | 40 / 30 / 60 | set |
| Travel | 150 | set |

Theoretical ceiling at 13 mm3/s on this nozzle: about 172 mm/s at 0.2 mm layers (0.42 mm lines), 136 mm/s at 0.24, 119 mm/s at 0.28. Acceleration, ringing and cooling set the practical limit first.

## Process: acceleration (mm/s2), until input shaping is tuned
| Setting | Value | Status |
|---|---|---|
| Normal, outer wall, inner wall | 500 | set |
| Initial layer / top surface | 300 / 300 | set |
| Travel | 500 | set |
| Jerk or junction deviation | leave at firmware value | pending `M503` |

## Printer: Motion ability (machine limits)
Match the firmware (`M203` max feedrate, `M201` max acceleration, `M205` jerk). Leave "Emit limits to G-code" unticked. **Pending:** exact values need the printer's `M503` output.

## Calibration status
Done: temperature, max volumetric speed, E steps, Linear Advance K, flow pass 1. Left: flow pass 2, initial-layer flow, retraction test, dimension check (calibration cube), input shaping. Revisit afterwards: brim-start blob, nozzle brushing the part after a pause return, saving a fresh `M503`.
