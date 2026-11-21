# Going back to the standard (SDIO) firmware

The printer has run two firmware variants for this build. Both come from the same CI presets and have the same options; they differ only in how the onboard SD slot is read.

| Variant | Preset | SD slot | Power-loss recovery | Use it with |
|---|---|---|---|---|
| Standard (SDIO) | `ender3v2-sprite` | SDIO (Marlin default for the 4.2.2 board) | compiled in | normal SD cards, and the Toshiba FlashAir W-04 |
| SPI | `ender3v2-sprite-spi` | SPI mode (`SD_SPI_MODE`, this fork only), card not mounted at startup | compiled out | the FYSETC SD-WIFI board, which cannot share an SDIO bus |

Since 2026-11-06 the printer runs the SPI build. Nothing new is needed for SPI: the preset and the source patch already exist.

## Saved standard binary

`../firmware/standard-sdio-20261028/` holds the last standard build that ran on this printer (the pre-SPI firmware, built 2026-10-28):

- `Ender3V2-422-BLTUBL-T13-DD-IS-LA-MPC-Bugfix-20261028.bin` (sha256 in `SHA256SUMS.txt`; check with `shasum -a 256 -c SHA256SUMS.txt`)
- `config/Configuration.h`, `config/Configuration_adv.h`, `config/Version.h`: the exact generated config it was compiled from

Checked in that config:

| Setting | Value |
|---|---|
| Board / display | 4.2.2 (STM32F103RET6), DWIN, ProUI 2.1.4 MRiscoC, bugfix-2.1.x |
| Probe / leveling | `BLTOUCH` (CR Touch), `AUTO_BED_LEVELING_UBL` |
| Thermistor | `TEMP_SENSOR_0 13` |
| Motion | `INPUT_SHAPING_X`, `INPUT_SHAPING_Y`, `LIN_ADVANCE`, `MPCTEMP` |
| Serial | `BAUDRATE 250000` (matches OctoPrint) |
| Speaker | `SPEAKER` off (M300 duration only) |
| Direct drive (DD) | `PAUSE_PARK_RETRACT_LENGTH 1.0`, `RETRACT_LENGTH 0.8` |
| Park point | `NOZZLE_PARK_POINT { 200, 200, 20 }` |
| SD | no `SD_SPI_MODE`, no `SD_IGNORE_AT_STARTUP`; `POWER_LOSS_RECOVERY` on |

Dual Z is mechanical (splitter cable on one driver, belt sync), so there is no firmware setting for it. Keep `M84 X Y E` in the end and cancel G-code so Z stays locked.

The CI scripts have not changed since this binary was built except to add the SPI option, so a fresh `ender3v2-sprite` build gives the same options on newer mriscoc code.

## Flash it

1. Save the current settings first: send `M503` and keep the output (OctoPrint terminal), or use `../gcode/restore-settings-20261106-1638.gcode`, which matches the current values.
2. Copy only the `.bin` to the root of a FAT32 SD card. Give it a name the printer has not seen before; renaming it (for example adding `-a`) is enough.
3. Power off, insert the card, power on, and wait for the screen to come up (about 10 to 20 seconds).
4. Send `M502` then `M500`, then print `../gcode/restore-settings-20261106-1638.gcode` from the SD card and check with `M503`.
5. Turn power-loss recovery off again if you want it off: `M413 S0`, `M500`. The restore file has no `M413` line because the SPI build does not have that command.
6. Re-run the bed mesh (the restore file does not include it), then check the Z offset on a first-layer print.

## Fresh build instead

Actions tab > "Build custom firmware" > Run workflow, preset `ender3v2-sprite`, leave `firmware_ref` blank (latest bugfix) and `firmware_source` at `upstream-latest`. Download the artifact; the `.bin` is in `dist/`. To go back to SPI later, run the same workflow with preset `ender3v2-sprite-spi`.

## FlashAir W-04 notes

The FlashAir behaves as an ordinary SD card, so it belongs in the standard (SDIO) build. Untested on this printer. Uploading over WiFi while the printer has the card mounted can corrupt the file list; upload with the printer idle, then re-select the card from the menu so it re-reads it.
