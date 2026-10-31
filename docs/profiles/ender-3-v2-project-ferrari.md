# Ender 3 V2 Project Ferrari (speed profile, planned)

Project Ferrari is the **speed-optimised variant** of the standard Ender 3 V2 profile. It is **not active yet**: the standard profile is still being calibrated. Come back to this after the standard calibrations (initial-layer flow, retraction, calibration cube, input shaping) are done, then raise speed and acceleration step by step.

**Everything not listed here is inherited from the standard profile**, in `docs/PRINTER-SETTINGS.md` (tuned results log and filament table): hardware and firmware settings, E steps, probe offsets, filament temperatures, max volumetric speed, Linear Advance K, flow ratio, retraction. The start and end G-code are `gcode/start.gcode` and `gcode/end.gcode`. Nothing above 2 mm retraction (`tools/check_retracts.py`).

## Speed targets (mm/s, 0.2 mm layers, 0.4 mm nozzle): drafted 2026-10-31, not yet applied
| Setting | Target | Standard profile today (PLA+) |
|---|---|---|
| Initial layer / initial layer infill | 25 / 30 | 20-25 |
| Outer wall / inner wall / small perimeters | 50 / 70 / 50 % | 50 / 70 |
| Sparse infill / internal solid infill | 80 / 80 | 90 (infill) |
| Top surface | 50 | n/a |
| Gap infill / bridge / support | 40 / 30 / 60 | n/a |
| Travel | 150 | n/a |

## Acceleration targets (mm/s2): conservative until input shaping is tuned
| Setting | Target |
|---|---|
| Normal, outer wall, inner wall | 500 |
| Initial layer / top surface | 300 / 300 |
| Travel | 500 (raise to 800-1000 only after input shaping) |
| Jerk or junction deviation | leave at firmware value (needs `M503`) |

## Machine limits (Printer settings > Motion ability)
Match the firmware (`M203`, `M201`, `M205`); leave "Emit limits to G-code" unticked. Pending: the exact numbers need the printer's `M503`.

## Ceilings from the 13 mm3/s volumetric limit
About 172 mm/s at 0.2 mm layers (0.42 mm lines), 136 mm/s at 0.24 mm, 119 mm/s at 0.28 mm. Acceleration, ringing and cooling set the practical limit first.

## How Ferrari gets tuned (after the standard profile is finished)
1. Raise infill and inner wall speed first, in 10 mm/s steps, looking for ripples after corners and under-extrusion.
2. Do input shaping, then raise acceleration in steps.
3. Re-check flow, K and cooling at the new speeds, and re-run the max volumetric speed test if the walls look starved.
