"""Build or verify library and registry hashes, using only Python's standard library."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def encode(data):
    return (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['index', 'check'])
    args = parser.parse_args()
    file = ROOT / 'library.json'
    original = file.read_bytes(); library = json.loads(original)
    assert library['kind'] == 'nbtcreator.asset-library' and library['schema_version'] == 1
    seen = set(); paths = set()
    for entry in library['assets']:
        path = (ROOT / entry['path']).resolve()
        assert path.is_relative_to(ROOT / 'assets') and path.suffix == '.json', 'Unsafe asset path'
        assert entry['id'] not in seen and entry['path'].casefold() not in paths, 'Duplicate asset'
        seen.add(entry['id']); paths.add(entry['path'].casefold())
        raw = path.read_bytes(); value = json.loads(raw)
        assert value['schema_version'] == 1
        if entry['type'] == 'parametric_recipe': assert value['kind'] == 'nbtcreator.parametric-recipe'
        elif entry['type'] != 'component': raise ValueError('Unsupported asset type')
        entry.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    assert paths == {p.relative_to(ROOT).as_posix().casefold() for p in (ROOT / 'assets').rglob('*.json')}, 'Unindexed assets'
    library['assets'].sort(key=lambda row: row['id'])
    updated = encode(library)
    registry = dict(schema_version=1, kind='nbtcreator.asset-registry', name='NBTCreator 拓展库清单', libraries=[dict(
        id=library['id'], name=library['name'], version=library['version'], path='library.json', manifest_sha256=hashlib.sha256(updated).hexdigest())])
    if args.action == 'check':
        assert updated == original, 'Asset hashes changed; run mise run index'
        assert (ROOT / 'registry.json').read_bytes() == encode(registry), 'Registry hash changed'
    else:
        file.write_bytes(updated); (ROOT / 'registry.json').write_bytes(encode(registry))
    print(json.dumps(dict(passed=True, assets=len(paths), version=library['version'])))


if __name__ == '__main__': main()
