"""Render baked modules or patterns and produce labelled comparison sheets."""
import argparse,hashlib,json,math,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def encode(v):return (json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--engine',type=Path,required=True)
    p.add_argument('--collection',choices=['modules','patterns'],required=True)
    p.add_argument('--evidence-version',type=int,default=1)
    p.add_argument('--font',type=Path,default=Path('C:/Windows/Fonts/msyh.ttc'))
    p.add_argument('--font-bold',type=Path,default=Path('C:/Windows/Fonts/msyhbd.ttc'))
    args=p.parse_args();engine=args.engine.resolve();sys.path.insert(0,str(engine/'scripts'))
    if not args.font.is_file():raise ValueError('Specify --font with an installed CJK TrueType font')
    from PIL import Image,ImageDraw,ImageFont
    from nbt_assembly import Volume
    from nbt_refine import read_master,save_master
    folder=ROOT/('docs/previews/ornate-'+args.collection+'-v'+str(args.evidence_version))
    report=json.loads((folder/'generation.json').read_text(encoding='utf8'))
    rows=report['components' if args.collection=='modules' else 'patterns']
    model=Volume((192,max(r['size'][1] for r in rows),math.ceil(len(rows)/4)*48));views=[]
    for i,row in enumerate(rows):
        source=folder/(row['id']+'.master.json.gz')
        if hashlib.sha256(source.read_bytes()).hexdigest()!=row['source_sha256']:raise ValueError('Source changed: '+row['id'])
        source_model,_=read_master(source);ox,oz=i%4*48,i//4*48
        for (x,y,z),value in source_model.blocks.items():model.put((x+ox,y,z+oz),value)
        points=list(source_model.blocks);lo=[min(p[j] for p in points) for j in range(3)];hi=[max(p[j] for p in points)+1 for j in range(3)]
        target=[(a+b)/2 for a,b in zip(lo,hi)];target[0]+=ox;target[2]+=oz
        extent=[b-a for a,b in zip(lo,hi)];distance=math.sqrt(sum(v*v for v in extent))/2/math.sin(math.radians(21))*1.08
        kind=row.get('kind',row.get('surface'))
        az=210 if kind in ('bench','shelf') else 35
        el=-45 if kind=='ceiling' else 60 if kind=='floor' else 28 if kind=='table' else 10 if kind=='pillar' else 20
        if row['id']=='ornate-lantern-chandelier':el=-15
        a,e=math.radians(az),math.radians(el);direction=[math.sin(a)*math.cos(e),math.sin(e),math.cos(a)*math.cos(e)]
        cuts=[dict(axis='x',position=ox,removed_side='below'),dict(axis='x',position=ox+48,removed_side='above'),dict(axis='z',position=oz,removed_side='below'),dict(axis='z',position=oz+48,removed_side='above')]
        views.append(dict(id=row['id'],role=row['name'],eye=[v+d*distance for v,d in zip(target,direction)],target=target,fov=42,cuts=cuts))
    source=folder/'collection.master.json.gz';save_master(source,model,set());cameras=folder/'cameras.json';cameras.write_bytes(encode(views))
    output=folder/'texture'
    subprocess.run([sys.executable,'-B',str(engine/'scripts/nbt_task.py'),'render','--source',str(source),'--cameras',str(cameras),
                    '--output',str(output),'--width','960','--height','960','--quality','balanced'],check=True,cwd=ROOT)
    font=lambda n,b=False:ImageFont.truetype(str(args.font_bold if b and args.font_bold.is_file() else args.font),n)
    def sheet(name,title,selected,cols=4,width=360,height=360):
        gap=16;head=112;cell=height+76
        canvas=Image.new('RGB',(48+cols*width+(cols-1)*gap,head+math.ceil(len(selected)/cols)*(cell+gap)+8),'#eef2f6');draw=ImageDraw.Draw(canvas)
        draw.text((24,20),title,font=font(29,True),fill='#1f2937')
        draw.text((24,65),'实际资产模型渲染；每款独立取景，不以图片生成代替游戏验收。',font=font(17),fill='#64748b')
        for i,row in enumerate(selected):
            x=24+i%cols*(width+gap);y=head+i//cols*(cell+gap)
            draw.rounded_rectangle((x,y,x+width,y+cell),radius=8,fill='white')
            im=Image.open(output/(row['id']+'.png')).convert('RGB').resize((width,height),Image.Resampling.LANCZOS);canvas.paste(im,(x,y))
            draw.text((x+12,y+height+10),row['name'],font=font(18,True),fill='#1f2937')
            draw.text((x+12,y+height+43),' × '.join(map(str,row['size']))+' 格',font=font(16),fill='#64748b')
        canvas.save(folder/name)
    sheet('all-'+args.collection+'.png','华丽构件 · 二十款' if args.collection=='modules' else '纹样、镶地与顶部花章',rows)
    if args.collection=='modules':
        sheet('architectural.png','柱式、檐梁、承托、台阶与拱门',[r for r in rows if r['kind'] in ('pillar','stairs','beam','bracket','arch','pedestal')],3,420,420)
        sheet('furnishings.png','陈设、花器与灯具',[r for r in rows if r['kind'] in ('table','bench','shelf','plant','planter','lantern')],3,420,420)
    else:
        for category,title in [('relief','八款原创浮雕纹样'),('floor','齐平镶地纹样'),('ceiling','顶部花章')]:
            selected=[r for r in rows if r['surface']==category]
            sheet(category+'.png',title,selected,min(4,len(selected)),420,420)
    print(json.dumps(dict(collection=args.collection,images=len(rows),output=str(folder)),ensure_ascii=False))


if __name__=='__main__':main()
