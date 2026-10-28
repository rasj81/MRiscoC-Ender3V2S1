; Original End Gcode from Orca
{if max_layer_z < printable_height}G1 Z{min(max_layer_z+2, printable_height)} F600 ; Move print head up{endif}
G1 X5 Y{print_bed_max[1]*0.8} F{travel_speed*60} ; present print
{if max_layer_z < printable_height-10}G1 Z{min(max_layer_z+70, printable_height-10)} F600 ; Move print head further up{endif}
{if max_layer_z < printable_height*0.6}G1 Z{printable_height*0.6} F600 ; Move print head further up{endif}
M140 S0 ; turn off heatbed
M104 S0 ; turn off temperature
M107 ; turn off fan
M84 X Y E ; disable motors

; Printer end G-code for Orca Slicer / Bambu Studio (Ender 3 V2 + Sprite Pro, dual Z on one driver)
; Paste into: Printer settings > Machine G-code > Machine end G-code.
; DRAFT 2026-10-27: not yet run on the printer. (2026-10-28: the original start sequence that was pasted
; here is now merged into gcode/start.gcode.)

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
