"""Rebase preview source paths for publication while preserving render evidence."""
import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf8')


def verify(folder, snapshot, manifest):
    source = Path(manifest['source'])
    if not source.is_absolute(): source = folder / source
    source = source.resolve()
    if not source.is_relative_to(ROOT) or not source.is_file(): raise ValueError('Preview source must stay inside the asset repository')
    if manifest['source_sha256'] != sha(source) or snapshot['source_sha256'] != sha(source): raise ValueError('Preview source hash changed')
    if snapshot['geometry_sha256'] != manifest['geometry_sha256']: raise ValueError('Preview geometry binding changed')
    if manifest['snapshot_sha256'] != sha(folder / manifest['snapshot_file']): raise ValueError('Preview snapshot hash changed')
    if manifest['cameras_sha256'] != sha(folder.parent / 'cameras.json'): raise ValueError('Preview cameras changed')
    for image in manifest['images']:
        file = (folder / image['image']).resolve()
        if not file.is_relative_to(folder.resolve()) or sha(file) != image['sha256']: raise ValueError('Preview image hash changed')
    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'check'])
    args = parser.parse_args(); count = 0
    for file in sorted((ROOT / 'docs/previews').glob('*/texture/render_manifest.json')):
        folder = file.parent; manifest = json.loads(file.read_text(encoding='utf8'))
        snapshot_file = folder / manifest['snapshot_file']; snapshot = json.loads(snapshot_file.read_text(encoding='utf8'))
        source = verify(folder, snapshot, manifest)
        relative = Path(os.path.relpath(source, folder)).as_posix()
        if args.action == 'prepare' and (snapshot['source'] != relative or manifest['source'] != relative):
            original_snapshot = sha(snapshot_file); original_manifest = sha(file)
            snapshot['source'] = relative; snapshot_file.write_bytes(encode(snapshot))
            manifest['source'] = relative; manifest['snapshot_sha256'] = sha(snapshot_file)
            manifest['publication'] = dict(source_path_base='manifest_directory', source_path_rebased=True,
                original_snapshot_sha256=original_snapshot, original_render_manifest_sha256=original_manifest,
                images_and_geometry_unchanged=True)
            file.write_bytes(encode(manifest))
        if snapshot['source'] != relative or manifest['source'] != relative: raise ValueError('Preview contains an absolute or noncanonical source path; run prepare')
        verify(folder, snapshot, manifest); count += 1
    print(json.dumps(dict(passed=True, collections=count, action=args.action)))


if __name__ == '__main__': main()
