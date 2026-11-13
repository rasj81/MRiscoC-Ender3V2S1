; OctoPrint "After print job is cancelled" script for this build.
; Paste into: OctoPrint Settings > GCODE Scripts > After print job is cancelled.
; Turns off the heaters and fan, lifts the nozzle 10 mm off the print, and releases X, Y and E.
M104 S0                              ; nozzle off
M140 S0                              ; bed off
M107                                 ; part fan off
G91                                  ; relative moves
G1 Z10 F600                          ; lift 10 mm off the print
G90                                  ; back to absolute moves
M84 X Y E                            ; disable X, Y, E only: Z stays locked so the dual-Z gantry does not drop
