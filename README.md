LLM-ready Symbi Archives

Structure:
- `index.jsonl`: one JSON per document with metadata
- `chunks/`: gzipped text-only chunks named `{doc_id}_{chunk_id}.txt.gz`

Index fields:
- `doc_id`: unique ID
- `source`: top-level source (Claude, GPT4, Grok, SYMBI, DeepSeek)
- `rel_path`: path relative to archive root or synthetic for DeepSeek
- `file_name`: original file name
- `title`: best-effort title
- `date_iso`: parsed from filename when present
- `created_at`: filesystem mtime ISO
- `size_bytes`: original file size
- `sha1`: digest of original file
- `num_chunks`: count of chunks

Chunking:
- Fixed-size character chunks for broad LLM compatibility
- Default: 4000 characters per chunk

Usage:
- Read `index.jsonl` to enumerate docs; load `chunks/{doc_id}_{i}.txt.gz`
- Metadata enables filtering by source/date and deduping

Deduplication:
- Run `python3 tools/dedupe_repo.py` to remove duplicates and rewrite `index.jsonl`
- Duplicates are detected via original `sha1` when available, else by full text hash

Distribution:
- Create a single release artifact: `python3 tools/pack_release.py` → `symbi-llm-repo.tar.gz`
- Publish the tarball as a GitHub Release asset for lightweight cloning
