#!/usr/bin/env python3
"""Move every Orca process onto "magic number" layer heights (multiples of 0.04 mm).

The Ender-3 V2 Z axis is a 1.8 deg motor on an 8 mm lead screw: 400 steps/mm, so one
full step is 0.04 mm. Layer heights that are whole multiples of it put every layer on
the same microstep, which gives evenly sized layers (CHEP "Magic Numbers" video).

Usage:  python3 tools/magic.py <orca dir> [--dry-run]
  <orca dir> holds machine/ and process/, e.g. E3V2-SpritePro-Wifi/orca-profiles
  or Orca's user/default folder. Works on the Fast and Turbo sets alike: renames the
  process presets (.json and .info), sets layer height, first layer, shell counts,
  and fixes each printer's minimum layer height and default process.
"""
import json, math, os, re, sys

LAYERS = {  # nozzle: Fine, Optimal, Standard, Draft (all multiples of 0.04, max 80 % of nozzle)
    '0.2': (0.04, 0.08, 0.12, 0.16),
    '0.4': (0.12, 0.16, 0.20, 0.24),
    '0.6': (0.16, 0.24, 0.28, 0.36),
    '0.8': (0.24, 0.32, 0.40, 0.48),
    '1.0': (0.32, 0.36, 0.48, 0.60),
}
FIRST = {'0.2': 0.16, '0.4': 0.20, '0.6': 0.28, '0.8': 0.40, '1.0': 0.48}
MIN_LAYER = {'0.2': 0.04, '0.4': 0.08, '0.6': 0.16, '0.8': 0.20, '1.0': 0.24}
LABELS = ('Fine', 'Optimal', 'Standard', 'Draft')
NAME = re.compile(r'^(\d\.\d\d)mm (Fine|Optimal|Standard|Draft) @(.*\(Sprite Pro, (?:Fast|Turbo)\)) (\d\.\d) nozzle$')

def g(x): return f'{round(x, 3):g}'
def load(p): return json.load(open(p))
def save(p, d):
    with open(p, 'w') as f: json.dump(d, f, indent=4)

root = sys.argv[1]; dry = '--dry-run' in sys.argv
renames = {}
pdir = os.path.join(root, 'process')
for fn in sorted(os.listdir(pdir)):
    if not fn.endswith('.json'): continue
    m = NAME.match(fn[:-5])
    if not m: continue
    old_lh, label, printer, noz = float(m[1]), m[2], m[3], m[4]
    lh = LAYERS[noz][LABELS.index(label)]
    new = f'{lh:.2f}mm {label} @{printer} {noz} nozzle'
    p = load(os.path.join(pdir, fn))
    assert abs(float(p['layer_height']) - old_lh) < 1e-6, fn
    top = int(p['top_shell_layers']); bot = int(p['bottom_shell_layers'])
    p.update(name=new, print_settings_id=new, layer_height=g(lh),
             initial_layer_print_height=g(FIRST[noz]),
             top_shell_layers=str(max(3, math.ceil(top * old_lh / lh - 1e-6))),
             bottom_shell_layers=str(max(3, math.ceil(bot * old_lh / lh - 1e-6))))
    for k in ('support_top_z_distance', 'support_bottom_z_distance'):
        if k in p and abs(float(p[k]) - old_lh) < 1e-6: p[k] = g(lh)
    renames[fn[:-5]] = new
    print(f'{fn[:-5]:70} -> {lh:.2f} first {FIRST[noz]} shells {top}/{bot} -> {p["top_shell_layers"]}/{p["bottom_shell_layers"]}')
    if dry: continue
    save(os.path.join(pdir, fn), p)
    if new != fn[:-5]:
        for ext in ('.json', '.info'):
            src = os.path.join(pdir, fn[:-5] + ext)
            if os.path.exists(src): os.rename(src, os.path.join(pdir, new + ext))

mdir = os.path.join(root, 'machine')
for fn in sorted(os.listdir(mdir)):
    if not fn.endswith('.json') or '(Sprite Pro, ' not in fn: continue
    d = load(os.path.join(mdir, fn)); noz = re.search(r'(\d\.\d) nozzle', fn)[1]
    before = (d.get('min_layer_height'), d.get('default_print_profile'))
    d['min_layer_height'] = [g(MIN_LAYER[noz])]
    if d.get('default_print_profile') in renames: d['default_print_profile'] = renames[d['default_print_profile']]
    print(f'{fn[:-5]:60} min {before[0]} -> {d["min_layer_height"]} | default {d["default_print_profile"]}')
    if not dry: save(os.path.join(mdir, fn), d)
