; Ender 3 V2: put acceleration back to the safe baseline (what the printer ran before the speed tests).
; Max accel X/Y 3000 stays (it is only a ceiling); print and travel go back to 500, retract 1000.
; Usage: put on the printer's SD card, print it from the menu, check with M503.

M201 X3000 Y3000 Z500 E5000
M204 P500 R1000 T500
M500
