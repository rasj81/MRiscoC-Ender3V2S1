# adxl345spi patch for the Pinput Shaping plugin (2026-11-25)

The OctoPrint plugin [Pinput Shaping](https://github.com/navaismo/Octoprint-Pinput_Shaping) records the ADXL345 with a small C program, `adxl345spi`, that its installer builds from [navaismo/adxl345spi](https://github.com/navaismo/adxl345spi) pinned at commit `13487d93e9cdd5a1f95386ac77badcc5da444b8a` (`bash/Octo-deps-install-ADXLSPI.sh` in the plugin). The stock program could not produce a capture the plugin would accept on this OctoPi (Pi 3B, 32-bit, `10.0.0.251`), so it was patched twice. This folder holds the working version.

## Files

| File | What it is |
|---|---|
| `adxl345spi.c` | Patch 2 source, version string `0.4-fifo1`. This is what runs on the Pi now. |
| `upstream-to-patch2.diff` | Patch 2 against the pinned upstream commit. |
| `upstream-to-patch1.diff` | Patch 1 (the one-line `flushEvery` change) against upstream, for the record. |
| `install.sh` | Installs a built patch 2 binary over `/usr/local/bin/adxl345spi`, keeping backups. |

All four were copied from `~/adxl345spi-fix2/` on the Pi (patch 1 diff made from `~/adxl345spi-fix/`, an upstream clone at the pinned commit). Nothing on the Pi was changed while saving them.

## Why it had to change

Every capture failed in the plugin at every rate (800, 1600 and 3200 Hz) with "Capture has excessive timestamp jitter or missing sample intervals".

The cause: in save mode the stock program polls the sensor in a busy loop, buffers 1000 samples (`flushEvery = 1000`), then stops sampling to `fprintf` all 1000 rows and `fflush`. That stall is about 5.6 ms, which is 4 to 18 missed samples every 1000, depending on rate. The plugin checks the time column for even spacing, so the gaps fail it.

**Patch 1** set `flushEvery` to 16 (a sed one-liner). Shorter stalls helped, but random SD-card write pauses on the Pi still failed some captures.

**Patch 2** rewrites save mode for the sensor's native rates (3200, 1600, 800, 400, 200, 100, 50, 25 Hz):

- The ADXL345 samples on its own clock into its 32-sample FIFO (stream mode). The Pi drains the FIFO every 2 ms or less, so a host stall shorter than the FIFO depth (10 ms at 3200 Hz) loses nothing.
- Each sample is timestamped as `index / rate`, so the time column is evenly spaced.
- A separate writer thread formats and writes rows from a 65536-sample ring buffer, so file I/O never blocks sampling. The sampling loop asks for real-time priority (harmless if refused).
- If the FIFO ever overflows, the index skips ahead by the estimated loss so the gap shows in the data instead of being hidden, and a warning goes to stderr.
- Command-line options (`-s`, `-f`, `-t`) and the CSV format (`time,x,y,z`) are unchanged, so the plugin needs no change. Non-native rates and the no-save console mode still use the old path (with patch 1's `flushEvery = 16`).

Result: six 25 s captures passed the plugin's check at 800, 1600 and 3200 Hz.

## Rebuild and install (on the Pi)

The plugin's installer had already put the build tools and `pigpio` on the Pi, and set `dtparam=spi=on` in `/boot/firmware/config.txt` (reboot after that the first time). Running the plugin's installer on OctoPi also needed a workaround for OctoPi's git root guard; that detail is from the install session and was not rechecked when writing this note.

```bash
mkdir -p ~/adxl345spi-fix2 && cd ~/adxl345spi-fix2
# copy adxl345spi.c and install.sh from this folder here, then:
gcc -Wall -pthread adxl345spi.c -L /usr/local/include -lpigpio -lrt -o adxl345spi
sudo bash ~/adxl345spi-fix2/install.sh
```

The compile line is the upstream Makefile's. `install.sh` refuses to run unless the original backup `/usr/local/bin/adxl345spi.orig` exists, and on its first run it saves the patch 1 binary as `/usr/local/bin/adxl345spi.patch1` (only if its checksum matches the known patch 1 build). It then installs the new binary, clears stale `/dev/shm/shm_*.csv` captures, and prints the version and checksum.

If the plugin is reinstalled or updated, its installer rebuilds stock upstream over `/usr/local/bin/adxl345spi`, so this has to be redone. Check with `/usr/local/bin/adxl345spi -h | head -1`: it should say `version 0.4-fifo1`.

Checksums on the Pi as of 2026-11-25 (sha256):

| Binary | sha256 |
|---|---|
| `/usr/local/bin/adxl345spi` (patch 2) | `79771c51c5d8243123f25fb2e328a6e9eeb8cea7b7336102371f26baa81b19cb` |
| `/usr/local/bin/adxl345spi.patch1` | `9afc73092d94a4f1f04ae9c3f7bcd1341ac901bcd0b84b5e15e19df9adb4e8b4` |
| `/usr/local/bin/adxl345spi.orig` (stock plugin build) | `c9f543620d48b3e10f5148df3fac04f352c4d73011ef6a3c622dc6e02af741b0` |

## Revert

```bash
sudo install -o root -g root -m 755 /usr/local/bin/adxl345spi.patch1 /usr/local/bin/adxl345spi
```

```bash
sudo install -o root -g root -m 755 /usr/local/bin/adxl345spi.orig /usr/local/bin/adxl345spi
```

The first goes back to patch 1, the second to the stock plugin build.

## The sensor clock runs 2.7% slow

Captures hold 97.3% of the samples expected for their length: the ADXL345's own oscillator runs slow. Patch 2 timestamps from the sample count, so the plugin sees time 2.7% stretched and reports every frequency 2.7% high.

- Multiply the plugin's frequencies by 0.973 before using them.
- Do not press the plugin's Apply button: it sends the uncorrected values to the printer.
- Set the shaper by hand from the OctoPrint terminal with `M593`, then `M500` to save.

## Results, 2026-11-25

| Axis | Plugin peak | Corrected (x 0.973) | Set in Marlin (ZV) | Damping |
|---|---|---|---|---|
| X | 48.4 Hz | 47.1 Hz | 54 Hz | 0.05 |
| Y | 35.9 Hz | 34.9 Hz | 35 Hz | 0.05 |

Before: 40 Hz and damping 0.15 on both axes (untuned). The values were set as `M593 X F54 D0.05`, `M593 Y F35 D0.05`, `M500`; the M503 capture after the tune is [`../m503/M503-20261125-1834.txt`](../m503/M503-20261125-1834.txt).
