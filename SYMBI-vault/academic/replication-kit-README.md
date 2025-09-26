# Replication Kit
Folders: /prompts • /protocol • /receipts • /metrics • /analysis • /ethics

## Quick start
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python run_ab.py --tasks data/tasks.csv --mode both --out out/

**Receipt schema**: see `latex/arxiv/src/receipt_schema.json`
