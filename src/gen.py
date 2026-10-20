import json,re,os
L=open('src/castle.dat').read().split('\n')
sd=open('src/castle.sd7').read()
names={int(n):k for k,n in re.findall(r'const integer: (\w+)\s+is\s+(\d+);',sd) if k not in('NO_ROOM','MAX_ROOM','ROOM_LINES','ROOM_COLUMNS','INVENTORY_LINE','MAX_STRENGTH','MAX_INVENTORY','PIXMAP_SIZE','STEP_SIZE','BORDER_DIST','LEGEND_YPOS_MIN')}
const={k:int(n) for n,k in names.items()}
D=['north','south','east','west','up','down']
rooms={};i=0
for r in range(1,86):
    grid=L[i:i+18];i+=18
    desc=[x for x in L[i:i+5]];i+=5
    ex=list(map(int,L[i].split()));i+=1
    rooms[r]=dict(grid=grid,desc=' '.join(d.strip() for d in desc if d.strip()),exits={D[k]:v for k,v in enumerate(ex) if v})
items=re.findall(r'initItem\((\w+),\s*"([^"]+)",\s*\w+,\s*(\d+),\s*(\d+),\s*(\w+)\);\s*(?:# (\w+))?',sd)
mons=re.findall(r'initMonster\((\w+),\s*"([^"]*)",\s*"([^"]*)",\s*\w+,\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\w+)\);',sd)
TRE=['CROWN','DIAMOND','FANCY_GOBLET','GOLDBAR','HARP','HOLY_CROSS','HOURGLASS','JADE_FIGURINE','LARGE_GEM','NECKLACE','RUBYS','SCEPTER','SILVER_BARS']
hidden={'BOOK':'on shelves; revealed by look/take shelves','GLASSES':'on desk; look/take desk','KEY':'on desk; look/take desk','WINE_FLASK':'on desk; look/take desk','LARGE_GEM':'in fountain; take fountain (hint: look fountain from Balcony)','NECKLACE':'worn by statue ($); take statue'}
out=[]
for r,d in rooms.items():
    nm=names.get(r)
    it=[dict(item=n,name=nn,row=int(l),col=int(c),treasure=n in TRE,**({'hidden':hidden[n]} if n in hidden else {})) for n,nn,l,c,rm,cm in items if const.get(rm if rm!='NO_ROOM' else cm)==r]
    mo=[dict(monster=m,name=(a+' '+n).strip(),row=int(l),col=int(c),attack=int(at),strength=int(s)) for m,a,n,l,c,at,s,rm in mons if const.get(rm)==r]
    feats=sorted({ {'U':'stairs up','D':'stairs down','=':'gate','$':'statue','?':'fountain','~':'water','{':'chains','+':'small bush','*':'big bush','@':'wood furniture (desk/shelves/barrels/table)','%':'stone table/throne','|':'mirror/balcony edge','>':'railing','K':'K wall letter','B':'B wall letter',':':'colored wall',';':'colored wall'}[ch] for row in d['grid'] for ch in row if ch in 'UD=$?~{+*@%|>KB:;'} | ({'bed'} if any(ch in '][_^WRNPY' for row in d['grid'] for ch in row) else set()))
    out.append(dict(id=r,const=nm,description=d['desc'],exits=d['exits'],items=it,monsters=mo,features=feats,source='Seed7 castle.dat + castle.sd7 (github.com/ThomasMertes/seed7/prg)'))
os.makedirs('game/data/rooms_layout',exist_ok=True)
json.dump(dict(legend="exits use room ids; 0/absent = none. rows/cols 1-based on 18x24 grid. 84=ESCAPED (win), 85=CASTLE pseudo-room.",rooms=out),open('game/data/rooms.json','w'),indent=1)
for o,(r,d) in zip(out,rooms.items()):
    g=[row.ljust(24) for row in d['grid']]
    for m in o['monsters']:
        s=list(g[m['row']-1]);s[m['col']-1]='M';g[m['row']-1]=''.join(s)
    open(f"game/data/rooms_layout/room_{r:02d}.txt",'w').write(f"Room {r} {o['const'] or ''}\n{o['description']}\nExits: {o['exits']}\n+{'-'*24}+\n"+''.join('|'+x+'|\n' for x in g)+f"+{'-'*24}+\nItems(lowercase letter a=Book..v=Silver Bars): {[(x['name'],x['row'],x['col']) for x in o['items']]}\nMonsters(M): {[(x['name'],x['row'],x['col']) for x in o['monsters']]}\n")
gv=['digraph C{rankdir=LR;node[shape=box,fontsize=9,style=filled,fillcolor=white];']
for o in out:
    lab=f"{o['id']}\\n{(o['const'] or o['description'][:22]).replace(chr(34),'')}"
    col='gold' if any(x['treasure'] for x in o['items']) else ('salmon' if o['monsters'] else 'white')
    gv.append(f'r{o["id"]}[label="{lab}",fillcolor={col}];')
seen=set()
for o in out:
    for dn,t in o['exits'].items():
        back=any(v==o['id'] for v in rooms[t]['exits'].values())
        k=tuple(sorted((o['id'],t)))
        if back and k in seen: continue
        seen.add(k)
        gv.append(f'r{o["id"]}->r{t}[label="{dn[0].upper() if dn not in("up","down") else dn}",fontsize=7{",dir=both" if back else ""}];')
gv.append('}');open('game/data/map.dot','w').write('\n'.join(gv))
print(len(out))
