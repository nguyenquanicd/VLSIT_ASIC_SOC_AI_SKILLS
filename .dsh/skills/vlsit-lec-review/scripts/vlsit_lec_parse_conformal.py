#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_lec_parse_conformal.py
# Function : parse a Conformal LEC do file and log into the review models
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Parse Conformal LEC setup and log (rule R-011 to R-023, R-033).

Usage   : vlsit_lec_parse_conformal.py --setup run.do --log run.log --out lec_config.json [--messages lec_log.json]
Output  : the config model, the message model and the risk table.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

CONSTRAINT = {'add_notranslate_modules': 'dont_verify', 'add_constant': 'constant',
              'add_ignored_outputs': 'dont_verify'}
FIXES = [
    (r'unresolved|undefined module', 'a module is not read', 'add the file or declare a black box'),
    (r'non-equivalent', 'at least one compare point differs', 'trace the first five failing points'),
    (r'unmapped', 'a compare point is not mapped', 'check the mapping method and the names'),
    (r'abort', 'the prover gave up', 'raise the effort or split the cone'),
    (r'cannot open|no such file', 'the path is wrong', 'correct the path and re-run'),
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
        kind = 'other'
        if name and name.group(1).startswith(('read_', 'set_system_mode')):
            kind = 'setup'
        if name and name.group(1) in ('map_key_points', 'compare', 'set_mapping_method'):
            kind = 'mapping' if name.group(1) == 'set_mapping_method' else 'verification'
        commands.append({'line': line_no, 'text': line, 'class': kind})
        if name and name.group(1) in CONSTRAINT:
            target = line.split()[-1]
            if CONSTRAINT[name.group(1)] == 'dont_verify':
                dont_verify.append({'line': line_no, 'text': line, 'object': target, 'comment': ''})
            else:
                constants.append({'line': line_no, 'text': line, 'object': target, 'value': 'constant'})
        if kind == 'mapping' or (name and name.group(1) == 'set_mapping_method'):
            mapping.append({'line': line_no, 'text': line})
        if name and name.group(1) in ('add_notranslate_modules', 'add_black_box'):
            black_boxes.append({'line': line_no, 'object': line.split()[-1]})
    risks = []
    for entry in dont_verify:
        risks.append({'id': 'C-%02d' % len(risks), 'item': 'dont_verify', 'severity': 'Critical',
                      'detail': 'modules excluded from the translation: %s' % entry['object'],
                      'line': entry['line']})
    for entry in constants:
        risks.append({'id': 'C-%02d' % len(risks), 'item': 'constant',
                      'severity': 'Critical' if 'scan' not in entry['text'].lower() else 'Medium',
                      'detail': 'constant on %s' % entry['object'], 'line': entry['line']})
    config = {'tool': 'conformal', 'setup': Path(args.setup).name, 'svf': '',
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
        for key, pattern in (('passing', r'passing points?\s*[:=]\s*(\d+)'),
                             ('failing', r'non-equivalent points?\s*[:=]\s*(\d+)'),
                             ('unverified', r'unverified points?\s*[:=]\s*(\d+)'),
                             ('unmapped', r'unmapped points?\s*[:=]\s*(\d+)')):
            found = re.search(pattern, lowered)
            if found:
                counts[key] = int(found.group(1))
        point = re.match(r'^point\s*:\s*(\S+)\s*$', line, re.I)
        if point:
            fails.append({'id': 'F-%02d' % (len(fails) + 1), 'compare_point': point.group(1),
                          'ref': point.group(1), 'impl': point.group(1), 'status': 'fail',
                          'file': Path(args.log).name, 'line': line_no})
    log = {'tool': 'conformal', 'files': [{'path': Path(args.log).name, 'errors': counts['errors'],
                                           'warnings': counts['warnings']}],
           'messages': messages, 'fails': fails, 'counts': counts}
    if args.messages:
        Path(args.messages).write_text(json.dumps(log, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('tool=conformal commands=%d dont_verify=%d constants=%d black_boxes=%d risks=%d'
          % (len(commands), len(dont_verify), len(constants), len(black_boxes), len(risks)))
    print('messages=%d fails=%d passing=%d unverified=%d unmapped=%d'
          % (len(messages), len(fails), counts['passing'], counts['unverified'], counts['unmapped']))
    print('RESULT: config=%s log=%s' % (args.out, args.messages or 'not written'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
