#!/bin/bash
# Install patch-2 (FIFO) adxl345spi. Run with: sudo bash ~/adxl345spi-fix2/install.sh
set -euo pipefail
cd "$(dirname "$0")"
B=/usr/local/bin/adxl345spi
PATCH1_SHA=9afc73092d94a4f1f04ae9c3f7bcd1341ac901bcd0b84b5e15e19df9adb4e8b4
[ "$(id -u)" = 0 ] || { echo "Run with sudo." >&2; exit 1; }
[ -e "$B.orig" ] || { echo "Missing $B.orig (original backup); refusing." >&2; exit 1; }
if [ ! -e "$B.patch1" ]; then
    if [ "$(sha256sum "$B" | cut -d' ' -f1)" = "$PATCH1_SHA" ]; then
        cp -p "$B" "$B.patch1"
        echo "Saved current (patch 1) binary as $B.patch1"
    else
        echo "$B is not the expected patch-1 binary; not overwriting." >&2; exit 1
    fi
fi
install -o root -g root -m 755 ./adxl345spi "$B"
rm -f /dev/shm/shm_800.csv /dev/shm/shm_1600.csv /dev/shm/shm_3200.csv
"$B" -h | head -1
sha256sum "$B"
echo "Undo to patch 1:  sudo install -o root -g root -m 755 $B.patch1 $B"
echo "Undo to original: sudo install -o root -g root -m 755 $B.orig $B"
