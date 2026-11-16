"""Render real window assets using the selected engine; no GUI or NBT export."""
import argparse,hashlib,json,math,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def encode(value):return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--engine',type=Path,required=True)
    p.add_argument('--font',type=Path,default=Path('C:/Windows/Fonts/msyh.ttc'))
    p.add_argument('--font-bold',type=Path,default=Path('C:/Windows/Fonts/msyhbd.ttc'));args=p.parse_args()
    if not args.font.is_file():raise ValueError('Specify --font with an installed CJK TrueType font')
    engine=args.engine.resolve();sys.path.insert(0,str(engine/'scripts'))
    from nbt_assembly import Volume
    from nbt_refine import read_master,save_master
    from PIL import Image,ImageDraw,ImageFont
    folder=ROOT/'docs/previews/ornate-windows-v1'
    report=json.loads((folder/'generation.json').read_text(encoding='utf8'))
    rows=report['windows'];model=Volume((160,48,120));views=[]
    for i,row in enumerate(rows):
        source=folder/(row['id']+'.master.json.gz')
        if hashlib.sha256(source.read_bytes()).hexdigest()!=row['source_sha256']:raise ValueError('Source changed: '+row['id'])
        component,_=read_master(source);ox,oz=i%4*40,i//4*40
        for (x,y,z),value in component.blocks.items():model.put((x+ox,y,z+oz),value)
        points=list(component.blocks);lo=[min(p[j] for p in points) for j in range(3)];hi=[max(p[j] for p in points)+1 for j in range(3)]
        target=[(a+b)/2 for a,b in zip(lo,hi)];target[0]+=ox;target[2]+=oz
        radius=math.sqrt(sum((b-a)**2 for a,b in zip(lo,hi)))/2;distance=radius/math.sin(math.radians(21))*1.08
        az,el=math.radians(205),math.radians(10)
        direction=[math.sin(az)*math.cos(el),math.sin(el),math.cos(az)*math.cos(el)]
        cuts=[dict(axis='x',position=ox,removed_side='below'),dict(axis='x',position=ox+40,removed_side='above'),dict(axis='z',position=oz,removed_side='below'),dict(axis='z',position=oz+40,removed_side='above')]
        views.append(dict(id=row['id'],role=row['name'],eye=[v+d*distance for v,d in zip(target,direction)],target=target,fov=42,cuts=cuts))
    source=folder/'collection.master.json.gz';save_master(source,model,set());cameras=folder/'cameras.json';cameras.write_bytes(encode(views))
    output=folder/'texture'
    subprocess.run([sys.executable,'-B',str(engine/'scripts/nbt_task.py'),'render','--source',str(source),'--cameras',str(cameras),
                    '--output',str(output),'--width','960','--height','960','--quality','balanced'],check=True,cwd=ROOT)
    # Contact sheets only resize and label the original captures.
    family=[('timber','木窗分格与双层窗扇'),('classical','古典线脚、齿饰与山花'),('round','圆拱券与楔石'),('gothic','双尖拱、玫瑰窗棂与彩玻')]
    font_path=args.font;bold_path=args.font_bold if args.font_bold.is_file() else args.font
    font=lambda size,bold=False:ImageFont.truetype(str(bold_path if bold else font_path),size)
    def sheet(name,title,selected,cols,width=360,height=360):
        gap=16;head=112;cell=height+76
        image=Image.new('RGB',(48+cols*width+(cols-1)*gap,head+math.ceil(len(selected)/cols)*(cell+gap)+8),'#eef2f6');draw=ImageDraw.Draw(image)
        draw.text((24,20),title,font=font(30,True),fill='#1f2937')
        draw.text((24,65),'实际模型渲染；尺寸为设计空间，图中各款独立取景。',font=font(17),fill='#64748b')
        for i,row in enumerate(selected):
            x=24+i%cols*(width+gap);y=head+i//cols*(cell+gap)
            draw.rounded_rectangle((x,y,x+width,y+cell),radius=8,fill='white')
            im=Image.open(output/(row['id']+'.png')).convert('RGB').resize((width,height),Image.Resampling.LANCZOS);image.paste(im,(x,y))
            draw.text((x+12,y+height+10),row['name'],font=font(18,True),fill='#1f2937')
            draw.text((x+12,y+height+43),' × '.join(map(str,row['size']))+' 格',font=font(16),fill='#64748b')
        image.save(folder/name)
    sheet('all-windows.png','华丽窗框 · 十一款实际预览',rows,4)
    for key,title in family:
        selected=[r for r in rows if r['id'].startswith('ornate-window-'+key)]
        sheet(key+'-windows.png',title,selected,len(selected),420,420)
    print(json.dumps(dict(windows=len(rows),output=str(folder),nbt_exported=False),ensure_ascii=False))


if __name__=='__main__':main()
