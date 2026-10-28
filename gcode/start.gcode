; Printer start G-code for Orca Slicer / Bambu Studio (Ender 3 V2 + Sprite Pro + CR Touch, Marlin UBL)
; Paste into: Printer settings > Machine G-code > Machine start G-code.
; MERGED 2026-10-28: your original start sequence (heat, home, left-edge prime at X2, Z0.28, E10 passes)
; plus the saved-mesh reload, 3-point tilt and leveling activation. The original is in git history (534f7be).
; DRAFT: the merged file has not been run on the printer yet. Keep a hand on the power switch for the
; first G29 J. Items marked [measure] need a real-world check.
; Orca bed exclude area for the prime strip: 0x0,10x0,10x145,0x145

M413 S0                              ; power-loss recovery off (remove this line if you use it)
G90                                  ; absolute positioning
M83                                  ; relative extruder moves
M220 S100                            ; reset speed factor
M221 S100                            ; reset flow factor
M207 S0.8 F2100 Z0                   ; firmware retraction (G10): 0.8 mm at 35 mm/s, no firmware Z raise (the slicer handles Z hop). Overrides the firmware default of 5 mm / 40 mm/s / 0.2 mm raise
M208 S0 F2100                        ; firmware recover (G11): no extra length, 35 mm/s
M140 S[bed_temperature_initial_layer_single]   ; start heating the bed
M104 S150                            ; warm the nozzle only enough to soften ooze (original: prevent ooze during homing)
M190 S[bed_temperature_initial_layer_single]   ; wait for the bed; the mesh was built warm so probe warm
; Optional extra soak: G4 S180   [measure]

G28                                  ; home all axes
G29 L0                               ; reload saved mesh slot 0 every print so the tilt below never compounds
G29 J                                ; 3-point tilt of the saved mesh to today's bed level [measure: points reachable]
M420 S1 Z10                          ; activate leveling, 10 mm fade height
G1 Z10 F600                          ; move clear of the bed (original used Z50 at F240)

G1 X2 Y10 F3000                      ; original prime start, left edge (outside the probed mesh, so leveling is extrapolated here)
M104 S[nozzle_temperature_initial_layer]       ; final nozzle temperature
M109 S[nozzle_temperature_initial_layer]       ; wait for the nozzle
G1 Z0.28 F240                        ; original prime height
G92 E0
G1 Y140 E10 F1500                    ; prime pass 1 (original)
G1 X2.3 F5000                        ; step over 0.3 mm (original)
G92 E0
G1 Y10 E10 F1200                     ; prime pass 2 (original)
G92 E0
G1 Z2 F600                           ; lift so the first travel does not drag the prime line (added)
