; Restore settings for the Ender 3 V2 (MRiscoC ProUI) after flashing a new build.
; Source: M503 output saved 2026-11-06 from the firmware that was running before the SPI-mode build.
; Usage: put this file on the printer's SD card, print it from the menu, then check with M503.
; Not included: the bed mesh (re-run leveling) and the C-lines M503 prints for settings that can't be set by G-code.

; Linear Units:
G21 ; (mm)
; Auto Temp Control:
M104 S0 B250 F0.00
; Temperature Units:
M149 C ; Units in Celsius
; Filament settings (Disabled):
M200 S0 D1.75
; Steps per unit:
M92 X80.00 Y80.00 Z400.00 E424.90
; Max feedrates (units/s):
M203 X500.00 Y500.00 Z10.00 E60.00
; Max Acceleration (units/s2):
M201 X500.00 Y500.00 Z500.00 E5000.00
; Acceleration (units/s2) (P<print-accel> R<retract-accel> T<travel-accel>):
M204 P500.00 R1000.00 T500.00
; Advanced (B<min_segment_time_us> S<min_feedrate> T<min_travel_feedrate> J<junc_dev>):
M205 B20000.00 S0.00 T0.00 J0.01
; Unified Bed Leveling:
M420 S0 Z10.00 ; Leveling OFF
; Material heatup parameters:
M145 S0 H195.00 B60.00 F128
M145 S1 H240.00 B90.00 F128
M145 S2 H230.00 B80.00 F128
M145 S3 H190.00 B50.00 F128
; Bed PID:
M304 P221.17 I43.20 D754.92
; Display Sleep:
M255 S5 ; (minutes)
; LCD Brightness:
M256 B127
; Power-loss recovery:
M413 S0 ; OFF
; Retract (S<length> F<feedrate> Z<lift>):
M207 S0.70 W13.00 F2100.00 Z0.00
; Recover (S<length> F<feedrate>):
M208 S0.00 W0.00 F2100.00 R480.00
; Homing Feedrate:
M210 X3000.00 Y3000.00 Z600.00
; Z-Probe Offset:
M851 X-31.20 Y-42.10 Z-2.85 ; (mm)
; Input Shaping:
M593 X F40.00 D0.15
M593 Y F40.00 D0.15
; Hotend Idle Timeout:
M86 B0 E0 S600 T170
; Linear Advance:
M900 K0.04
; Filament load/unload:
M603 L0.00 U100.00 ; (mm)
; Filament runout sensor:
M412 S0 D25.00 ; Sensor OFF
; Model predictive control:
M306 E0 P40.00 C8.84 R0.3167 A0.0559 F0.0584 H0.0056
; BLTouch HS mode (M401 only sets the mode on firmware that has HS mode; otherwise it deploys the probe, so stow it)
M401 S1 ; ON
M402 ; stow probe

; Save everything to the EEPROM
M500
