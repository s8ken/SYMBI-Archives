import tarfile
from pathlib import Path

ROOT = Path('.')
SRC = ROOT / 'symbi-llm-repo'
OUT = ROOT / 'symbi-llm-repo.tar.gz'

def main():
    if not SRC.exists():
        raise SystemExit('symbi-llm-repo not found')
    with tarfile.open(OUT, 'w:gz') as tar:
        tar.add(SRC, arcname='symbi-llm-repo')
    print('Packed:', OUT)

if __name__ == '__main__':
    main()

