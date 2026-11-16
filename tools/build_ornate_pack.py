"""Author the ornate collection using an explicitly selected NBTCreator engine.

This is a maintainer tool, never an executable asset or an install hook.
Run with --engine <minecraft-nbt-modeler skill directory>. No NBT is exported.
"""
import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def encode(value):return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')


def window_recipes():
    rows=[]
    def add(identifier,name,size,profile,material,accent,**form):
        rows.append(dict(id=identifier,name=name,category='华丽窗框',tags=['frame','ornate','window',profile],
                    arguments=dict(kind='frame',size=size,name=name,material=material,accent=accent,
                                   form=dict(profile=profile,**form))))
    add('ornate-window-timber-four','四格木窗与前挑窗台',[7,7,4],'sash_window','stripped_spruce_log','spruce_planks',
        panes=[2,2],recess=2,sill_material='spruce_slab[type=top]')
    add('ornate-window-timber-twelve','十二格上下木窗',[10,13,4],'sash_window','stripped_dark_oak_log','dark_oak_planks',
        panes=[3,4],recess=2,sill_material='dark_oak_slab[type=top]')
    add('ornate-window-timber-sixteen','十六格高窗与双层窗扇',[13,13,4],'sash_window','stripped_dark_oak_log','dark_oak_planks',
        panes=[4,4],recess=2,sill_material='dark_oak_slab[type=top]')
    stone=dict(sill_material='smooth_sandstone_slab[type=top]',detail_material='chiseled_sandstone',recess=3)
    add('ornate-window-classical-cornice','齿饰檐口古典窗套',[13,21,4],'classical_window','smooth_sandstone','cut_sandstone',
        head='cornice',dentils=True,**stone)
    add('ornate-window-classical-pediment','三角山花与线脚窗套',[13,24,4],'classical_window','smooth_sandstone','cut_sandstone',
        head='triangular',dentils=True,**stone)
    add('ornate-window-classical-divided','山花分格宫廷窗',[17,29,4],'classical_window','smooth_sandstone','cut_sandstone',
        head='triangular',dentils=True,panes=[3,4],bar_material='dark_oak_planks',**stone)
    add('ornate-window-round-single','圆拱券与楔石窗',[15,23,4],'round_arch_window','smooth_sandstone','cut_sandstone',
        border=2,lights=1,recess=3,detail_material='chiseled_sandstone',sill_material='smooth_sandstone_slab[type=top]')
    add('ornate-window-round-twin','双光圆拱石窗',[15,23,4],'round_arch_window','smooth_quartz','quartz_bricks',
        border=2,lights=2,recess=3,sill_material='smooth_quartz_slab[type=top]',glass_palette=['light_blue_stained_glass','cyan_stained_glass'])
    add('ornate-window-gothic-clear','玫瑰与双尖拱窗棂',[19,27,4],'pointed_arch_window','smooth_sandstone','cut_sandstone',
        recess=2,sill_material='smooth_sandstone_slab[type=top]',glass_material='glass')
    add('ornate-window-gothic-lapis','蓝金彩玻玫瑰尖拱窗',[23,31,5],'pointed_arch_window','smooth_quartz','quartz_bricks',
        recess=3,sill_material='smooth_quartz_slab[type=top]',glass_palette=['blue_stained_glass','light_blue_stained_glass','yellow_stained_glass'])
    add('ornate-window-gothic-gilded','黑金玫瑰宫廷尖拱窗',[23,31,5],'pointed_arch_window','polished_blackstone_bricks','gold_block',
        recess=3,sill_material='polished_blackstone_slab[type=top]',glass_palette=['blue_stained_glass','cyan_stained_glass','yellow_stained_glass'])
    return rows


def register(entries,identifier,name,type,path,category,tags,**extra):
    raw=(ROOT/path).read_bytes()
    entry=dict(id=identifier,name=name,type=type,path=path,category=category,tags=tags,
               status='recommended',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),**extra)
    entries[identifier]=entry


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine',type=Path,required=True)
    parser.add_argument('--replace-draft',action='store_true',help='Replace only this tool\'s explicitly named, unpublished assets')
    args=parser.parse_args();engine=args.engine.resolve()
    sys.path.insert(0,str(engine/'scripts'))
    from nbt_structure_agent import dispatch,build
    from nbt_assembly import Volume
    from nbt_refine import save_master
    index=ROOT/'library.json';manifest=json.loads(index.read_text(encoding='utf8'))
    entries={row['id']:row for row in manifest['assets']};written=[]
    def write(path,value):
        file=(ROOT/path).resolve()
        if not file.is_relative_to(ROOT/'assets'):raise ValueError('Asset outside asset directory')
        raw=encode(value)
        if file.exists() and file.read_bytes()!=raw and not args.replace_draft:raise FileExistsError(file)
        file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(raw)
    snapshots=ROOT/'docs/previews/ornate-windows-v1'
    snapshots.mkdir(parents=True,exist_ok=True)
    for row in window_recipes():
        request=deepcopy(row['arguments'])
        compiled=dispatch(ROOT,'parametric_compile',request)
        component=build(ROOT,compiled['spec']);component['review_status']='pending_visual_review'
        identifier=row['id'];recipe_path=f'assets/recipes/frame/{identifier}.json'
        write(recipe_path,dict(schema_version=1,kind='nbtcreator.parametric-recipe',arguments=request,
                               controls=dict(style=False,spacing=False)))
        register(entries,identifier,row['name'],'parametric_recipe',recipe_path,row['category'],row['tags'])
        component_id=identifier+'-component';component_path=f'assets/components/windows/{component_id}.json'
        write(component_path,component)
        register(entries,component_id,row['name']+'（构件）','component',component_path,row['category'],row['tags'])
        model=Volume(component['size'])
        for x,y,z,value,_ in component['blocks']:model.put((x,y,z),component['palette'][value])
        save_master(snapshots/(identifier+'.master.json.gz'),model,set())
        written.append(dict(id=identifier,name=row['name'],size=model.size,blocks=len(model.blocks),
                            source_sha256=hashlib.sha256((snapshots/(identifier+'.master.json.gz')).read_bytes()).hexdigest(),
                            content_sha256=component['content_sha256'],parameters=request))
    # Merge the latest index rather than discarding assets added by another author.
    latest=json.loads(index.read_text(encoding='utf8'));old_ids={r['id'] for r in manifest['assets']}
    for row in latest['assets']:
        if row['id'] not in old_ids and row['id'] not in entries:entries[row['id']]=row
    latest['assets']=sorted(entries.values(),key=lambda row:row['id']);index.write_bytes(encode(latest))
    from nbt_modeling_session import engine_revision
    revision=hashlib.sha256(json.dumps(engine_revision(),sort_keys=True).encode()).hexdigest()
    (snapshots/'generation.json').write_bytes(encode(dict(windows=written,engine=engine.name,engine_revision_sha256=revision,nbt_exported=False)))
    print(json.dumps(dict(windows=len(written),assets=len(latest['assets']),output=str(ROOT)),ensure_ascii=False))


if __name__=='__main__':main()
