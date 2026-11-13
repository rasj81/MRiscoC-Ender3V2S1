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
