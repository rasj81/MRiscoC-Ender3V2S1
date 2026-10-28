# Ender 3 V2 printer settings reference

Hardware: Ender 3 V2, 4.2.2 board (STM32F103RET6, 512 kB), DWIN display, Creality Sprite Pro direct drive with its built-in CR Touch mount, dual Z (splitter cable, timing belt sync), smart filament sensor. Fallback: previous Bowden setup.

Provenance tags: **[config]** read from the generated firmware config; **[ref]** one other user's working values (mriscoc/Ender3V2S1 discussion #883); **[memory]** recalled, unconfirmed; **[measure]** fill in from your own printer.

## Firmware builds
| Preset | Options | Thermistor |
|---|---|---|
| `ender3v2-sprite` | Ender3V2, 422, DWIN, BLT, UBL, T13, IS, LA, MPC | T13 (`TEMP_SENSOR_0 13`) [config]. T13 for the Sprite Pro is unconfirmed: compare the reading with a thermometer before heating. |
| `ender3v2-bowden` | same, no T13 | stock type 1 (`TEMP_SENSOR_0 1`) [config] |

File name: `<Configurator name>-<firmware branch>-<YYYYMMDD>.bin` (e.g. `Ender3V2-422-BLTUBL-T13-IS-LA-MPC-Bugfix-20261026.bin`). Machine name shown on the printer is shortened to 32 characters or less (`E3V2-422-BLTUBL-T13-IS-LA-MPC`). Branches: blank = latest bugfix, `stable` = newest New-Year-#### (regression testing).
Flash: copy only the `.bin` to the SD root (FAT32), use a new file name each time. Display assets are in the artifact's `display/` folder; a DWIN screen does not need an update with the stock icon set.

