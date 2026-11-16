"""Bake ornate architectural modules as data-only components.

The collection keeps structural geometry separate from decoration. Recolouring
touches existing full cubes only; transparent foliage, stairs and guardrails
are not overwritten by a decorative surface pass.
"""
import argparse,hashlib,json,sys
from pathlib import Path
from itertools import product
ROOT=Path(__file__).resolve().parents[1]
def encode(v):return (json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')


def requests():
    ornament=lambda p,m:dict(profile=p,motif=m,density=100,scale=3,depth=1,border_layers=0,material='gold_block')
    return [
      ('ornate-pillar-corinthian','白金莨苕叶柱','pillar',[13,56,13],dict(material='quartz_block',accent='gold_block',form=dict(order='corinthian',capital_height=12,leaf_count=12,leaf_layers=3,flute_count=16,flute_depth=.75))),
      ('ornate-pillar-composite','黑金复合柱式','pillar',[15,64,15],dict(material='polished_blackstone_bricks',accent='gold_block',form=dict(order='composite',capital_height=12,leaf_count=12,leaf_layers=3,flute_count=16,flute_depth=.75,detail_material='gold_block'))),
      ('ornate-pillar-ionic','象牙蓝颈饰涡卷柱','pillar',[13,48,13],dict(material='smooth_quartz',accent='blue_concrete',form=dict(order='ionic',neck_pattern='egg_dart',detail_material='gold_block'))),
      ('ornate-stairs-ceremonial','镶嵌平台礼仪阶梯','stairs',[9,13,15],dict(material='smooth_quartz',accent='quartz_bricks',form=dict(profile='straight',rise=8,run_width=5,landing=3,tread='quartz_stairs',handrail=dict(style='horizontal',height=2,side='both')))),
      ('ornate-wall-vine','蓝金卷叶浮雕饰墙','wall',[29,23,5],dict(material='quartz_bricks',accent='blue_concrete',ornament={**ornament('art_nouveau','vine'),'depth':3,'scale':4,'border_layers':2})),
      ('ornate-wall-fan','黑金放射折线饰墙','wall',[29,23,5],dict(material='polished_blackstone_bricks',accent='gold_block',ornament={**ornament('art_deco','sunburst'),'depth':3,'scale':4,'border_layers':2})),
      ('ornate-ceiling-coffers','白金凹格宫廷藻井','ceiling',[27,7,27],dict(material='quartz_bricks',accent='gold_block',form=dict(profile='grid',drop=3,pitch=5),ornament={**ornament('classical','dentil'),'depth':2,'border_layers':2})),
      ('ornate-ceiling-lattice','蓝金格栅天花','ceiling',[27,7,27],dict(material='blue_concrete',accent='gold_block',form=dict(profile='grid',drop=3,pitch=5),ornament={**ornament('geometric','diamond'),'depth':2,'border_layers':2})),
      ('ornate-plant-vessel','花冠镶金陈设花器','plant',[9,15,9],dict(material='dark_oak_log',accent='quartz_bricks',foliage='flowering_azalea_leaves[persistent=true]',form=dict(profile='trailing',pot_height=5,crown_height=8,radius=3,density=100),ornament=ornament('art_nouveau','leaf'))),
      ('ornate-planter-gallery','金线连槽花廊','planter',[27,12,9],dict(material='dark_oak_log',accent='quartz_bricks',foliage='flowering_azalea_leaves[persistent=true]',form=dict(profile='upright',pot_height=4,crown_height=8,radius=3,density=100))),
      ('ornate-shelf-palace','镀金陈列书架','shelf',[15,19,7],dict(material='dark_oak_planks',accent='gold_block',spacing=4,ornament=ornament('gothic','pointed_arch'))),
      ('ornate-lantern-court','四盏花枝庭灯','lantern',[7,15,7],dict(material='polished_blackstone_bricks',accent='gold_block',style='stepped')),
      ('ornate-beam-dentil','齿饰金边檐梁','beam',[31,7,7],dict(material='quartz_bricks',accent='gold_block',form=dict(profile='braced',pitch=5),ornament=ornament('classical','dentil'))),
      ('ornate-arch-gilded','白金椭圆礼仪拱门','arch',[23,27,5],dict(material='quartz_bricks',accent='gold_block',form=dict(profile='round',border=2),ornament=ornament('classical','dentil'))),
      ('ornate-railing-frieze','宫廷横索栏片与雕饰下槛','railing',[25,3,3],dict(form=dict(profile='horizontal',pitch=4))),
    ]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--engine',type=Path,required=True);p.add_argument('--replace-draft',action='store_true')
    p.add_argument('--evidence-version',type=int,default=1);args=p.parse_args()
    engine=args.engine.resolve();sys.path.insert(0,str(engine/'scripts'))
    from nbt_structure_agent import dispatch,build
    from nbt_components import validate
    from nbt_collision import collision_cells
    from nbt_registry import effective
    from nbt_assembly import Volume
    from nbt_refine import save_master
    from PIL import Image,ImageDraw
    index=ROOT/'library.json';manifest=json.loads(index.read_text(encoding='utf8'));entries={r['id']:r for r in manifest['assets']}
    folder=ROOT/f'docs/previews/ornate-modules-v{args.evidence_version}'
    if (folder/'texture').exists():raise FileExistsError('Preserve reviewed captures; choose a new --evidence-version')
    folder.mkdir(parents=True,exist_ok=True);evidence=[]
    def publish(identifier,name,kind,size,blocks,parameters=None,anchor=None):
        palette=sorted(set(blocks.values()));ids={v:i for i,v in enumerate(palette)}
        data=validate(dict(schema_version=1,name=name,size=list(size),anchor=anchor or [size[0]//2,0,size[2]//2],
                 palette=palette,blocks=[[*pos,ids[value],False] for pos,value in blocks.items()],
                 tags=[kind,'ornate','authored'],review_status='pending_visual_review'))
        rel=f'assets/components/ornate/{identifier}.json';file=ROOT/rel;raw=encode(data)
        if file.exists() and file.read_bytes()!=raw and not args.replace_draft:raise FileExistsError(file)
        file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(raw)
        entries[identifier]=dict(id=identifier,name=name,type='component',category='华丽构件 · '+kind,
                 tags=[kind,'ornate'],status='recommended',path=rel,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        volume=Volume(size)
        for pos,value in blocks.items():volume.put(pos,value)
        source=folder/(identifier+'.master.json.gz');save_master(source,volume,set())
        evidence.append(dict(id=identifier,name=name,kind=kind,size=list(size),blocks=len(blocks),parameters=parameters,
                 content_sha256=data['content_sha256'],source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
    prepared=[]
    for identifier,name,kind,size,patch in requests():
        request=dict(kind=kind,size=size,name=name,**patch);result=dispatch(ROOT,'parametric_compile',request)
        prepared.append((identifier,name,kind,size,patch,request,result,build(ROOT,result['spec'])))
    for identifier,name,kind,size,patch,request,result,data in prepared:
        blocks={tuple(row[:3]):data['palette'][row[3]] for row in data['blocks']}
        solid=lambda value:collision_cells(value)[1] is None and len(collision_cells(value)[0])==8
        w,h,d=size
        if kind=='stairs':
            for x,y,z in result['construction']['walk_columns']:
                if solid(blocks[(x,y,z)]) and effective(blocks[(x,y,z)])[0]=='minecraft:smooth_quartz':
                    blocks[(x,y,z)]='gold_block' if (x+z)%4==0 else 'chiseled_quartz_block'
        if kind=='wall':
            from build_ornate_patterns import designs
            motif='scroll-leaf' if identifier.endswith('vine') else 'fan-sunburst'
            master=next(row for row in designs() if row['id']==motif)
            iw,ih=w-4,h-4;scale=20;mask=Image.new('L',(iw*scale,ih*scale),0);draw=ImageDraw.Draw(mask)
            for path in master['paths']:
                draw.line([(round(x/master['w']*iw*scale),round(y/master['h']*ih*scale)) for x,y in path],
                          fill=255,width=max(1,round(scale*1.1*min(iw/master['w'],ih/master['h']))),joint='curve')
            ink=mask.resize((iw,ih),Image.Resampling.LANCZOS)
            background='blue_concrete' if motif=='scroll-leaf' else 'polished_blackstone_bricks'
            blocks={(x,y,0):background for x,y in product(range(w),range(h))}
            for x,y in product(range(w),range(h)):
                edge=min(x,y,w-1-x,h-1-y)
                if edge==0:
                    for z in (1,2,3):blocks[(x,y,z)]='gold_block'
                elif edge==1:blocks[(x,y,1)]='chiseled_quartz_block'
                elif ink.getpixel((x-2,ih-1-(y-2)))>100:
                    blocks[(x,y,1)]='gold_block'
        if kind=='ceiling':
            for x,z in product(range(w),range(d)):blocks[(x,h-1,z)]='quartz_bricks'
        if kind in ('plant','planter'):
            pot=patch['form']['pot_height']
            for pos,value in list(blocks.items()):
                if pos[1]>=pot:blocks.pop(pos)
            centres=[w//2] if kind=='plant' else [4,w//2,w-5]
            cy=10 if kind=='plant' else 8;radius=3;cz=d//2
            for cx in centres:
                for y in range(pot,cy+1):blocks[(cx,y,cz)]='dark_oak_log[axis=y]'
                for x,y,z in product(range(w),range(max(pot,cy-radius),min(h,cy+radius+1)),range(d)):
                    if (x-cx)**2+(y-cy)**2+(z-cz)**2<=radius*radius:
                        blocks.setdefault((x,y,z),'flowering_azalea_leaves[persistent=true]')
            for pos,value in list(blocks.items()):
                x,y,z=pos
                if y>=pot or not solid(value) or effective(value)[0]=='minecraft:dirt':continue
                edge=min(x,z,w-1-x,d-1-z)==0
                if edge and (y==pot-1 or y in (1,2) and (x+z+y)%4<2):blocks[pos]='gold_block'
                elif edge and y==0:blocks[pos]='chiseled_quartz_block'
        if kind=='shelf':
            for level in range(1,h-2,4):
                for x in range(1,w-1):
                    pos=(x,level+1,d-2)
                    if pos not in blocks and (x,level,d-2) in blocks:blocks[pos]='bookshelf'
            for x in range(2,w-2,2):blocks[(x,h-1,0)]='chiseled_quartz_block'
        if kind=='lantern':
            for x,z in product((0,w-1),(0,d-1)):blocks[(x,h-2,z)]='lantern[hanging=true,waterlogged=false]'
        if kind=='railing':
            for x in range(w):blocks[(x,0,d//2)]='gold_block' if x%4==0 else 'chiseled_quartz_block'
        publish(identifier,name,kind,size,blocks,request)
    # A low table uses real half-slabs, preserving the inlaid top's plane.
    w,d=13,9;blocks={}
    for x,z in product(range(w),range(d)):
        edge=min(x,z,w-1-x,d-1-z)==0
        diamond=abs(x-w//2)+abs(z-d//2)
        material='waxed_cut_copper_slab' if edge or diamond in (2,4) else 'quartz_slab' if (x+z)%2 else 'polished_blackstone_slab'
        blocks[(x,1,z)]=material+'[type=bottom,waterlogged=false]'
    for x,z in product((0,w-1),(0,d-1)):blocks[(x,0,z)]='dark_oak_fence[north=false,east=false,south=false,west=false,waterlogged=false]'
    publish('ornate-table-inlaid','镶铜白石纹样长桌','table',[w,2,d],blocks)
    # A high-backed bench keeps its seat and back distinct; no floating plates.
    w,d=15,5;blocks={}
    for x,z in product(range(1,w-1),range(d-1)):blocks[(x,1,z)]='dark_oak_slab[type=bottom,waterlogged=false]'
    for x in range(w):
        for y in (1,2):blocks[(x,y,d-1)]='dark_oak_trapdoor[facing=south,half=bottom,open=true,powered=false,waterlogged=false]'
        blocks[(x,3,d-1)]='dark_oak_trapdoor[facing=north,half=bottom,open=false,powered=false,waterlogged=false]'
    for x in (0,w-1):
        for z in range(d):
            blocks[(x,0,z)]='dark_oak_fence[north=true,south=true,east=false,west=false,waterlogged=false]'
            blocks[(x,1,z)]='dark_oak_fence[north=true,south=true,east=false,west=false,waterlogged=false]'
            if z<d-1:blocks[(x,2,z)]='dark_oak_trapdoor[half=bottom,open=false,powered=false,waterlogged=false]'
        for y in (1,2):blocks[(x,y,d-1)]='chiseled_quartz_block' if y==1 else 'gold_block'
    publish('ornate-bench-highback','薄木花格高背长椅','bench',[w,4,d],blocks)
    # Separate the trusted engine's richly modelled Ionic capital and base as
    # reusable support pieces; do not invent a new collision certification.
    for identifier,name,kind,form,start,count in [
      ('ornate-bracket-volute','涡卷柱头承托块','bracket',dict(order='ionic',detail_material='gold_block'),40,8),
      ('ornate-pedestal-moulded','金线环带陈设基座','pedestal',dict(base_height=9,capital_height=3,base_profile='torus'),0,9)]:
        request=dict(kind='pillar',size=[13,48,13],material='smooth_quartz',accent='smooth_quartz',form=form)
        data=build(ROOT,dispatch(ROOT,'parametric_compile',request)['spec'])
        blocks={ (x,y-start,z):data['palette'][i] for x,y,z,i,_ in data['blocks'] if start<=y<start+count }
        if kind=='pedestal':
            for pos in blocks:
                if pos[1] in (1,7):blocks[pos]='gold_block'
        publish(identifier,name,kind,[13,count,13],blocks,request)
    # Hanging fixture: four real lanterns under connected golden arms.
    blocks={};cx=cz=4
    for y in range(3,8):blocks[(cx,y,cz)]='chain[axis=y,waterlogged=false]'
    for x in range(1,8):blocks[(x,3,cz)]='gold_block'
    for z in range(1,8):blocks[(cx,3,z)]='gold_block'
    for x,z in ((1,4),(7,4),(4,1),(4,7)):blocks[(x,2,z)]='lantern[hanging=true,waterlogged=false]'
    publish('ornate-lantern-chandelier','四臂金饰悬灯','lantern',[9,8,9],blocks,anchor=[4,7,4])
    latest=json.loads(index.read_text(encoding='utf8'))
    for r in latest['assets']:
        if r['id'] not in entries:entries[r['id']]=r
    latest['assets']=sorted(entries.values(),key=lambda r:r['id']);index.write_bytes(encode(latest))
    (folder/'generation.json').write_bytes(encode(dict(components=evidence,nbt_exported=False)))
    print(json.dumps(dict(components=len(evidence),assets=len(latest['assets'])),ensure_ascii=False))


if __name__=='__main__':main()
