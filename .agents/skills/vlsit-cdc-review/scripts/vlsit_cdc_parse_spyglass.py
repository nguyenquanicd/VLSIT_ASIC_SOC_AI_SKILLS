#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_cdc_parse_spyglass.py
# Function : normalise a Spyglass CDC/CDC report and read its .waive file
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Parse a Spyglass reset report into the common violation record (rule R-020, R-030).

Purpose : one record per violation with the tool, rule, severity, section, path, domain
          pair and the report line.
Usage   : vlsit_cdc_parse_spyglass.py REPORT --out violations.json [--waive FILE]
Output  : the JSON file, one line per violation and the skipped-line count.
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
        if not line.strip() or line.strip().startswith('#'):
            continue
        rule = re.search(r'-rule\s+(\S+)', line)
        path_field = re.search(r'-path\s+"([^"]+)"', line) or re.search(r'-path\s+(\S+ -> \S+)', line)
        reason = re.search(r'-reason\s+"([^"]*)"', line) or re.search(r'-reason\s+(.+)$', line)
        owner = re.search(r'-owner\s+(\S+)', line)
        entries.append({'rule': rule.group(1) if rule else '', 'path': path_field.group(1) if path_field else '',
                        'reason': (reason.group(1).strip() if reason else ''), 'owner': owner.group(1) if owner else '',
                        'line': line_no})
    return entries


def parse_report(text):
    violations = []
    block, section, pending = [], 'unknown', False
    last_blank = True
    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if re.fullmatch(r'[-=]{6,}', stripped):
            pending = last_blank
            last_blank = False
            continue
        if pending and stripped:
            section, pending = stripped, False
            last_blank = False
            continue
        heading = re.match(r'^[-=]+\s*(.+?)\s*[-=]+$', stripped)
        if heading and len(stripped) > 6:
            section = heading.group(1)
            continue
        if not stripped:
            if block:
                violations.append((block, line_no, section))
                block = []
            last_blank = True
            continue
        pending = False
        last_blank = False
        block.append((line_no, stripped))
    if block:
        violations.append((block, 0, section))

    records, skipped = [], 0
    for lines, end_line, section_name in violations:
        fields = {}
        for line_no, text in lines:
            for key, pattern in (('rule', r'^Rule\s*[:=]\s*(\S+)'), ('severity', r'^Severity\s*[:=]\s*(\w+)'),
                                 ('path', r'^Path\s*[:=]\s*(.+)$'), ('from_clock', r'^From\s+Clock\s*[:=]\s*(\S+)'),
                                 ('to_clock', r'^To\s+Clock\s*[:=]\s*(\S+)'), ('reset', r'^Reset\s*[:=]\s*(\S+)'),
                                 ('section', r'^Section\s*[:=]\s*(.+)$')):
                found = re.match(pattern, text, re.I)
                if found and key not in fields:
                    fields[key] = found.group(1).strip()
                    fields.setdefault('_line', line_no)
        if not fields.get('rule'):
            skipped += len(lines)
            continue
        path = fields.get('path', '')
        halves = [part.strip() for part in path.split('->')] if '->' in path else ['', '']
        records.append({'id': 'V-%03d' % (len(records) + 1), 'tool': 'spyglass',
                        'rule': fields['rule'], 'severity': fields.get('severity', ''),
                        'section': fields.get('section', section_name),
                        'path': path, 'from': halves[0], 'to': halves[1],
                        'from_clock': fields.get('from_clock', ''), 'to_clock': fields.get('to_clock', ''),
                        'from_reset': fields.get('reset', ''), 'to_reset': '',
                        'line': fields.get('_line', end_line), 'waived': False, 'waiver_line': None})
    return records, skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('report')
    parser.add_argument('--out', required=True)
    parser.add_argument('--waive', help='Spyglass .waive file')
    args = parser.parse_args()
    text = Path(args.report).read_text(encoding='utf-8', errors='replace')
    records, skipped = parse_report(text)
    tool = 'Spyglass' if 'spyglass' in text.lower() else 'unknown'
    version = re.search(r'(?:Version|Release)\s*[:=]\s*(\S+)', text)
    waiver = parse_waiver(args.waive)
    for record in records:
        for entry in waiver:
            if entry['rule'] and entry['rule'] == record['rule'] and (
                    not entry['path'] or entry['path'] == record['path']):
                if entry['reason']:
                    record['waived'] = True
                    record['waiver_line'] = entry['line']
                    record['waiver_reason'] = entry['reason']
                    record['waiver_owner'] = entry['owner']
                break
    document = {'schema': 'vlsit-cdc-violations/1', 'tool': 'spyglass', 'tool_name': tool,
                'version': version.group(1) if version else '',
                'count': len(records), 'waiver_entries': len(waiver),
                'violations': records, 'skipped_lines': skipped}
    Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for record in records:
        print('%-6s %-10s %-8s %-30s %s' % (record['id'], record['rule'], record['severity'],
                                            record['path'][:30], 'waived' if record['waived'] else 'active'))
    print('RESULT: tool=%s version=%s violations=%d waived=%d skipped_lines=%d, written %s'
          % (tool, document['version'] or '?', len(records),
             sum(1 for record in records if record['waived']), skipped, args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
