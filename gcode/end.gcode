; Printer end G-code for Orca Slicer / Bambu Studio (Ender 3 V2 + Sprite Pro, dual Z on one driver)
; Paste into: Printer settings > Machine G-code > Machine end G-code.
; MERGED 2026-10-28: Orca's original end sequence (lift above the print, present it at the front, raise the
; head, heaters/fan off, release X/Y/E) plus a 1.5 mm retract and nozzle-off right after the retract.
; The original is kept in gcode/original/end.gcode. DRAFT: not yet run on the printer.
; Needs Orca "Printable height" = 230 AND firmware Z max = 230 (the Z moves below are capped by printable_height).
; Needs "Relative extruder addressing" on in Orca (the start G-code sets M83).

M400                                 ; finish queued moves
G1 E-1.5 F2400                       ; retract 1.5 mm to stop stringing (added; kept at or below 2 mm to avoid pulling molten plastic into the cool zone)
M104 S0                              ; nozzle off now so it cools during the moves below (original: after them)
{if max_layer_z < printable_height}G1 Z{min(max_layer_z+2, printable_height)} F600 ; Move print head up{endif}
G1 X5 Y{print_bed_max[1]*0.8} F{travel_speed*60} ; present print
{if max_layer_z < printable_height-10}G1 Z{min(max_layer_z+70, printable_height-10)} F600 ; Move print head further up{endif}
{if max_layer_z < printable_height*0.6}G1 Z{printable_height*0.6} F600 ; Move print head further up{endif}
M140 S0                              ; turn off heatbed
M107                                 ; turn off fan
M84 X Y E                            ; disable X, Y, E only: Z stays locked so the dual-Z gantry does not drop
