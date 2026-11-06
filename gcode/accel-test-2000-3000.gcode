; Ender 3 V2 (Sprite Pro, direct drive): raise print and travel acceleration to a conservative test level.
; Print 2000, travel 3000, retract 1000 (unchanged). Max accel X/Y 3000 (already set), Z 500, E 5000 (unchanged).
; Why not higher: input shaping is still the untuned 40 Hz / 0.15 on both axes. Above about 2000-3000 a bed-slinger
; with an untuned shaper shows ringing (ghost ripples after corners), and the Y axis (moving bed) shows it first.
; Test with a small ringing tower or a sharp-cornered part. If you see ripples, run accel-baseline-500.gcode
; or lower the numbers (try P1500 T2500). After tuning input shaping per axis, re-test and raise in steps.
; Usage: put on the printer's SD card, print it from the menu, check with M503.

M201 X3000 Y3000 Z500 E5000 ; max acceleration (X/Y 3000)
M204 P2000 R1000 T3000      ; print / retract / travel acceleration
M500                         ; save to EEPROM
