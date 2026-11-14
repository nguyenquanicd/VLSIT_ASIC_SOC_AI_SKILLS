#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_rdc_parse_questa.py
# Function : normalise a Questa CDC report into the common violation record
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Parse a Questa CDC report (rule R-020, R-030).

Usage   : vlsit_rdc_parse_questa.py REPORT --out violations.json [--waive FILE]
Output  : the JSON file and one line per violation.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path


def parse_waiver(path):
    entries = []
    if not path:
        return entries
    for line_no, line in enumerate(Path(path).read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        text = line.strip()
        if not text or text.startswith('#'):
            continue
        parts = re.split(r'\s*\|\s*|\s+', text)
        if len(parts) >= 2 and parts[0].lower() != 'rule':
            entries.append({'rule': parts[0], 'path': '%s -> %s' % (parts[1], parts[2]) if len(parts) > 2 else '',
                            'reason': ' '.join(parts[3:]) if len(parts) > 3 else '', 'owner': '',
                            'line': line_no})
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('report')
    parser.add_argument('--out', required=True)
    parser.add_argument('--waive')
    args = parser.parse_args()
    lines = Path(args.report).read_text(encoding='utf-8', errors='replace').splitlines()
    records, current, section = [], None, 'unknown'

    def flush():
        nonlocal current
        if current and current.get('rule'):
            records.append(current)
        current = None

    for line_no, line in enumerate(lines, 1):
        text = line.strip()
        heading = re.match(r'^[-=]{3,}\s*(.+?)\s*[-=]{3,}$', text)
        if heading:
            section = heading.group(1)
            continue
        found = re.match(r'^Violation\s*[:\s]+(\S+)', text)
        if found:
            flush()
            current = {'id': 'V-%03d' % (len(records) + 1), 'tool': 'questa', 'rule': found.group(1),
                       'severity': '', 'section': section, 'path': '', 'from': '', 'to': '',
                       'from_clock': '', 'to_clock': '', 'from_reset': '', 'to_reset': '',
                       'line': line_no, 'waived': False, 'waiver_line': None}
            continue
        if current is None:
            continue
        severity = re.match(r'^Severity\s*:\s*(\w+)', text, re.I)
        if severity:
            current['severity'] = severity.group(1)
            continue
        pair = re.search(r'From\s*[:\s]+(\S+)\s+To\s*[:\s]+(\S+)', text, re.I)
        if pair:
            current['from'], current['to'] = pair.group(1), pair.group(2)
            current['path'] = '%s -> %s' % (pair.group(1), pair.group(2))
            continue
        clocks = re.search(r'Clocks?\s*:\s*(\S+)\s*->\s*(\S+)', text, re.I)
        if clocks:
            current['from_clock'], current['to_clock'] = clocks.group(1), clocks.group(2)
            continue
        reset = re.match(r'^Reset\s*:\s*(\S+)', text, re.I)
        if reset:
            current['from_reset'] = reset.group(1)
    flush()

    waiver = parse_waiver(args.waive)
    for record in records:
        for entry in waiver:
            if entry['rule'] == record['rule'] and (not entry['path'] or entry['path'] == record['path']):
                if entry['reason']:
                    record['waived'] = True
                    record['waiver_line'] = entry['line']
                    record['waiver_reason'] = entry['reason']
                break
    document = {'schema': 'vlsit-rdc-violations/1', 'tool': 'questa', 'tool_name': 'Questa CDC',
                'version': '', 'count': len(records), 'waiver_entries': len(waiver),
                'violations': records, 'skipped_lines': 0}
    Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for record in records:
        print('%-6s %-10s %-8s %-34s %s' % (record['id'], record['rule'], record['severity'],
                                            record['path'][:34], 'waived' if record['waived'] else 'active'))
    print('RESULT: tool=questa violations=%d waived=%d, written %s'
          % (len(records), sum(1 for record in records if record['waived']), args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
