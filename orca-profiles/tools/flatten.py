import json, glob, os, copy, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
U=os.path.join(ROOT,'user/default'); OUT=os.path.join(ROOT,'flattened')
idx={}  # (type,name)->(path,data)
def add(t,f,src):
    try: d=json.load(open(f))
    except Exception: return
    if isinstance(d,dict) and 'name' in d: idx.setdefault((t,d['name']),(f,d,src))
for t in ['machine','process','filament']:
    for f in glob.glob(f'{U}/{t}/*.json')+glob.glob(f'{U}/{t}/base/*.json'): add(t,f,'user')
    for f in glob.glob(f'{ROOT}/system/*/{t}/**/*.json',recursive=True): add(t,f,'system')
META={'inherits','from','name','print_settings_id','printer_settings_id','filament_settings_id','instantiation','setting_id','filament_id','base_id','type','include','is_custom_defined','renamed_from','description'}
def resolve(t,name,chain):
    f,d,src=idx[(t,name)]; chain.append(f'{name} [{src}]')
    base={}
    for inc in d.get('include',[]) or []:
        base.update(resolve(t,inc,chain))
    if d.get('inherits'): base.update(resolve(t,d['inherits'],chain))
    for k,v in d.items():
        if k in ('inherits','include'): continue
        base[k]=copy.deepcopy(v)
    return base
def flat(t,name):
    chain=[]; r=resolve(t,name,chain)
    for k in ['inherits','include','instantiation','setting_id','filament_id','base_id','type','is_custom_defined','renamed_from','description']: r.pop(k,None)
    r['name']=name; r['from']='User'; r['inherits']=''
    return r,chain
PRINTERS=["Creality Ender-3 V2 (Sprite Pro) 0.4 nozzle","Creality Ender-3 V2 (Sprite Pro, Fast) 0.4 nozzle"]
res={}
for p in PRINTERS:
    r,c=flat('machine',p); r['printer_settings_id']=p; res[('machine',p)]=(r,c)
std,c=flat('process','0.20mm Standard, Fast @Creality Creality Ender-3 V2 0.4 nozzle')
std['compatible_printers']=PRINTERS; std['compatible_printers_condition']=''
res[('process',std['name'])]=(std,c)
KEEP_PER_VARIANT=['layer_height','top_shell_layers','bottom_shell_layers']
for v in ['0.12mm Fine','0.15mm Optimal','0.24mm Draft']:
    vn=f'{v} @Creality Creality Ender-3 V2 0.4 nozzle'
    orig=idx[('process',vn)][1]
    r=copy.deepcopy(std)
    for k in KEEP_PER_VARIANT: r[k]=orig[k]
    r['name']=vn; r['print_settings_id']=vn
    res[('process',vn)]=(r,[f'synced from {std["name"]}; kept {KEEP_PER_VARIANT} from {vn}'])
for fl in ['Inland PLA+','Inland PETG+','DEEPLEE PLA Pro (Amazon)']:
    r,c=flat('filament',fl); r['filament_settings_id']=[fl]
    r['compatible_printers']=PRINTERS; r['compatible_printers_condition']=''
    res[('filament',fl)]=(r,c)
for (t,n),(r,c) in res.items():
    os.makedirs(f'{OUT}/{t}',exist_ok=True)
    with open(f'{OUT}/{t}/{n}.json','w') as fh: json.dump(dict(sorted(r.items())),fh,indent=4)
    with open(f'{OUT}/{t}/{n}.info','w') as fh: fh.write('sync_info = \nuser_id = \nsetting_id = \nbase_id = \nupdated_time = 0\n')
    print(t,'|',n,'| keys',len(r),'| chain:',' -> '.join(c))
