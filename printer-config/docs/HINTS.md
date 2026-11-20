# 3D printing hints

Practical tips that apply to any printer. Add new ones as their own section.

## Assembling multi-piece prints with 3D Gloop

[3D Gloop!](https://www.3dgloop.com/) is a solvent-based adhesive made for 3D prints. It softens the plastic on both faces and cures into a chemical weld, which the maker says is usually stronger than the printed part. Source video: <https://youtube.com/shorts/pQyhVhQozbU>.

**Pick the matching formula.** There are separate versions for PLA, PETG/co-polyester ("PET") and ABS (the site also lumps ASA in with ABS). Use the one that matches the plastic. For our filaments: PLA Gloop for Inland PLA+ and DEEPLEE PLA Pro, PET Gloop for Inland PETG+.

**Design and slice for it.** Give the faces that will be glued solid material: at least 3 walls or 6 solid layers (about 1.2 mm) for functional parts, 2 walls or 4 layers for cosmetic ones. Flat, matching mating faces bond best, so split models on flat planes where you can.

**Steps (from the maker's fusing guide):**
1. Sand the mating faces lightly with 100 grit or coarser. It is optional, but it helps the Gloop bite and flattens the faces. If you skip it, use a bit more Gloop.
2. Brush a thin, even coat on **both** faces. Be generous, but don't flood it.
3. Press the parts together firmly by hand or with clamps. You only have a few seconds to adjust the position.
4. Wipe off squeeze-out right away with a cotton swab or paper towel.
5. Keep it clamped about 15 minutes (strong tack), and leave it at least 30 minutes before handling. Full strength takes about 24 hours. Gentle warmth speeds curing.

**Gluing two different plastics** (for example PLA to PETG): sand both faces hard with 60 to 80 grit to cut deep grooves, put the matching Gloop on each side, and clamp about 30 minutes. Expect a weaker bond and a longer cure.

**Safety.** It is a solvent: work with good ventilation (if you can smell it, you need more), keep it away from flames and sparks, wear gloves and keep it off bare skin, and don't use it inside a closed enclosure without a respirator. See the [health and safety page](https://www.3dgloop.com/health-and-safety).

**Storage.** Opened bottles are best used within 2 to 3 months. Unopened, stored cool (below 15 °C), they keep about a year.

*All figures above come from 3dgloop.com (fusing guide, FAQ and safety page), read 2026-11-16. They have not been tested on this printer yet.*

## Smooth top surfaces: slow the top surface speed

The single biggest lever for a smooth, glossy top skin is the **top surface speed**. A maker of printed patches and badges said in a TikTok video that their top surfaces went from visibly lined to smooth when they dropped the top surface speed from 200 mm/s to 50 mm/s, and left everything else alone. Fine layer lines still show up close, but the top reads as smooth. Source video: <https://www.tiktok.com/@thatmedicandrew/video/7707501628802207006>.

**Why it works.** The top layer bridges over sparse infill and is the one you look at. Printing it slowly gives the extruder time to keep pressure steady and lets each line settle and fuse with its neighbour before the next one arrives, so the lines merge instead of standing as ridges.

**Where to set it in Orca.** Process > Speed > *Top surface*. It only affects the topmost solid layers, so the cost in print time is small even when the rest of the print runs fast.

**Our profiles already follow this.** The "(Sprite Pro, Fast)" processes use 30 mm/s and the "(Sprite Pro, Turbo)" processes use 35 to 60 mm/s (lower on the larger nozzles). If a top still looks rough, check the slice preview first: a top speed that a custom process or an object override has raised is the usual cause. Beyond speed, the next things to try are a **monotonic** top surface pattern and **ironing** (see the ironing calibration to-do).

*From one creator's video (they did not name their printer or slicer), 2026-11-17. The numbers are theirs, not tested on this printer.*

## Sparse infill that doesn't stick: slow it down

Thin, sparse infill lines (low density, crosshatch, gyroid) are the first thing to delaminate or snap loose from the walls when they are printed fast. Each line only touches the layer below at a few points, so it needs time and heat to fuse there, and hard acceleration tugs the fresh line before it has set.

**What our profiles do (2026-11-18).** Sparse infill has its own, lower speed and acceleration:

| Set | Sparse infill speed | Sparse infill accel |
|---|---|---|
| (Sprite Pro, Fast) | 40 mm/s (was 50) | 1000 mm/s² (was 2000, the default) |
| (Sprite Pro, Turbo) | 0.2/0.4: 100, 0.6: 90, 0.8: 70, 1.0: 55 mm/s (was 100 to 200) | 2000 mm/s² (was 4000, the default) |

Solid infill, walls and travel are unchanged, so the cost is small: sparse infill is a minor share of most prints.

**Only below a certain density?** Orca has no setting that ties infill speed to infill density. The speed above applies to sparse infill at any density, which is fine because the problem is worst on sparse lines anyway. For a single part, use a modifier (right-click the object > Add modifier, then set Sparse infill speed on it), or make a copy of the process with a different speed.

**If it still doesn't stick, check these next:**
- **Temperature.** Go up 5 to 10 °C. Hotter plastic bonds to the layer below better, especially at speed.
- **Infill line width.** Wider infill (Quality > Line width > Sparse infill, e.g. 0.5 to 0.55 on a 0.4 nozzle) puts more plastic on each contact point.
- **Infill/wall overlap.** Ours is 23%. Raise it to 25 to 30% if the infill pulls away from the walls rather than from itself.
- **Combine infill.** Strength > Infill > *Infill combination* prints sparse infill every second layer at double height, which gives thicker, stronger lines (needs the layer height to be at most half the nozzle).
- **Pattern.** Crosshatch at 15% leaves long unsupported spans. Gyroid or grid at 15 to 20% bond more reliably.
- **Cooling.** Too much part fan on fast infill chills the line before it fuses; Orca's fan settings are in the filament profile.

## Magic number layer heights (multiples of 0.04 mm)

Pick layer heights that are whole multiples of the Z axis's full step. On the Ender-3 V2 (and Ender 3, CR-10, Geeetech A10) the Z motor is 1.8° (200 full steps per turn) on an 8 mm lead screw, so one full step is 8 / 200 = **0.04 mm**. Our firmware confirms it: 400 steps/mm at 16 microsteps. Source video: CHEP, "Better Quality 3D Prints Using MAGIC NUMBERS" <https://youtu.be/WIkT8asT90A>.

**Why it works.** Microsteps between full steps aren't evenly spaced. With a layer height like 0.10 or 0.15 each layer stops at a different microstep, so layers come out slightly thick and thin in turn. A multiple of 0.04 puts every layer on the same microstep, so the layers are even. The difference is small and mostly visible on fine detail under magnification, but it costs nothing, and 0.12 prints faster than 0.10 with the same look.

**Good values:** 0.04, 0.08, 0.12, 0.16, 0.20, 0.24, 0.28, 0.32 and so on. Stay at or below about 80% of the nozzle diameter (0.32 on a 0.4 nozzle). The first layer should be a multiple too.

**Where it's set.** All our Fast and Turbo processes use magic numbers since 2026-11-20 (`printer-config/tools/magic.py`; values in the orca-profiles README). Avoid Orca's variable (adaptive) layer height and *Precise Z height* when you want the benefit, because both produce in-between heights.

**Limits.** Our UBL mesh compensation fades out at 10 mm. Below that the firmware keeps nudging Z to follow the bed, so the benefit shows mainly above 10 mm. To check it on your own printer, print the same model at 0.15 and 0.16 and compare the walls under a magnifier.
