; Printer start G-code for Orca Slicer / Bambu Studio (Ender 3 V2 + Sprite Pro + CR Touch, Marlin UBL)
; Paste into: Printer settings > Machine G-code > Machine start G-code.
; DRAFT 2026-10-27: not yet run on the printer. Test with the nozzle well above the bed
; (hand on the power switch) the first time. Items marked [measure] need a real-world check.
; Placeholders in [brackets] are Orca/Bambu Studio variables, filled in at slice time.

M413 S0                              ; power-loss recovery off (remove if you use it)
G90                                  ; absolute positioning
M83                                  ; relative extruder moves
M220 S100                            ; reset speed factor
M221 S100                            ; reset flow factor
M140 S[bed_temperature_initial_layer_single]   ; start heating the bed
M104 S150                            ; warm the nozzle only enough to soften ooze for probing
M190 S[bed_temperature_initial_layer_single]   ; wait for the bed
; Optional soak so the bed shape matches the saved mesh (the mesh was built warm): G4 S180   [measure]

G28                                  ; home all axes
G29 L0                               ; reload saved mesh slot 0 every print, so the tilt below never compounds
G29 J                                ; 3-point tilt: corrects the saved mesh for how the bed sits today [measure: confirm the probe points are reachable]
M420 S1 Z10                          ; activate leveling with 10 mm fade height

M109 S[nozzle_temperature_initial_layer]       ; heat the nozzle to printing temperature
G92 E0
G1 Z5 F600                           ; lift before travel
G1 X10 Y10 F5000                     ; purge line start (front-left, inside the 10 mm probe margin)
G1 Z0.3 F600
G1 X110 E10 F1200                    ; ~100 mm purge line, tuned for a 0.4 mm nozzle; change E for other nozzles [measure]
G1 Y12 F2000
G1 X10 E-0.8 F1200                   ; wipe back along the line
G1 Z5 F600
G92 E0
