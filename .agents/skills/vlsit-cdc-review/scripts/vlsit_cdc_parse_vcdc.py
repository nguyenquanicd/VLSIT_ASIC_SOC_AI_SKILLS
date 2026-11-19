#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_cdc_parse_vcdc.py
# Function : normalise a VC CDC reset report and its .waive file
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Parse a VC CDC (Synopsys) reset report (rule R-020, R-030).

Usage   : vlsit_cdc_parse_vcdc.py REPORT --out violations.json [--waive FILE]
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
        rule = re.search(r'-rule\s+(\S+)', line)
        pin = re.search(r'-pin\s+(\S+)', line)
        reason = re.search(r'-reason\s+"([^"]*)"', line)
        owner = re.search(r'-owner\s+(\S+)', line)
        if rule:
            entries.append({'rule': rule.group(1), 'path': pin.group(1) if pin else '',
                            'reason': reason.group(1) if reason else '', 'owner': owner.group(1) if owner else '',
                            'line': line_no})
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('report')
    parser.add_argument('--out', required=True)
    parser.add_argument('--waive')
    args = parser.parse_args()
    text = Path(args.report).read_text(encoding='utf-8', errors='replace')
    lines = text.splitlines()
    records, current = [], None
    section = 'unknown'

    def flush():
        nonlocal current
        if current and current.get('rule'):
            records.append(current)
        current = None

    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        heading = re.match(r'^\[(.+)\]$', stripped)
        if heading:
            section = heading.group(1)
            continue
        rule = re.match(r'^Rule\s*:\s*(\S+)', stripped)
        if rule:
            flush()
            current = {'id': 'V-%03d' % (len(records) + 1), 'tool': 'vcdc', 'rule': rule.group(1),
                       'severity': '', 'section': section, 'path': '', 'from': '', 'to': '',
                       'from_clock': '', 'to_clock': '', 'from_reset': '', 'to_reset': '',
                       'line': line_no, 'waived': False, 'waiver_line': None}
            continue
        if current is None:
            continue
        severity = re.match(r'^Severity\s*:\s*(\w+)', stripped)
        if severity:
            current['severity'] = severity.group(1)
        start = re.match(r'^Startpoint\s*:\s*(\S+)', stripped)
        if start:
            current['from'] = start.group(1)
        end = re.match(r'^Endpoint\s*:\s*(\S+)', stripped)
        if end:
            current['to'] = end.group(1)
        crossing = re.match(r'^Crossing\s*:\s*(\S+)\s*->\s*(\S+)', stripped)
        if crossing:
            current['from_clock'], current['to_clock'] = crossing.group(1), crossing.group(2)
        reset = re.match(r'^Reset\s*:\s*(\S+)', stripped)
        if reset:
            current['from_reset'] = reset.group(1)
    flush()
    for record in records:
        record['path'] = '%s -> %s' % (record['from'], record['to']) if record['from'] else ''
    waiver = parse_waiver(args.waive)
    for record in records:
        for entry in waiver:
            if entry['rule'] == record['rule'] and (not entry['path'] or record['to'].startswith(entry['path'])):
                if entry['reason']:
                    record['waived'] = True
                    record['waiver_line'] = entry['line']
                    record['waiver_reason'] = entry['reason']
                break
    version = re.search(r'VC\s+CDC\s*(?:Version)?\s*([\w.]+)', text)
    document = {'schema': 'vlsit-cdc-violations/1', 'tool': 'vcdc', 'tool_name': 'VC CDC',
                'version': version.group(1) if version else '', 'count': len(records),
                'waiver_entries': len(waiver), 'violations': records, 'skipped_lines': 0}
    Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for record in records:
        print('%-6s %-10s %-8s %-34s %s' % (record['id'], record['rule'], record['severity'],
                                            record['path'][:34], 'waived' if record['waived'] else 'active'))
    print('RESULT: tool=vcdc version=%s violations=%d waived=%d, written %s'
          % (document['version'] or '?', len(records),
             sum(1 for record in records if record['waived']), args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
