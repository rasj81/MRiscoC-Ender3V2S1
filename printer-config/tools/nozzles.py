import json, os, math, copy
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C=os.path.join(ROOT,'clean/default'); OUT=os.path.join(ROOT,'nozzles/default')
INFO='sync_info = \nuser_id = \nsetting_id = \nbase_id = \nupdated_time = 0\n'
def w(t,n,d):
    os.makedirs(f'{OUT}/{t}',exist_ok=True)
    json.dump(dict(sorted(d.items())),open(f'{OUT}/{t}/{n}.json','w'),indent=4)
    open(f'{OUT}/{t}/{n}.info','w').write(INFO)
def f(x): return f'{round(x,3):g}'
BASES=["Creality Ender-3 V2 (Sprite Pro) 0.4 nozzle","Creality Ender-3 V2 (Sprite Pro, Fast) 0.4 nozzle"]
STD=json.load(open(f'{C}/process/0.20mm Standard, Fast @Creality Creality Ender-3 V2 0.4 nozzle.json'))
WIDTH_KEYS=[k for k,v in STD.items() if k.endswith('line_width') and not str(v).endswith('%')]
newprinters={}
for d in [0.2,0.6,0.8,1.0]:
    ds=f'{d:.1f}'; names=[]
    for b in BASES:
        m=json.load(open(f'{C}/machine/{b}.json'))
        n=b.replace('0.4 nozzle',f'{ds} nozzle'); names.append(n)
        m.update(name=n, printer_settings_id=n, printer_variant=ds,
                 nozzle_diameter=[ds], max_layer_height=[f(d*0.8)], min_layer_height=[f(d*0.25 if d>0.2 else 0.04)])
        newprinters[n]=m
    s=d/0.4
    for label,frac in [('Fine',0.3),('Optimal',0.375),('Standard',0.5),('Draft',0.6)]:
        lh=round(d*frac+1e-9,2)
        p=copy.deepcopy(STD)
        pn=f'{lh:.2f}mm {label}, Fast @Creality Creality Ender-3 V2 {ds} nozzle'
        for k in WIDTH_KEYS: p[k]=f(float(STD[k])*s)
        p.update(name=pn, print_settings_id=pn, layer_height=f(lh),
                 initial_layer_print_height=f(min(0.5,max(0.15,d*0.5))),
                 top_shell_layers=str(max(4,math.ceil(1.0/lh))), bottom_shell_layers=str(max(3,math.ceil(0.8/lh))),
                 support_top_z_distance=f(lh), support_bottom_z_distance=f(lh),
                 compatible_printers=names, compatible_printers_condition='')
        w('process',pn,p)
        if label=='Standard':
            for n in names: newprinters[n]['default_print_profile']=pn
        print(ds,label,'| lh',lh,'| line',p['line_width'],'| first',p['initial_layer_print_height'],'| shells',p['top_shell_layers'],p['bottom_shell_layers'])
for n,m in newprinters.items():
    w('machine',n,m); print('printer',n,m['nozzle_diameter'],m['min_layer_height'],m['max_layer_height'])
# filaments: make visible on all printers (full updated copies)
allp=BASES+list(newprinters)
for fl in ['Inland PLA+','Inland PETG+','DEEPLEE PLA Pro (Amazon)']:
    fd=json.load(open(f'{C}/filament/{fl}.json')); fd['compatible_printers']=allp; w('filament',fl,fd)
