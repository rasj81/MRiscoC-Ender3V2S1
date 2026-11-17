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
