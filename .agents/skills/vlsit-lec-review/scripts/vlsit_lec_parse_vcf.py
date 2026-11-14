#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_lec_parse_vcf.py
# Function : parse a VC Formal EQ setup and log into the review models
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Parse VC Formal EQ setup and log (rule R-011 to R-023, R-033).

Usage   : vlsit_lec_parse_vcf.py --setup run.tcl --log run.log --out lec_config.json [--messages lec_log.json]
Output  : the config model, the message model and the risk table.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

FIXES = [
    (r'failed to read|no such file', 'a file path is wrong', 'correct the path and re-run'),
    (r'unmatched', 'a compare point is not matched', 'check the mapping and the names'),
    (r'property failed|check_fv.*fail', 'at least one property differs', 'trace the first five failing points'),
    (r'error', 'the setup stopped before the check', 'read the first error in the log'),
]


def classify(text):
    for pattern, cause, fix in FIXES:
        if re.search(pattern, text, re.I):
            return cause, fix
    return '', ''


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--setup', required=True)
    parser.add_argument('--log', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--messages')
    args = parser.parse_args()
    commands, dont_verify, constants, mapping, black_boxes = [], [], [], [], []
    for line_no, raw in enumerate(Path(args.setup).read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue
        name = re.match(r'([a-z_]+)', line)
        kind = 'setup' if name and name.group(1) in ('read_verilog', 'read_file', 'read_guidance') else 'other'
        if name and name.group(1) in ('check_fv', 'verify', 'report'):
            kind = 'verification'
        if name and name.group(1) in ('map', 'set_mapping'):
            kind = 'mapping'
        commands.append({'line': line_no, 'text': line, 'class': kind})
        if 'dont_verify' in line and name:
            dont_verify.append({'line': line_no, 'text': line,
                                'object': line.split()[-1].strip('{}'), 'comment': ''})
        if 'set_constant' in line or 'assume' in line:
            constants.append({'line': line_no, 'text': line, 'object': line.split()[-1], 'value': 'constant'})
        if kind == 'mapping':
            mapping.append({'line': line_no, 'text': line})
        if re.search(r'-black_box|add_black_box', line):
            black_boxes.append({'line': line_no, 'object': line.split()[-1]})
    risks = []
    for entry in dont_verify:
        risks.append({'id': 'C-%02d' % len(risks), 'item': 'dont_verify', 'severity': 'Critical',
                      'detail': 'check_fv dont_verify on %s' % entry['object'], 'line': entry['line']})
    for entry in constants:
        risks.append({'id': 'C-%02d' % len(risks), 'item': 'constant',
                      'severity': 'Critical' if 'scan' not in entry['text'].lower() else 'Medium',
                      'detail': 'constant or assumption on %s' % entry['object'], 'line': entry['line']})
    config = {'tool': 'vcf', 'setup': Path(args.setup).name, 'svf': '',
              'commands': commands, 'dont_verify': dont_verify, 'constants': constants,
              'mapping': mapping, 'black_boxes': black_boxes, 'risks': risks,
              'counts': {'commands': len(commands), 'dont_verify': len(dont_verify),
                         'constants': len(constants), 'black_boxes': len(black_boxes)}}
    Path(args.out).write_text(json.dumps(config, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    text = Path(args.log).read_text(encoding='utf-8', errors='replace')
    messages, fails = [], []
    counts = {'errors': 0, 'warnings': 0, 'failing': 0, 'passing': 0, 'unverified': 0, 'unmapped': 0}
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        lowered = line.lower()
        if re.match(r'^error', lowered):
            counts['errors'] += 1
            cause, fix = classify(line)
            messages.append({'id': 'M-%03d' % (len(messages) + 1), 'severity': 'High', 'text': line,
                             'cause': cause, 'fix': fix, 'file': Path(args.log).name, 'line': line_no})
        elif re.match(r'^warning', lowered):
            counts['warnings'] += 1
            cause, fix = classify(line)
            messages.append({'id': 'M-%03d' % (len(messages) + 1), 'severity': 'Medium', 'text': line,
                             'cause': cause, 'fix': fix, 'file': Path(args.log).name, 'line': line_no})
        for key, pattern in (('passing', r'pass(?:ing)?\s*[:=]\s*(\d+)'),
                             ('failing', r'fail(?:ing)?\s*[:=]\s*(\d+)'),
                             ('unverified', r'unverified\s*[:=]\s*(\d+)'),
                             ('unmapped', r'unmatched\s*[:=]\s*(\d+)')):
            found = re.search(pattern, lowered)
            if found:
                counts[key] = int(found.group(1))
        property_fail = re.search(r'property\s+(\S+)\s+.*failed', line, re.I)
        if property_fail:
            fails.append({'id': 'F-%02d' % (len(fails) + 1), 'compare_point': property_fail.group(1),
                          'ref': property_fail.group(1), 'impl': property_fail.group(1),
                          'status': 'fail', 'file': Path(args.log).name, 'line': line_no})
    log = {'tool': 'vcf', 'files': [{'path': Path(args.log).name, 'errors': counts['errors'],
                                     'warnings': counts['warnings']}],
           'messages': messages, 'fails': fails, 'counts': counts}
    if args.messages:
        Path(args.messages).write_text(json.dumps(log, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('tool=vcf commands=%d dont_verify=%d constants=%d risks=%d messages=%d fails=%d'
          % (len(commands), len(dont_verify), len(constants), len(risks), len(messages), len(fails)))
    print('RESULT: config=%s log=%s' % (args.out, args.messages or 'not written'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
