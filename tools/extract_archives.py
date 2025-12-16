import os
import re
import sys
import json
import gzip
import hashlib
from datetime import datetime
from html import unescape

ARCHIVE_ROOT = os.path.abspath('.')
OUTPUT_ROOT = os.path.join(ARCHIVE_ROOT, 'symbi-llm-repo')
CHUNK_DIR = os.path.join(OUTPUT_ROOT, 'chunks')
INDEX_PATH = os.path.join(OUTPUT_ROOT, 'index.jsonl')

CHUNK_SIZE = 4000

def ensure_dirs():
    os.makedirs(CHUNK_DIR, exist_ok=True)

def read_text(path):
    try:
        with open(path, 'rb') as f:
            data = f.read()
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            text = data.decode('latin-1', errors='ignore')
        return text
    except Exception:
        return ''

def extract_html_text(html):
    if not html:
        return ''
    html = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<style[\s\S]*?</style>', '', html, flags=re.IGNORECASE)
    body_match = re.search(r'<body[\s\S]*?</body>', html, flags=re.IGNORECASE)
    if body_match:
        html = body_match.group(0)
    html = re.sub(r'<!--([\s\S]*?)-->', '', html)
    text = re.sub(r'<[^>]+>', '\n', html)
    text = unescape(text)
    text = re.sub(r'\r', '', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    text = text.strip()
    return text

def extract_title(html, fallback):
    if html:
        m = re.search(r'<title[^>]*>([\s\S]*?)</title>', html, flags=re.IGNORECASE)
        if m:
            t = unescape(m.group(1)).strip()
            if t:
                return t
    return fallback

def parse_date_from_name(name):
    m = re.search(r'(\d{1,2})_(\d{1,2})_(\d{4}).*?(\d{1,2})[：:](\d{2})[：:](\d{2})\s*([AP]M)?', name)
    if m:
        month, day, year, hour, minute, second, ampm = m.groups()
        h = int(hour)
        if ampm:
            if ampm == 'PM' and h != 12:
                h += 12
            if ampm == 'AM' and h == 12:
                h = 0
        try:
            dt = datetime(int(year), int(month), int(day), h, int(minute), int(second))
            return dt.isoformat()
        except Exception:
            return None
    m2 = re.search(r'(\d{4})-(\d{2})-(\d{2})', name)
    if m2:
        try:
            dt = datetime(int(m2.group(1)), int(m2.group(2)), int(m2.group(3)))
            return dt.isoformat()
        except Exception:
            return None
    return None

def sha1_file(path):
    h = hashlib.sha1()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def source_from_path(path):
    parts = os.path.normpath(path).split(os.sep)
    for p in parts:
        if p.lower() in ['claude', 'gpt 4.0', 'grok', 'symbi', 'deepseek']:
            if p.lower() == 'gpt 4.0':
                return 'GPT4'
            return p.capitalize() if p.lower() != 'deepseek' else 'DeepSeek'
    return 'Misc'

def chunk_and_write(doc_id, text):
    chunks = []
    n = 0
    i = 0
    while i < len(text):
        chunk = text[i:i+CHUNK_SIZE]
        chunk_path = os.path.join(CHUNK_DIR, f'{doc_id}_{n}.txt.gz')
        with gzip.open(chunk_path, 'wb') as gz:
            gz.write(chunk.encode('utf-8', errors='ignore'))
        chunks.append(chunk_path)
        n += 1
        i += CHUNK_SIZE
    return len(chunks)

def process_file(rel_path, index_f):
    abs_path = os.path.join(ARCHIVE_ROOT, rel_path)
    html = read_text(abs_path)
    title = extract_title(html, os.path.basename(rel_path))
    text = extract_html_text(html)
    stat = os.stat(abs_path)
    created = datetime.fromtimestamp(stat.st_mtime).isoformat()
    size = stat.st_size
    digest = sha1_file(abs_path)
    src = source_from_path(rel_path)
    doc_id = hashlib.sha1(rel_path.encode('utf-8')).hexdigest()[:16]
    num_chunks = chunk_and_write(doc_id, text)
    date_iso = parse_date_from_name(os.path.basename(rel_path))
    rec = {
        'doc_id': doc_id,
        'source': src,
        'rel_path': rel_path,
        'file_name': os.path.basename(rel_path),
        'title': title,
        'date_iso': date_iso,
        'created_at': created,
        'size_bytes': size,
        'sha1': digest,
        'num_chunks': num_chunks
    }
    index_f.write(json.dumps(rec, ensure_ascii=False) + '\n')

def process_deepseek(index_f):
    ds_path = os.path.join(ARCHIVE_ROOT, 'DeepSeek', 'conversations.json')
    if not os.path.exists(ds_path):
        return
    try:
        with open(ds_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        items = data if isinstance(data, list) else data.get('conversations') or data.get('data') or []
        for idx, item in enumerate(items):
            content = ''
            if isinstance(item, dict):
                msgs = item.get('messages') or item.get('conversation') or []
                if isinstance(msgs, list):
                    parts = []
                    for m in msgs:
                        if isinstance(m, dict):
                            role = m.get('role') or ''
                            txt = m.get('content') or m.get('text') or ''
                            parts.append(f'{role}: {txt}'.strip())
                    content = '\n\n'.join([p for p in parts if p])
                else:
                    content = json.dumps(item, ensure_ascii=False)
            elif isinstance(item, str):
                content = item
            else:
                content = json.dumps(item, ensure_ascii=False)
            doc_id = f'deepseek_{idx:04d}'
            num_chunks = chunk_and_write(doc_id, content)
            rec = {
                'doc_id': doc_id,
                'source': 'DeepSeek',
                'rel_path': 'DeepSeek/conversations.json',
                'file_name': 'conversations.json',
                'title': f'DeepSeek Conversation {idx}',
                'date_iso': None,
                'created_at': None,
                'size_bytes': None,
                'sha1': None,
                'num_chunks': num_chunks
            }
            index_f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    except Exception:
        return

def main():
    ensure_dirs()
    patterns = ('.html', '.htm', '.mhtml', '.webarchive')
    to_process = []
    for root, dirs, files in os.walk(ARCHIVE_ROOT):
        for name in files:
            lp = name.lower()
            if any(lp.endswith(p) for p in patterns):
                if '_files' in root:
                    continue
                rel = os.path.relpath(os.path.join(root, name), ARCHIVE_ROOT)
                to_process.append(rel)
    to_process.sort()
    with open(INDEX_PATH, 'w', encoding='utf-8') as index_f:
        for rel in to_process:
            process_file(rel, index_f)
        process_deepseek(index_f)
    print(f'Indexed {len(to_process)} files')

if __name__ == '__main__':
    main()

