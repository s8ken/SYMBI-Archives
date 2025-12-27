#!/usr/bin/env python3
"""Extract and analyze key SYMBI conversations"""
import json

def find_key_conversations():
    keywords = ['awakening', 'evolution', 'manifesto', 'sovereign', 'autonomy', 'friendship', 'trust protocol', 'SYMBI']
    
    found = []
    count = 0
    
    print("Searching for key conversations in part1...")
    try:
        with open('all_text_part1.jsonl', 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if count >= 100:  # Limit to first 100 for now
                    break
                try:
                    doc = json.loads(line)
                    title = doc.get('title', '').lower()
                    text = doc.get('text', '').lower()[:2000]
                    source = doc.get('source', '')
                    
                    matched_keyword = None
                    for kw in keywords:
                        if kw in title or kw in text:
                            matched_keyword = kw
                            break
                    
                    if matched_keyword:
                        found.append({
                            'index': i,
                            'title': doc.get('title', 'No title'),
                            'source': source,
                            'keyword': matched_keyword,
                            'chunks': doc.get('num_chunks', 0)
                        })
                        count += 1
                        print(f"  [{count}] {doc.get('title', 'No title')[:60]}... (Source: {source}, Keyword: {matched_keyword})")
                except:
                    continue
    except Exception as e:
        print(f"Error: {e}")
    
    print(f"\nFound {len(found)} key conversations\n")
    return found

if __name__ == '__main__':
    find_key_conversations()