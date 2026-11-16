"""Create original procedural ornament masters and corresponding voxel assets.

Masters are editable SVG and PNG attachments, not executable assets. Installable
JSON contains only validated component data. Reliefs are backed panels; floor
variants are flat, while ceiling variants mount by their solid upper plane.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
from itertools import product
ROOT=Path(__file__).resolve().parents[1]
def encode(v):return (json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')


def designs():
    rows=[]
    def add(id,name,w,h,paths):rows.append(dict(id=id,name=name,w=w,h=h,paths=paths))
    circle=lambda cx,cy,r:[(cx+r*math.cos(t*math.tau/240),cy+r*math.sin(t*math.tau/240)) for t in range(241)]
    cx=cy=15
    paths=[[(cx+(10+2*math.cos(8*a))*math.cos(a),cy+(10+2*math.cos(8*a))*math.sin(a)) for a in [t*math.tau/480 for t in range(481)]],circle(cx,cy,5)]
    for i in range(8):
        a=i*math.tau/8;paths.append([(cx+5*math.cos(a),cy+5*math.sin(a)),(cx+12*math.cos(a),cy+12*math.sin(a))])
    add('rosette-eight','八瓣花章浮雕',31,31,paths)
    paths=[[(15+12*math.sin(3*t),15+12*math.sin(4*t)) for t in [i*math.tau/720 for i in range(721)]],circle(15,15,3)]
    add('interlace-knot','连环交织结纹',31,31,paths)
    paths=[]
    for r in (9,18,27):paths.append([(15+r*math.cos(a),28-r*math.sin(a)) for a in [i*math.pi/120 for i in range(121)]])
    for i in range(13):
        a=i*math.pi/12;paths.append([(15+5*math.cos(a),28-5*math.sin(a)),(15+27*math.cos(a),28-27*math.sin(a))])
    add('fan-sunburst','扇形日轮饰板',31,31,paths)
    def bezier(points):
        return [tuple((1-t)**3*points[0][j]+3*(1-t)**2*t*points[1][j]+3*(1-t)*t*t*points[2][j]+t**3*points[3][j] for j in range(2)) for t in [i/160 for i in range(161)]]
    paths=[]
    for sign in (-1,1):
        paths.append(bezier([(15,28),(15+sign*14,26),(15+sign*12,9),(15,3)]))
        paths.append([(15+sign*(8-3*t)*math.cos(t*math.tau),15+(8-3*t)*math.sin(t*math.tau)) for t in [i/180 for i in range(181)]])
        for yy in (7,13,21):
            paths.append(bezier([(15+sign*3,yy+5),(15+sign*11,yy+3),(15+sign*8,yy-3),(15+sign*3,yy+5)]))
    paths.append(circle(15,15,3))
    add('scroll-leaf','对称卷叶浮雕',31,31,paths)
    paths=[[(0,11),(30,11)]]
    for centre in (5,15,25):
        for i in range(7):
            a=i*math.pi/6;paths.append([(centre,11),(centre+4*math.cos(a),11-8*math.sin(a))])
        paths.append([(centre+4*math.cos(a),11-8*math.sin(a)) for a in [i*math.pi/80 for i in range(81)]])
    add('palmette-frieze','棕叶连续饰带',31,13,paths)
    paths=[[(0,1),(30,1)],[(0,9),(30,9)]]
    for start in range(0,30,5):paths.append([(start,8),(start+4,8),(start+4,3),(start+1,3),(start+1,6),(start+3,6)])
    add('meander-frieze','回环折线边带',31,11,paths)
    points=[(15+(13 if i%2==0 else 6)*math.cos(i*math.pi/8),15+(13 if i%2==0 else 6)*math.sin(i*math.pi/8)) for i in range(17)]
    paths=[points,[(15,8),(22,15),(15,22),(8,15),(15,8)],circle(15,15,3)]
    for x,y in ((3,3),(27,3),(3,27),(27,27)):paths.append(circle(x,y,1.5))
    add('star-eight','八向星章镶饰',31,31,paths)
    paths=[circle(15,15,12),circle(15,15,9),circle(15,15,3)]
    for i in range(4):
        a=i*math.pi/2;paths.append([(15+9*math.cos(a)+4*math.cos(t),15+9*math.sin(a)+4*math.sin(t)) for t in [j*math.tau/120 for j in range(121)]])
    add('coffer-rosette','花环凹格章纹',31,31,paths)
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--engine',type=Path,required=True);p.add_argument('--replace-draft',action='store_true')
    p.add_argument('--evidence-version',type=int,default=1);args=p.parse_args()
    sys.path.insert(0,str(args.engine.resolve()/'scripts'))
    from PIL import Image,ImageDraw
    from nbt_components import validate
    from nbt_assembly import Volume
    from nbt_refine import save_master
    index=ROOT/'library.json';manifest=json.loads(index.read_text(encoding='utf8'));entries={r['id']:r for r in manifest['assets']}
    source=ROOT/'docs/pattern-masters';source.mkdir(parents=True,exist_ok=True)
    folder=ROOT/f'docs/previews/ornate-patterns-v{args.evidence_version}'
    if (folder/'texture').exists():raise FileExistsError('Preserve reviewed captures; choose a new --evidence-version')
    folder.mkdir(parents=True,exist_ok=True);reports=[]
    def publish(identifier,name,size,blocks,category,anchor,master):
        palette=sorted(set(blocks.values()));ids={v:i for i,v in enumerate(palette)}
        component=validate(dict(schema_version=1,name=name,size=size,anchor=anchor,palette=palette,
                  blocks=[[*p,ids[v],False] for p,v in blocks.items()],tags=['ornate','pattern',category],review_status='pending_visual_review'))
        rel=f'assets/components/patterns/{identifier}.json';file=ROOT/rel;raw=encode(component)
        if file.exists() and file.read_bytes()!=raw and not args.replace_draft:raise FileExistsError(file)
        file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(raw)
        entries[identifier]=dict(id=identifier,name=name,type='component',category='华丽纹样 · '+category,tags=['ornate','pattern',category],status='recommended',path=rel,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        volume=Volume(size)
        for p,v in blocks.items():volume.put(p,v)
        saved=folder/(identifier+'.master.json.gz');save_master(saved,volume,set())
        reports.append(dict(id=identifier,name=name,size=size,surface=category,master=master,blocks=len(blocks),content_sha256=component['content_sha256'],source_sha256=hashlib.sha256(saved.read_bytes()).hexdigest()))
    for row in designs():
        w,h=row['w'],row['h'];scale=20
        mask=Image.new('L',(w*scale,h*scale),0);draw=ImageDraw.Draw(mask)
        for path in row['paths']:draw.line([(round(x*scale),round(y*scale)) for x,y in path],fill=255,width=round(scale*1.1),joint='curve')
        draw.rectangle((scale,scale,(w-2)*scale,(h-2)*scale),outline=255,width=scale)
        small=mask.resize((w,h),Image.Resampling.LANCZOS)
        filled={(x,y) for x,y in product(range(w),range(h)) if small.getpixel((x,y))>100}
        # Keep the raised ivory boss within the actual gold relief, not in air.
        highlight={p for p in filled if h>=20 and 4<=(p[0]-w//2)**2+(p[1]-h//2)**2<=9}
        image=Image.new('RGB',mask.size,'#122866')
        layer=Image.new('RGB',mask.size,'#dcb247');image.paste(layer,(0,0),mask)
        image.save(source/(row['id']+'.png'))
        svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+str(w)+' '+str(h)+'">',f'<rect width="{w}" height="{h}" fill="#122866"/>']
        for path in row['paths']:svg.append('<polyline points="'+' '.join(f'{x:.4f},{y:.4f}' for x,y in path)+'" fill="none" stroke="#dcb247" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/>')
        svg.append(f'<rect x="1" y="1" width="{w-3}" height="{h-3}" fill="none" stroke="#dcb247" stroke-width="1"/>')
        svg+=['</svg>'];(source/(row['id']+'.svg')).write_text('\n'.join(svg)+'\n',encoding='utf8')
        blocks={(x,h-1-y,0):'blue_concrete' for x,y in product(range(w),range(h))}
        for x,y in filled:blocks[(x,h-1-y,1)]='gold_block'
        for x,y in highlight:blocks[(x,h-1-y,2)]='smooth_quartz'
        publish('ornate-pattern-'+row['id'],row['name'],[w,h,3],blocks,'relief',[w//2,0,0],row['id'])
        if row['id'] in ('rosette-eight','interlace-knot','star-eight','coffer-rosette'):
            floor={(x,0,y):'smooth_quartz' if (x,y) in highlight else 'gold_block' if (x,y) in filled else 'blue_concrete' for x,y in product(range(w),range(h))}
            publish('ornate-floor-'+row['id'],row['name']+' · 齐平镶地',[w,1,h],floor,'floor',[w//2,0,h//2],row['id'])
        if row['id'] in ('rosette-eight','coffer-rosette'):
            ceiling={(x,2-depth,z):v for (x,z,depth),v in blocks.items()}
            publish('ornate-ceiling-'+row['id'],row['name']+' · 顶部花章',[w,3,h],ceiling,'ceiling',[w//2,2,h//2],row['id'])
    latest=json.loads(index.read_text(encoding='utf8'))
    for r in latest['assets']:
        if r['id'] not in entries:entries[r['id']]=r
    latest['assets']=sorted(entries.values(),key=lambda r:r['id']);index.write_bytes(encode(latest))
    (folder/'generation.json').write_bytes(encode(dict(patterns=reports,masters_original=True,nbt_exported=False)))
    print(json.dumps(dict(components=len(reports),masters=8,assets=len(latest['assets'])),ensure_ascii=False))


if __name__=='__main__':main()
