#!/usr/bin/env python3
"""
SYMBI-Archives Analysis Tool
Reads and analyzes conversations to extract story arcs, core ideas, and unique solutions
"""

import json
import gzip
import os
from collections import defaultdict

def load_index(index_path='index.jsonl'):
    """Load the index file"""
    docs = []
    with open(index_path, 'r') as f:
        for line in f:
            docs.append(json.loads(line))
    return docs

def read_chunk(doc_id, chunk_id, chunks_dir='chunks'):
    """Read a specific chunk file"""
    chunk_path = os.path.join(chunks_dir, f'{doc_id}_{chunk_id}.txt.gz')
    if os.path.exists(chunk_path):
        with gzip.open(chunk_path, 'rt', encoding='utf-8') as f:
            return f.read()
    return None

def read_document_chunks(doc_id, num_chunks, chunks_dir='chunks'):
    """Read all chunks for a document"""
    chunks = []
    for i in range(num_chunks):
        chunk = read_chunk(doc_id, i, chunks_dir)
        if chunk:
            chunks.append(chunk)
    return chunks

def analyze_conversation(docs, target_doc_id):
    """Analyze a specific conversation by doc_id"""
    for doc in docs:
        if doc['doc_id'] == target_doc_id:
            print(f"\n{'='*80}")
            print(f"Document: {doc.get('title', 'No title')}")
            print(f"Source: {doc.get('source', 'Unknown')}")
            print(f"Chunks: {doc.get('num_chunks', 0)}")
            print(f"{'='*80}\n")
            
            chunks = read_document_chunks(doc['doc_id'], doc.get('num_chunks', 0))
            if chunks:
                # Combine first and last chunks for overview
                if len(chunks) > 0:
                    print("--- FIRST CHUNK ---")
                    print(chunks[0][:2000])
                    print("\n... (truncated) ...\n")
                
                if len(chunks) > 1:
                    print("--- LAST CHUNK ---")
                    print(chunks[-1][-2000:])
            return doc
    return None

def main():
    # Load index
    docs = load_index()
    print(f"Loaded {len(docs)} documents from index")
    
    # Group by source
    by_source = defaultdict(list)
    for doc in docs:
        by_source[doc['source']].append(doc)
    
    print("\nDocuments by source:")
    for source, docs_list in sorted(by_source.items()):
        print(f"  {source}: {len(docs_list)} docs")
    
    return docs, by_source

if __name__ == '__main__':
    docs, by_source = main()