## Steps per mm and speeds
| Setting | Firmware default [config] | Notes |
|---|---|---|
| X, Y steps/mm | 80, 80 | standard; verify with a 100 mm print only if prints are off |
| Z steps/mm | 400 | unchanged by the splitter and belt |
| E steps/mm | **93 (stock Bowden)** | wrong for the Sprite Pro. Start near 424.9 [memory, from Creality's Ender-3 S1 Sprite config], then calibrate. |
| Max feedrate X/Y/Z/E | 500, 500, 10, 45 mm/s | |
| Max acceleration X/Y/Z/E | 500, 500, 100, 1000 | |
| Print acceleration | 500 | |
| Homing feedrate X/Y/Z | 50, 50, 10 mm/s | |
| Probe travel (XY) | 12,000 mm/min | |
| Probe Z fast / slow | 960 / 480 mm/min | other user used Z feed rate 480 [ref] |
| `INVERT_E0_DIR` | false | flip if filament goes backward when extruding |

E-steps method (direct drive): hot nozzle, mark 120 mm from the extruder entry, extrude 100 mm slowly, measure what remains. New E = old x 100 / actual extruded. Repeat, then `M500`. `M502` resets E to 93, so set it after any reset.
E-steps (measured): [measure]

## Probe (CR Touch, Sprite Pro built-in mount)
- Firmware default `NOZZLE_TO_PROBE_OFFSET { -41.5, -7, 0 }` [config]: for a different bracket, do not use.
- Other user, same hardware and firmware family [ref]: X -31.4, Y -40.1, Z -2.76 (Z is bed and nozzle specific). Mesh inset in the same post equals max position plus offset (X 183.6 = 215 - 31.4, Y 179.9 = 220 - 40.1).
- Left and front are negative. Measure from nozzle tip to the probe pin centre.
- Mine (measured 2026-10-27): X -31.2, Y -42.1 (centred with a small washer between nozzle and probe pin), Z -2.82 after removing spacers (earlier -3.21 with a 0.1 mm feeler gauge, now superseded). Confirm Z on the first-layer print and re-check if probe speed or mount changes.
- UBL mesh (2026-10-27): 6x6 points, Maximize area. Bounds read from the printer: X 10 to 183, Y 10 to 177 (matches the calculation from the probe offsets and bed limits). Point spacing about 34.6 mm in X and 33.4 mm in Y. Build warm, save to slot 0, activate, fade height 10. Rebuild after any probe or limit change. Go to 7x7 only if the mesh map shows a ridge or dip.
- Multi probing 2 and HS mode were enabled in the reference post [ref].

## Bed and limits (set on the printer screen, then `M500`)
Reference [ref]: X min 0, Y min -5, X max 215, Y max 220, Z max 235; mesh 7x7, fade height 10, inset 10.
Mine (measured 2026-10-27/28 in the current configuration): X 0 to 220, Y 0 to 220, Z max 230. The firmware's compiled Z_MAX_POS is 250, so set Z max to 230 on the printer screen and `M500` so the firmware never drives above the real limit. Mesh: 6x6, maximize area (see below), fade height 10.
Orca printer profile: bed shape 220 x 220 mm, origin 0,0 (front-left), max print height 230 mm, bed exclude area `0x0,10x0,10x145,0x145` (left-edge prime strip of `gcode/start.gcode`; if Orca rejects the point format, draw the rectangle in its editor). Usable area: 220 x 220 minus a 10 x 145 strip.

## Heater tuning
- Hotend uses MPC: run the autotune from the menu or `M306 T`, then `M500`. Reference PID values in the source post are not needed.
- Bed PID: autotune at 60 C, 5 cycles [ref], then `M500`. Reference result Kp 98.27, Ki 17.55, Kd 366.86 [ref, do not copy].

## Dual Z
Both motors share one driver through a splitter cable, so independent auto-align (G34) is not available. Plan: tensioned GT2 timing belt between the leadscrews; Prusa-style bump only to re-square. Splitter wiring halves the current per motor, so watch for skipped steps and keep Z speed and acceleration modest. Slicer end G-code `M84 X Y E` keeps Z energized.

## Startup sequence after flashing
1. Boot screen shows the new machine name; hotend reads room temperature (compare with a thermometer).
2. `M502`, `M500`, restart. Set E steps again.
3. Move X, Y, Z by hand: both Z motors same direction, no binding. Check homing, probe deploy and stow, extruder direction, filament sensor.
4. Set physical limits, probe offsets and Z offset on the screen; `M500` after each.
5. First heat-up watched: MPC autotune, bed PID, `M500`.
6. Square the gantry, level the bed screws, create a UBL mesh with the bed warm, save to slot 0, activate.
7. E-steps calibration, then first-layer test and a cube.
8. Calibrate in order: temperature, flow, pressure advance or Linear Advance K, retraction, then Input Shaping.
9. Save `M503` output to a file.

## Pre-print mesh tilt (decided 2026-10-27)
The 6x6 mesh stays saved in slot 0 and is not rebuilt per print. Each print reloads it and tilts it to the bed's current level:
`G28`, then `G29 L0` (reload slot 0; without this the tilt would compound from print to print), `G29 J` (3-point tilt), `M420 S1 Z10`.
Rebuild the full mesh warm (and `G29 S0` to save) after major changes: nozzle, probe mount, springs, bed surface, or if the first layer drifts. Start and end G-code files: `gcode/start.gcode` and `gcode/end.gcode` (drafts, untested; end G-code keeps Z locked with `M84 X Y E`).
Not verified on this firmware: that `G29 J` runs and reaches its points inside the mesh bounds; that the saved mesh loads after any change to the point count.

## Orca G-code files (reviewed 2026-10-28; all untested on the printer)
Retraction ceiling (owner rule, 2026-10-28): keep every retract at or below 2 mm on this direct drive (slicer 0.8 mm start, end-of-print 1.5 mm). No G-code command enforces this; it is enforced by the Orca retraction fields, and `tools/check_retracts.py` checks an exported .gcode file (`python3 tools/check_retracts.py print.gcode`; exits 1 if any retract, including a split wipe retract, is deeper than 2 mm, or if `M207 S` is above it; `--max 1.5` changes the limit). It can also run as an Orca post-processing script. Firmware pause/M600 retract (`PAUSE_PARK_RETRACT_LENGTH`) is 2 mm.
- `gcode/start.gcode`: Orca's original start (left-edge prime at X2, Z0.28, two E10 passes) plus warm-bed probing, `G29 L0` mesh reload, `G29 J` tilt, `M420 S1 Z10`. Bed exclude area for the prime strip: `0x0,10x0,10x145,0x145`.
- `gcode/end.gcode`: Orca's original end (lift above the print, present it at X5 / 80% of bed Y, raise the head, heaters and fan off, `M84 X Y E` so Z stays locked) plus a 1.5 mm retract and nozzle-off first. Needs Orca printable height 230 and firmware Z max 230.
- `gcode/before-layer-change.gcode`: unchanged. `G92 E0` is redundant with relative extrusion (`M83`) but harmless.
- `gcode/pause.gcode`: `M25` is correct for this firmware (with PARK_HEAD_ON_PAUSE it calls `M125`, which pauses, retracts and parks). Do not use `M601`: this firmware has no `M601`.
- `gcode/original/`: Orca's originals, kept verbatim.
- Park point (fixed in CI 2026-10-28, NOT yet in the flashed firmware): the generator's default `NOZZLE_PARK_POINT {X_BED_SIZE+10, Y_MAX_POS-10, 20}` = X 240, Y 221 is outside your 220 x 220 travel, and Marlin's park move is not clamped by the soft limits. `ci/build.py` now rewrites it to `{ 200, 200, 20 }` (20 mm in from the bed size, at most 200) and fails the build if it cannot. It takes effect only after you run a new build and flash it. Until then: do not pause, and do not trust the runout sensor.

## Slicer settings by filament type and nozzle size

Orca Slicer / Bambu Studio terms. **Every value is a starting point from general practice, not tested on this printer, and the spool label's range overrides mine.** Put filament values in the Filament profile and nozzle values in the Printer/Process profile. Slicer retraction is used; firmware retraction stays off.

### Common to everything (printer / process profile)
| Setting | Value | Why |
|---|---|---|
| Walls | Arachne generator | thin features and small text print instead of being skipped |
| Seam | scarf seam, contour | hides the seam on round parts |
| Infill | Gyroid (strength), Adaptive Cubic (save filament), Lightning (display only); avoid Grid | see the printpal and Creality notes in the 3d-printing skill |
| Acceleration | 500 (firmware default); raise only after Input Shaping is tuned | |
| Travel speed | 150 mm/s | |
| Bed mesh | UBL, fade height 10 | |
| Printer end G-code | `M84 X Y E` | keeps Z motors locked so the gantry does not drop (dual Z) |
| Printer start G-code | `gcode/start.gcode` in this repo (merged with the original start 2026-10-28, untested): heat bed, `G28`, `G29 L0`, `G29 J`, `M420 S1 Z10`, then the original left-edge prime at X2 (Z0.28, two E10 passes) | [measure] confirm the 3-point tilt reaches its points inside the mesh bounds and that the mesh stays active after `G28` |

### Filament profiles (0.4 mm nozzle values)
| | PLA | PLA+ | PLA Pro | PETG+ | ABS | ASA |
|---|---|---|---|---|---|---|
| Nozzle C | 205-215 (210) | 210-225 (215) | 210-230 (220) | 235-250 (240) | 240-260 (250) | 245-265 (255) |
| First layer nozzle | +5 | +5 | +5 | +5 | +0 | +0 |
| Bed C | 55-60 | 55-65 | 55-65 | 75-80 | 95-100 | 90-100 |
| Part fan | 100 % from layer 3 | 70-100 % | 70-100 % | 20-40 % | 0-20 % | 0-30 % |
| Outer / inner / infill speed (mm/s) | 60/80/100 | 50/70/90 | 50/70/90 | 40/55/65 | 40/60/70 | 40/60/70 |
| First layer speed (mm/s) | 20-25 | 20-25 | 20-25 | 20 | 20 | 20 |
| Max volumetric speed (mm3/s) | 10-12 | 9-11 | 9-11 | 8-10 | 10-12 | 10-12 |
| Flow ratio | 0.98 | 0.98 | 0.98 | 0.95-0.98 | 0.95-0.98 | 0.95-0.98 |
| Retraction (direct drive) | 0.8 mm at 35 mm/s | 0.8 mm at 35 | 0.8 mm at 35 | 0.8-1.2 mm at 30 | 0.8 mm at 30 | 0.8 mm at 30 |
| Z hop | off | off | off | 0.2 mm if it drags | off | off |
| Enclosure | no | no | no | no | **yes** | **yes** |

- PLA+, PLA Pro and PETG+ are brand blends: they vary a lot between makers, so start from the label and tune.
- PETG+ strings and sticks to the nozzle; keep the fan low and the nozzle clean.
- ABS and ASA warp and crack on an open frame. Print them only in an enclosure. I haven't confirmed the Sprite Pro hotend's temperature rating; check its manual before going above about 260 C.

### Nozzle profiles (layer height and line width)
| Nozzle | Layer height (range) | Line width | Walls | Notes |
|---|---|---|---|---|
| 0.2 | 0.10 (0.08-0.12) | 0.22 | 4-5 | slow, +5 C, clogs easily; avoid abrasive filaments |
| 0.4 | 0.20 (0.12-0.28) | 0.42 | 3 | baseline |
| 0.6 | 0.30 (0.20-0.40) | 0.62 | 2-3 | good speed/detail compromise |
| 0.8 | 0.40 (0.30-0.60) | 0.82 | 2 | likely needs +5 to +10 C for flow |
| 1.0 | 0.50 (0.40-0.75) | 1.00 | 2 | flow limited by the heater; expect slow outer walls |

Large nozzles do not remove the melt-rate limit. The cap is the **max volumetric speed** of the hotend and filament. Set it per filament (table above) and let the slicer slow the print down. Speed at the cap = volumetric speed / (layer height x line width):

| Nozzle | Layer | Width | PLA | PLA+ | PLA Pro | PETG+ | ABS | ASA |
|---|---|---|---|---|---|---|---|---|
| 0.2 | 0.10 | 0.22 | 455 | 409 | 409 | 364 | 455 | 455 |
| 0.4 | 0.20 | 0.42 | 119 | 107 | 107 | 95 | 119 | 119 |
| 0.6 | 0.30 | 0.62 | 54 | 48 | 48 | 43 | 54 | 54 |
| 0.8 | 0.40 | 0.82 | 30 | 27 | 27 | 24 | 30 | 30 |
| 1.0 | 0.50 | 1.00 | 20 | 18 | 18 | 16 | 20 | 20 |

(mm/s at the default layer and width, using the low volumetric value from the filament table. The slicer's own feature speeds apply first.) A 0.8 or 1.0 nozzle is slow unless the hotend can sustain a higher flow; raise the cap only after a flow test shows no under-extrusion or grinding.

Per nozzle change: re-check flow ratio and Linear Advance K, set retraction a little higher for 0.8 and 1.0 (try 1.0 to 1.5 mm), re-run MPC autotune because the heater block and nozzle change, and redo the Z offset if the nozzle length changed. Whether the Sprite Pro takes all of these sizes is not something I have confirmed.

### Tuned results log (fill in)
| Filament | Nozzle | Temp | Flow | LA K | Retraction | Max vol. | Date |
|---|---|---|---|---|---|---|---|
| | | [measure] | [measure] | [measure] | [measure] | [measure] | |

### Calibration order per new filament (from the 3d-printing skill)
Temperature tower, flow rate, Linear Advance K, retraction, then (once only) Input Shaping. Record each result in the log above.

## Status (2026-10-28)
Flashed and running. Done: MPC autotune, bed PID autotune, `M503` output saved. Measured: probe X -31.2, Y -42.1, Z offset -2.82. Still borrowed or unverified: E steps 424.9, bed limits from the reference post; Z offset still needs the first-layer confirmation.

## Open items
1. Z offset: -2.82 measured; confirm on the first-layer print (live adjust 0.02 to 0.05 mm), then `M500`.
2. Verify E steps by measuring (120 mm mark, extrude 100 mm).
3. Probe offsets measured; check bed limits slowly at each edge and update the mesh bounds if they change.
4. ~~Bed PID autotune~~ done.
5. Build and save the UBL mesh (bed warm), slot 0, activate.
6. Retraction in the slicer (start 0.8 mm at 35 mm/s, direct drive); firmware retraction stays off.
7. Linear Advance K, then Input Shaping.
8. Smart filament sensor: needs the firmware option (not in the generator feature list).
9. `M503` saved once; save a new copy after the remaining tuning.
10. CI follow-ups: GitHub Releases for builds, `BUILDS.md`, cleanup action, clean/experimental tiers.
11. Firmware park point: patched in `ci/build.py` (70a9724+). Run "Build custom firmware", flash the new .bin, then confirm with a pause test at a safe moment (hand on the power switch). Until flashed, do not pause and treat the runout sensor as unsafe.
