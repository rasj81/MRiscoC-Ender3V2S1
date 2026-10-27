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
