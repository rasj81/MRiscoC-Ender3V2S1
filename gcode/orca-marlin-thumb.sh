#!/bin/sh
# Orca post-processing script: make Orca's JPG thumbnail readable by the Professional (ProUI) firmware.
# Orca writes the tag as "thumbnail_JPG"; the firmware looks for lowercase "thumbnail_jpg".
# Runs only on G-code sliced with G-code flavor = Marlin 2, so other profiles (Bambu, Klipper) are left alone.
# Orca passes the G-code file path as the first argument. Setup: docs/GCODE-PREVIEW.md
f="$1"
[ -f "$f" ] || exit 0
if grep -q '^; gcode_flavor = marlin2' "$f"; then
  # BSD (macOS) sed needs -i ''; GNU sed needs -i alone.
  if sed --version >/dev/null 2>&1; then
    sed -i 's/thumbnail_JPG/thumbnail_jpg/g' "$f"
  else
    sed -i '' 's/thumbnail_JPG/thumbnail_jpg/g' "$f"
  fi
fi
exit 0
