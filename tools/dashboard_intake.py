"""Private Dashboard intake receiver. Never builds or publishes content."""
import argparse
import json
import os
from pathlib import Path
import re
import uuid
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / '.local_data' / 'dashboard-intake'
def atomic(file, data):
    tmp = file.with_name(file.name + '.' + str(uuid.uuid4()) + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, file)
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('item_id')
    p.add_argument('--revision', type=int)
    p.add_argument('--stage', choices=['received', 'questions', 'draft', 'integrated'], default='received')
    p.add_argument('--question', action='append', default=[])
    p.add_argument('--manuscript', action='append', default=[], help='Existing .md relative to this private item directory')
    args = p.parse_args()
    if not re.fullmatch(r'[a-f0-9-]{36}', args.item_id): p.error('Invalid item ID')
    folder = INBOX / args.item_id
    versions = sorted(int(f.stem.split('-')[1]) for f in folder.glob('revision-*.json'))
    version = args.revision if args.revision is not None else max(versions, default=0)
    if version not in versions: p.error('No saved handoff at this revision')
    snapshot = json.loads((folder / f'revision-{version}.json').read_text(encoding='utf-8-sig'))
    if snapshot['itemId'] != args.item_id or snapshot['revision'] != version: p.error('Snapshot identity mismatch')
    status_file = folder / 'status.json'
    previous = json.loads(status_file.read_text(encoding='utf-8')) if status_file.exists() else {}
    if version < previous.get('receivedRevision', 0): p.error('Cannot regress received revision')
    refs = args.manuscript or previous.get('manuscriptRefs', [])
    for ref in refs:
        file = (ROOT / ref).resolve()
        if not (file.is_relative_to(folder.resolve()) or (file.is_relative_to((ROOT / 'trips').resolve()) and 'manuscripts' in file.relative_to(ROOT / 'trips').parts)) or file.suffix != '.md' or not file.is_file(): p.error('Manuscript must be existing private item .md')
    integrated = version if args.stage in ('draft', 'integrated') else previous.get('integratedRevision', 0)
    if args.stage in ('draft', 'integrated') and not refs: p.error('Draft/integrated requires a readable manuscript')
    status = dict(itemId=args.item_id, receivedRevision=version, integratedRevision=integrated, stage=args.stage, questions=args.question, manuscriptRefs=refs, updatedAt=datetime.now(timezone.utc).isoformat())
    atomic(status_file, status)
    print(json.dumps({'itemId':args.item_id,'revision':version,'stage':args.stage,'snapshot':str(folder / f'revision-{version}.json')},ensure_ascii=False))
if __name__ == '__main__': main()
