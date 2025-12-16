import os
import json
import gzip
import hashlib
from pathlib import Path

ROOT = Path('.')
INDEX = ROOT / 'symbi-llm-repo' / 'index.jsonl'
CHUNKS = ROOT / 'symbi-llm-repo' / 'chunks'

def text_hash_for_doc(doc_id, num_chunks):
    h = hashlib.sha1()
    for i in range(num_chunks):
        p = CHUNKS / f'{doc_id}_{i}.txt.gz'
        if not p.exists():
            continue
        with gzip.open(p, 'rt', encoding='utf-8', errors='ignore') as f:
            for chunk in iter(lambda: f.read(8192), ''):
                if not chunk:
                    break
                h.update(chunk.encode('utf-8', errors='ignore'))
    return h.hexdigest()

def load_index():
    recs = []
    with INDEX.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                recs.append(json.loads(line))
            except Exception:
                continue
    return recs

def write_index(recs):
    tmp = INDEX.with_suffix('.jsonl.tmp')
    with tmp.open('w', encoding='utf-8') as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    backup = INDEX.with_suffix('.jsonl.bak')
    if backup.exists():
        backup.unlink()
    INDEX.rename(backup)
    tmp.rename(INDEX)

def delete_doc_chunks(doc_id, num_chunks):
    count = 0
    for i in range(num_chunks):
        p = CHUNKS / f'{doc_id}_{i}.txt.gz'
        if p.exists():
            p.unlink()
            count += 1
    return count

def main():
    recs = load_index()
    seen = {}
    keep = []
    removed = []
    for r in recs:
        sha1 = r.get('sha1')
        did = r.get('doc_id')
        n = r.get('num_chunks') or 0
        key = None
        if sha1:
            key = ('sha1', sha1)
        else:
            th = text_hash_for_doc(did, n)
            key = ('text', th)
        if key not in seen:
            seen[key] = r
            keep.append(r)
        else:
            removed.append(r)
    for r in removed:
        did = r.get('doc_id')
        n = r.get('num_chunks') or 0
        delete_doc_chunks(did, n)
    write_index(keep)
    print('Original index:', len(recs))
    print('Kept:', len(keep))
    print('Removed:', len(removed))

if __name__ == '__main__':
    main()

