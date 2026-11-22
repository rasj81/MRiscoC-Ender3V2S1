# Accelerometer (Creality ADXL345 sensor on the OctoPi)

Plan for using Creality's "ADXL345 Vibration Compensation Sensor for Ender-3 V3 KE" (store page subtitle "Type C interface") as a removable input-shaping sensor on this Ender-3 V2, read by the Raspberry Pi 3B (OctoPi 64-bit) over SPI. The printer stays on Marlin. Not bought yet: researched 2026-11-21.

Status tags used below: **Verified** means an official Creality page or a photo of the actual board shows it. **Community** means one forum user reported it, not confirmed by Creality. **Inferred** means my reasoning from the ADXL345 datasheet or the Pi pinout, to check when the part arrives.

## What's in the box

- **Verified:** the kit is a small sensor board plus a separate cable. The sensor end of the cable is a **6-pin** connector; the other end is **USB-C**, which plugs into the back of the KE's Nebula screen ([Creality wiki install guide](https://wiki.creality.com/en/ender-series/ender-3-v3-ke/quick-start-guide/g-sensor%EF%BC%88vibration-compensation-sensor%EF%BC%89installation-and-operate-guide), step 4: "install the 6Pin port on the sensor port, and install the Type-C port ... on the back port of the Nebula screen").
- **Verified:** the replacement cable is Creality part 3103110632 ([Creality troubleshooting page](https://wiki.creality.com/en/3d-printer-accessories/troubleshooting/vibration-sensor-unable-to-recognize-when-it-connects-to-the-machine)).
- **Community (two sources):** the same sensor board was also sold for the Sonic Pad; the two versions "differ only in the cable" ([Creality forum](https://forum.creality.com/t/ender-3v3-ke-connection-g-sensor/4804)). The [Reddit guide](https://www.reddit.com/r/klippers/comments/1e5ocz5/guide_hooking_up_your_creality_adxl345gsensor_to/) agrees: the Sonic Pad cable ends in a **PS/2 plug (mini-DIN 6)**, the Nebula Pad (KE) cable in USB-C, and the two cables use different wire colors (see [Cable wire colors](#cable-wire-colors)).
- **The USB-C is not USB.** It carries the raw SPI bus. Nothing on the KE shows up as a USB device when the sensor is plugged in (Community: [Creality forum](https://forum.creality.com/t/ender-3-v3-ke-spi-and-gpio-on-nebula-pad-usb-c-connector/36565), [Klipper forum](https://klipper.discourse.group/t/ender-3v3-ke-adxl345-on-type-c/24773); the [Reddit guide](https://www.reddit.com/r/klippers/comments/1e5ocz5/guide_hooking_up_your_creality_adxl345gsensor_to/) author confirms in the comments that it has no USB chip, it is "just disguised as one" because of the Nebula's port). **Never plug the Creality cable into a real USB port** (the Pi, a Mac, a charger): VBUS is 5 V and the ADXL345 chip is rated 3.6 V max.

## Recommendation: skip the USB-C, cable from the 6-pin connector

The 6-pin end is labeled on a photo of the actual board, so a cable from the sensor's 6-pin socket straight to the Pi header avoids the unknown USB-C wiring entirely. Leave Creality's USB-C cable in the box (or keep it for a KE someday).

### Sensor 6-pin connector

From a photo of the board posted on the [Creality forum](https://forum.creality.com/t/ender-3-v3-ke-spi-and-gpio-on-nebula-pad-usb-c-connector/36565) (chip marked "345B", which is the ADXL345). Orientation: board flat, chip on the left, white connector on the right edge, mounting holes top and bottom. Pins listed top to bottom:

| Position (top to bottom) | Label | ADXL345 function | SPI role |
|---|---|---|---|
| 1 | SDO | SDO/ALT ADDRESS | MISO (sensor out) |
| 2 | SDA | SDA/SDI/SDIO | MOSI (sensor in) |
| 3 | VCC | supply | |
| 4 | GND | ground | |
| 5 | SCLK | SCL/SCLK | clock |
| 6 | CS | CS | chip select (low = SPI active) |

- **Verified (photo):** the labels and their order.
- **Community, confirms the photo:** the [Reddit guide](https://www.reddit.com/r/klippers/comments/1e5ocz5/guide_hooking_up_your_creality_adxl345gsensor_to/) lists the USB-C cable's wires in the same order, SDO, SDA, VCC, GND, SCL, CS (red to blue), so red is position 1 at the sensor end.
- **Inferred:** the connector is a JST-style 6-pin wire-to-board socket, but the pitch isn't stated anywhere. Measure it when it arrives (2.0 mm = JST-PH, 1.5 mm = ZH, 1.25 mm = GH) and buy the matching pre-crimped 6-pin pigtail. Easiest of all: cut Creality's cable in half and keep the 6-pin end, if you don't care about the USB-C end.
- **Verified (Klipper docs):** connect the ADXL345 to **3.3 V only**. Klipper warns that some boards have a level shifter, which makes 5 V dangerous for the Pi.
- **Community:** the [Reddit guide](https://www.reddit.com/r/klippers/comments/1e5ocz5/guide_hooking_up_your_creality_adxl345gsensor_to/) labels VCC as 3.3 V on both cable versions, and the author ran it from a Pi 4B's 3.3 V pin.
- **Inferred:** VCC should be **3.3 V**. The ADXL345 chip runs at 2.0 to 3.6 V, and the KE board is believed to be 3.3 V logic (Community, "I think" from the forum poster). I can't see a regulator on the photographed side, so do not feed 5 V. 3.3 V is safe whether or not there is a regulator.
- **Community:** the KE talks to it in **SPI mode 3** (`SPI_MODE3 // KE is mode 3` in the forum poster's working Arduino test). That matches the ADXL345 datasheet and Klipper's driver.
- **Not usable:** I2C. The pin labels are I2C-style (SDA/SCL), but the chip is wired for SPI here, CS is broken out, and Klipper's docs say I2C is too slow for resonance measurement anyway.

### Pi 3B header mapping (SPI0, CE0)

| Sensor pin | Pi physical pin | Pi signal |
|---|---|---|
| VCC | 1 | 3V3 |
| GND | 6 (or 9, 14, 20, 25) | GND |
| SDA (MOSI) | 19 | GPIO10 / SPI0 MOSI |
| SDO (MISO) | 21 | GPIO9 / SPI0 MISO |
| SCLK | 23 | GPIO11 / SPI0 SCLK |
| CS | 24 | GPIO8 / SPI0 CE0 |

- **Verified:** this is the standard Pi SPI0 mapping. It matches the table in the current [Klipper resonance doc](https://www.klipper3d.org/Measuring_Resonances.html) pin for pin (checked 2026-11-22) and [Creality's copy of it](https://github.com/CrealityOfficial/Ender-3_V3_KE_Klipper/blob/main/docs/Measuring_Resonances.md).
- **Recommended, compact block (Verified from the Reddit guide's photo of a working Pi 4B):** use the Pi's second 3.3 V pin and a nearby ground instead of pins 1 and 6. Then all six wires sit in header rows 9 to 12, and one **2x4 female Dupont housing over pins 17 to 24** (pins 18 and 22 left empty) plugs on in one go:

  | Sensor pin | Pi physical pin | Pi signal |
  |---|---|---|
  | VCC | 17 | 3V3 |
  | GND | 20 | GND |
  | SDA (MOSI) | 19 | GPIO10 / SPI0 MOSI |
  | SDO (MISO) | 21 | GPIO9 / SPI0 MISO |
  | SCLK | 23 | GPIO11 / SPI0 SCLK |
  | CS | 24 | GPIO8 / SPI0 CE0 |

  Pins 17 and 1 are both the Pi's 3.3 V rail, and 20 and 6 are both ground, so this is electrically the same as the Klipper table. The Pi 3B header is identical to the Pi 4B's.
- Either way, the Pi end should be a female Dupont housing so the cable unplugs at the Pi too.
- Cable: the sensor moves with the hotend (X) and the bed (Y), so use flexible stranded wire about 1 m long. Klipper recommends twisting pairs GND+MISO, 3.3V+MOSI, SCLK+CS (or a shielded Cat5e cable) to keep the SPI clean.
- **Ground loop warning (Klipper docs):** the Pi's ground is tied to the printer's mainboard through the OctoPrint USB cable, so the sensor's GND is effectively printer ground. Klipper says the sensor and the screws holding it must not touch any metal part of the printer, or a ground loop can damage the electronics. Use a printed bracket, and nylon screws or washers wherever a screw would reach the metal frame, hotend or bed.
- If a shielded Cat5e cable is used, connect the shield to the Pi's ground only, but connect the GND wire at both ends.

### Cable wire colors

From the [Reddit guide](https://www.reddit.com/r/klippers/comments/1e5ocz5/guide_hooking_up_your_creality_adxl345gsensor_to/) (2026-11-22, Community: one user's cables; text and photos sent by Richard). The author cut the USB-C end off, fitted a quick disconnect made of two 3-pin plugs (purple/red/orange in one, black/blue/yellow in the other), then put single Dupont pins on each wire into a Pi 4B.

| Signal | Pi pin (compact block) | USB-C cable (Nebula/KE) | PS/2 cable (Sonic Pad) |
|---|---|---|---|
| VCC 3.3 V | 17 (or 1) | purple | red |
| GND | 20 (or 6) | yellow | black |
| SDA (MOSI) | 19 | black | orange |
| SDO (MISO) | 21 | red | purple |
| SCL (SCLK) | 23 | orange | blue |
| CS | 24 | blue | yellow |

- **Verified (photo of the author's Pi 4B):** purple on pin 17, black 19, red 21, orange 23 along the inner row, yellow on 20 and blue on 24 on the board-edge row. That is exactly the compact block above, and it matches the colors in the guide's text.
- **Watch the colors:** red is VCC on the PS/2 cable but SDO on the USB-C cable, and black is GND on one and SDA on the other. Wire by this table (or by the board labels with a continuity check), never by "red = power".
- **Mini-DIN 6 pigtail plan:** the Sonic Pad version shows Creality itself uses a mini-DIN 6 (PS/2) plug on this sensor. If you buy the Sonic Pad cable, its PS/2 end can mate with a mini-DIN 6 socket pigtail on the Pi side. The guide gives wire colors only, not mini-DIN pin numbers, so map pins with a meter before wiring the Pi end. A generic PS/2 extension or keyboard pigtail has its own colors: go by mini-DIN pin numbers and continuity, not by colors.
- **Connector pitch, estimated from the guide's board photo (not measured):** using the ADXL345 chip (3 x 5 mm) for scale, the six contacts are about 1.25 to 1.5 mm apart, so the socket is most likely JST-GH (1.25 mm, latching) or ZH (1.5 mm), not PH (2.0 mm). The stock plug is a small white 6-pin housing. Measure before buying a pigtail.
- Still unknown: which USB-C contacts carry which wire (the guide gives colors only, so the Printables mapping below stays unverified).
- **From the guide's comments:** two people got `Invalid adxl345 id (got ff vs e5)`; the author's answer was wiring or wire order, checked with a meter from the sensor contacts to the Pi header. Another asked about a Pi Pico; the author says it runs on 3.3 V, so a Pico works too.

### Richard's plan: mini-DIN socket built into the Pi case (2026-11-22)

Keep the sensor's PS/2 (mini-DIN 6) cable whole, and build a short pigtail inside the Pi case: a panel-mount **mini-DIN 6 female socket** on the case wall, wired to a **2x4 female Dupont housing** that plugs onto Pi pins 17 to 24 (the compact block above). The sensor then plugs straight into the case and unplugs without touching the Pi header.

| Signal | PS/2 cable color (Sonic Pad version) | Mini-DIN socket pin | Pi pin |
|---|---|---|---|
| VCC 3.3 V | red | measure | 17 |
| SDA (MOSI) | orange | measure | 19 |
| GND | black | measure | 20 |
| SDO (MISO) | purple | measure | 21 |
| SCLK | blue | measure | 23 |
| CS | yellow | measure | 24 |

Pins 18 and 22 in the 2x4 housing stay empty.

- **Map the mini-DIN pins with a meter first.** The guide gives the cable's wire colors, not mini-DIN pin numbers, and those colors are for the one user's cable. Plug the sensor cable in, unplug the board end, and beep each wire from the 6-pin end (labels SDO, SDA, VCC, GND, SCLK, CS on the board) to each socket pin. Fill in the "Mini-DIN socket pin" column from that, then wire the pigtail by the socket's pin numbers, not by its wire colors (a pigtail's own colors won't match Creality's).
- Socket pin numbers are mirrored between the front of the socket and its solder side. Label the pins from the side you solder on, and check again after the socket is mounted.
- Test before the first measurement: with the pigtail on the Pi and the sensor plugged in, run the `0xE5` device ID read in [Testing the wiring](#testing-the-wiring-before-any-measuring).
- **Never plug this into a real PS/2 port** (an old PC or a KVM): PS/2 supplies 5 V on its power pin. Likewise never plug a keyboard or mouse into the case socket.
- The socket's metal shell is a path to ground. On a printed case it stays isolated, which is what the ground-loop warning above wants. Don't screw it to a metal panel that touches the printer frame.

## Fallback: building a USB-C breakout cable

Only if you want to keep the Creality cable whole and plug a USB-C breakout board into it. **Community, unverified:** a Printables mount page ([WMVos, model 713280](https://www.printables.com/model/713280-adxl345-alternate-y-axis-pcb-mount-ender-3-v3-seke); Printables blocked my fetch, this is from the search summary) gives:

| USB-C pin | ADXL345 signal |
|---|---|
| VBUS | VCC |
| GND | GND |
| D- | SDA (MOSI) |
| D+ | SDO (MISO) |
| CC | SCLK |
| SBU | CS |

The same page says the port is symmetrical, so either plug orientation works. Before trusting it, check with a multimeter in continuity mode from each pin of a USB-C breakout plugged into the cable to the 6-pin end. Use a breakout that exposes CC and SBU (most cheap "USB-C 2.0" breakouts only have VBUS, GND, D+ and D-), and don't add a USB-C extension cable in between: ordinary cables don't carry SBU straight through.

## Testing the wiring (before any measuring)

1. Enable SPI on the Pi: add `dtparam=spi=on` to `config.txt` on the boot partition (`/boot/firmware/config.txt` on newer OctoPi images, `/boot/config.txt` on older ones), then reboot. `ls /dev/spidev0.*` should list `spidev0.0`.
2. Read the device ID. The ADXL345 always answers `0xE5` to a read of register 0x00:

   ```bash
   sudo apt install -y python3-spidev
   python3 -c "import spidev; s=spidev.SpiDev(); s.open(0,0); s.mode=3; s.max_speed_hz=1000000; print(hex(s.xfer2([0x80,0])[1]))"
   ```

   `0xe5` means the wiring is right. `0x0` or `0xff` usually means SDA/SDO are swapped, CS isn't connected, or VCC is missing. At 3.3 V a swap won't damage anything; fix and retry.

## Using it with Marlin (no Klipper)

Marlin has no accelerometer support, so the sensor is only a measuring tool: the Pi records vibration while OctoPrint moves the axis, a script on the Pi or the Mac finds the resonance peak, and the result goes into Marlin's input shaper (`INPUT_SHAPING_X` and `_Y` are enabled in this firmware) as `M593 X F<Hz> D<damping>`, `M593 Y F<Hz> D<damping>`, `M500`. Marlin only has the ZV shaper, so use the peak frequency rather than Klipper's MZV/EI recommendation.

Candidate tools, to check when the part arrives (Inferred, not tested here):
- [`adxl345spi`](https://github.com/nagimov/adxl345spi): a small Pi program that samples an ADXL345 over SPI at up to 3200 Hz and writes CSV.
- Klipper's `scripts/calibrate_shaper.py` (from a Klipper checkout, no Klipper install needed) to turn the CSV into a frequency plot. It expects Klipper's CSV column format, so the recorder's output may need a header rewrite.
- A G-code sweep: short, fast back-and-forth moves on one axis at rising frequency, sent from OctoPrint while the recorder runs. This replaces Klipper's `TEST_RESONANCES`.

Klipper's own procedure, adapted (from the [Klipper resonance doc](https://www.klipper3d.org/Measuring_Resonances.html)):
- Turn all fans off during a measurement; noisy fans spoil the reading.
- This is a bed slinger, so it needs two mounts: measure X with the sensor on the extruder itself (not the carriage plate), then Y with it on the bed.
- Klipper's offline scripts work without a Klipper install. `scripts/graph_accelerometer.py` takes raw accelerometer CSVs (columns `#time,accel_x,accel_y,accel_z`), and `scripts/calibrate_shaper.py raw.csv -o x.png` prints a fitted ZV frequency and a suggested max accel for it. If the printer's corner speed differs from Klipper's default 5 mm/s, pass `--square_corner_velocity=`.
- The suggested max accel is a theoretical ceiling, not a target. Pick something below it and confirm with a test print.
- Don't measure often. The sweep shakes the printer hard near its resonances, so check that screws are still tight afterwards.

Ballpark for this build: a Klipper config for an Ender-3 V2 with a Sprite Pro ([davebl160389-ux on GitHub](https://github.com/davebl160389-ux/Ender-3-V2-Klipper-HIGHT-SPEED-Performance)) has MZV X 65.6 Hz and Y 47.5 Hz (commented out, from that person's printer, so only a sanity check for ours).

Until that's set up, the ringing tower in [PRINTER-SETTINGS.md](PRINTER-SETTINGS.md) remains the way to tune input shaping.

## Mounting

Creality's official X and Y brackets are on Creality Cloud (`vip.creality.com/en/goods-detail/2098`, sign-in required) and fit the KE's hotend and bed, not the V2 with a Sprite Pro. The sensor board mounts with two M3 screws (Creality uses M3x8 flat heads), so a clip-on bracket only needs two M3 holes at the board's hole spacing (measure it). Mount rigidly: a loose clip adds its own resonance and spoils the reading.

## Sources checked

- 2026-11-22: the [Reddit guide](https://www.reddit.com/r/klippers/comments/1e5ocz5/guide_hooking_up_your_creality_adxl345gsensor_to/) (text, photos and PDFs sent by Richard; Reddit itself is blocked for Claude). It confirms the 6-pin order, 3.3 V, the wire colors for both cables and the Pi header pins (compact block on pins 17 to 24). Its board photo suggests a 1.25 to 1.5 mm pitch, but doesn't settle it, nor the USB-C contact mapping.
- 2026-11-22: an r/ender3v2 post (text pasted by Richard) that only announces the davebl160389-ux high-speed repo (Sprite Pro, ADXL345, dual 5015 fans) and says to calibrate before copying its values. Nothing new on wiring. The repo uses a BTT ADXL345 over USB, not the Creality sensor.

## Open questions (check when it arrives)

- 6-pin connector pitch (photo estimate 1.25 to 1.5 mm) and board hole spacing.
- Check the wire colors on whichever cable arrives against the [Cable wire colors](#cable-wire-colors) table.
- Whether there's a regulator on the back of the board (doesn't change the plan: feed 3.3 V either way).
- Confirm the 6-pin label order against the photo, and the `0xE5` device ID read.
