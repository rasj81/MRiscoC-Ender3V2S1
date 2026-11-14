# OctoPrint

OctoPrint setup for this build (Ender-3 V2, Sprite Pro, WiFi), running mriscoc Marlin. Staying on Marlin, not Klipper.

## Hardware

- Raspberry Pi 3B running OctoPi 64-bit (camera-streamer). Hostname `octopi`, user `pi`, SSH key login.
- Camera: Kano USB webcam (UVC), not a Pi Camera Module.
- Pi is powered separately from the printer. Tape over the 5V pin on the printer's USB cable so the Pi doesn't backfeed the mainboard.

## Connection

- Serial baud 250000 (matches `BAUDRATE` in the firmware), or Auto.
- The firmware already has the host options OctoPrint uses (host action commands, host prompts, emergency parser, auto temperature reports, arcs), so no reflash is needed.

## G-code scripts

- Leave OctoPrint's start and end scripts empty: OrcaSlicer's start and end G-code handle that.
- After print job is cancelled: paste in [`../gcode/octoprint-after-cancel.gcode`](../gcode/octoprint-after-cancel.gcode). It turns off the heaters and fan, lifts 10 mm and releases X, Y and E only, so the dual-Z gantry doesn't drop.

## Power (planned)

- Shelly Plus Plug on the printer, controlled from the Shelly app and from OctoPrint with PSU Control + the PSU Control - Shelly sub-plugin over the local network.
- In the Shelly settings, set power-on restore to Off, so the printer stays off after a power cut.

## To-Do: plugins

- [ ] Octolapse (start with a simple mode such as Smart or the stock defaults; the 3B is slow)
- [ ] TouchUI
- [ ] OctoEverywhere (or a similar remote-access plugin)
- [ ] SimplyPrint (the plugin on stock OctoPi, not the SimplyPrint image). It also does remote access, so it overlaps with OctoEverywhere: you may only need one
- [ ] CameraSettings
- [ ] Exclude Region
- [ ] PrettyGcode
- [ ] PSU Control + PSU Control - Shelly (once the plug arrives)

## To-Do: alternative plugins

Candidates to look at instead of, or alongside, the list above.

- [ ] UI Customizer: rearranges and themes the desktop web UI (column layout, hiding panels). It doesn't overlap with TouchUI, which is for phones and small screens.
- [ ] Dashboard: adds a tab with temperatures, progress, layer and fan info, plus the Pi's CPU load and temperature at a glance.
- [ ] Slicer Thumbnails: shows the slicer's embedded preview image in the file list and state panel. OrcaSlicer has to embed a thumbnail it can read (PNG is safest) next to the JPG used for the printer screen.
- [ ] Cancel Objects: cancels a single failed part in a multi-part print, using OrcaSlicer's object labels. It overlaps with Exclude Region, so you probably only need one.
- [ ] Print Time Genius: more accurate time estimates from analysing the G-code. The analysis is slow on a 3B, and OrcaSlicer's estimate may already be good enough.
- [ ] File Manager: a fuller file browser (move, copy, rename, folders) than the built-in one.
- [ ] OctoDash: not a plugin. It's a separate touchscreen app that runs on a display attached to the Pi. It's an alternative to TouchUI, which runs in a browser.
- [ ] Timelapse Purger: deletes old timelapses after a set number of days so the SD card doesn't fill up. Useful once Octolapse is running.
- [ ] Firmware Updater: flashes new firmware from OctoPrint. For this STM32 board it needs the Marlin binary file transfer method, so check the firmware supports that before relying on it. Flashing from the SD card still works as the fallback.
