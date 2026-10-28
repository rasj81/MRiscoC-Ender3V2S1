; Original Gcode
G90 ; use absolute coordinates
M83 ; extruder relative mode
M140 S[bed_temperature_initial_layer] ; set final bed temp
M104 S150 ; set temporary nozzle temp to prevent oozing during homing
G4 S10 ; allow partial nozzle warmup
G28 ; home all axis
G1 Z50 F240
G1 X2 Y10 F3000
M104 S[nozzle_temperature_initial_layer] ; set final nozzle temp
M190 S[bed_temperature_initial_layer] ; wait for bed temp to stabilize
M109 S[nozzle_temperature_initial_layer] ; wait for nozzle temp to stabilize
G1 Z0.28 F240
G92 E0
G1 Y140 E10 F1500 ; prime the nozzle
G1 X2.3 F5000
G92 E0
G1 Y10 E10 F1200 ; prime the nozzle
G92 E0



; Printer end G-code for Orca Slicer / Bambu Studio (Ender 3 V2 + Sprite Pro, dual Z on one driver)
; Paste into: Printer settings > Machine G-code > Machine end G-code.
; DRAFT 2026-10-27: not yet run on the printer.

M400                                 ; finish queued moves
G91                                  ; relative positioning
G1 E-2 F2400                         ; retract to stop stringing
G1 Z10 F600                          ; lift 10 mm (relative, so it cannot crash into the part)
G90
G1 X10 Y200 F5000                    ; park at the back-left, clear of the part (keep inside your Y limit)
M104 S0                              ; nozzle off
M140 S0                              ; bed off
M107                                 ; fan off
M84 X Y E                            ; release X, Y, E only: Z stays locked so the dual-Z gantry does not drop
