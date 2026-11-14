#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_rdc_waiver.py
# Function : apply a tool waiver or a CSV waiver to the parsed violations
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Mark each violation waived or active and reject a waiver without a reason (rule R-023).

Purpose : a waiver is a debt, so it is applied only when it names the rule, the path and
          the reason, and the record keeps the waiver line for the report.
Usage   : vlsit_rdc_waiver.py --violations violations.json --out violations_waived.json [--report TOOL_REPORT] [--csv WAIVER.csv]
Output  : the JSON file and the counts.
Exit    : 0 success, 1 error.
"""
import argparse
import csv
import json
import sys
from pathlib import Path


def load_csv(path):
    entries = []
    with Path(path).open(encoding='utf-8', newline='') as handle:
        for row_index, row in enumerate(csv.DictReader(handle), 2):
            entries.append({'rule': (row.get('rule') or '').strip(),
                            'path': (row.get('path') or '').strip(),
                            'reason': (row.get('reason') or '').strip(),
                            'owner': (row.get('owner') or '').strip(),
                            'line': 'csv:%d' % row_index})
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--violations', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--report', help='tool report, only to record the tool name')
    parser.add_argument('--csv', help='CSV waiver with rule,path,reason,owner')
    args = parser.parse_args()
    document = json.loads(Path(args.violations).read_text(encoding='utf-8'))
    entries = load_csv(args.csv) if args.csv else []
    applied, rejected = 0, 0
    for record in document['violations']:
        for entry in entries:
            if entry['rule'] and entry['rule'] == record['rule']:
                if entry['path'] and entry['path'] != record['path']:
                    continue
                if not entry['reason']:
                    rejected += 1
                    record['waiver_rejected'] = 'reason is empty at %s' % entry['line']
                    break
                record['waived'] = True
                record['waiver_line'] = entry['line']
                record['waiver_reason'] = entry['reason']
                record['waiver_owner'] = entry['owner']
                applied += 1
                break
    for record in document['violations']:
        if record.get('waived') and not record.get('waiver_reason'):
            record['waived'] = False
            rejected += 1
            record['waiver_rejected'] = 'the waiver had no reason'
    document['csv_entries'] = len(entries)
    document['waiver_applied'] = applied
    document['waiver_rejected'] = rejected
    document['active'] = sum(1 for record in document['violations'] if not record.get('waived'))
    document['waived'] = sum(1 for record in document['violations'] if record.get('waived'))
    Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for record in document['violations']:
        state = 'waived' if record.get('waived') else ('rejected' if record.get('waiver_rejected') else 'active')
        print('%-6s %-10s %-34s %s' % (record['id'], record['rule'], record['path'][:34], state))
    print('RESULT: %d active, %d waived, %d waiver(s) rejected, written %s'
          % (document['active'], document['waived'], rejected, args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
