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
- Mine: X [measure], Y [measure], Z [measure, paper test, re-check if probe speed changes]
- Multi probing 2 and HS mode were enabled in the reference post [ref].

## Bed and limits (set on the printer screen, then `M500`)
Reference [ref]: X min 0, Y min -5, X max 215, Y max 220, Z max 235; mesh 7x7, fade height 10, inset 10.
Mine: X min [measure], Y min [measure], X max [measure], Y max [measure], Z max [measure]

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

## Open items
Probe offsets, bed limits, E steps, Z offset, MPC and PID results, Linear Advance K, Input Shaping frequencies, smart filament sensor option (not in the generator feature list).
