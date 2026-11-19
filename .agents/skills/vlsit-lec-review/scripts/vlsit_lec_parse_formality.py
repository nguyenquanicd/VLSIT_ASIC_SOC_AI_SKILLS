#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_lec_parse_formality.py
# Function : parse a Formality setup Tcl and log into the review models
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Parse Formality setup and log, classify the risks and keep the failing points (rule R-011 to R-023).

Usage   : vlsit_lec_parse_formality.py --setup run.tcl --log run.log --out lec_config.json [--messages lec_log.json]
Output  : the config model, the message model and the risk table.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

CLASS = {
    'read_verilog': 'setup', 'read_sverilog': 'setup', 'read_db': 'setup', 'read_svf': 'setup',
    'set_reference_design': 'setup', 'set_implementation_design': 'setup', 'set_svf': 'setup',
    'set_dont_verify': 'constraint', 'set_dont_verify_points': 'constraint',
    'set_constant': 'constraint', 'set_case_analysis': 'constraint',
    'set_mapping_method': 'mapping', 'match': 'verification', 'verify': 'verification',
}
FIXES = [
    (r'cannot read library|library .* not found', 'the library path is wrong or the file is missing',
     'correct the path and re-run the read step before verify'),
    (r'unresolved module (\S+)', 'the defining file of the module was not read',
     'add the file or declare the module a black box with a reason'),
    (r'undefined cell (\S+)', 'the library list lacks the cell the netlist uses',
     'add the library that defines the cell, or map the cell'),
    (r'unmatched point', 'the mapping could not pair the reference and the implementation point',
     'check the register name, the guidance file and the mapping method'),
    (r'unverified point', 'the point is in the design but not compared',
     'remove the dont_verify or the constant that covers it'),
    (r'verification failed', 'at least one compare point differs',
     'trace the first five failing points (step 8)'),
    (r'aborted point', 'the prover gave up on the point',
     'raise the effort, split the cone or add a cut point'),
    (r'inconsistent svf', 'the guidance file does not match the netlist',
     'regenerate the SVF with the same synthesis run'),
    (r'clock (\S+) not found', 'the clock name changed in the netlist',
     'map the clock with the guidance file or rename it'),
]


def classify(text):
    lowered = text.lower()
    for pattern, cause, fix in FIXES:
        match = re.search(pattern, lowered)
        if match:
            return cause, fix
    return '', ''


def parse_setup(path):
    commands, dont_verify, constants, mapping, black_boxes = [], [], [], [], []
    for line_no, raw in enumerate(Path(path).read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue
        name = re.match(r'([a-z_]+)', line)
        kind = CLASS.get(name.group(1), 'other') if name else 'other'
        commands.append({'line': line_no, 'text': line, 'class': kind})
        if name and name.group(1) in ('set_dont_verify', 'set_dont_verify_points'):
            objects = re.findall(r'\[get_(?:pins|ports|designs|cells)\s+([^\]]+)\]', line)
            dont_verify.append({'line': line_no, 'text': line,
                                'object': objects[0].strip() if objects else line.split()[-1],
                                'comment': ''})
        if name and name.group(1) in ('set_constant', 'set_case_analysis'):
            constants.append({'line': line_no, 'text': line,
                              'object': re.findall(r'\[get_[a-z]+\s+([^\]]+)\]', line)[0] if '[' in line else '',
                              'value': line.split()[-1]})
        if kind == 'mapping':
            mapping.append({'line': line_no, 'text': line})
        if re.search(r'read_db|read_verilog.*lib|set_dont_touch', line):
            black_boxes.append({'line': line_no, 'object': line.split()[-1]})
    return commands, dont_verify, constants, mapping, black_boxes


def risks_of(dont_verify, constants, black_boxes):
    risks = []
    for index, entry in enumerate(dont_verify, 1):
        severity = 'Critical' if re.search(r'reg|state|u_', entry['object']) else 'High'
        risks.append({'id': 'C-%02d' % len(risks), 'item': 'dont_verify', 'severity': severity,
                      'detail': 'object %s is removed from the proof' % (entry['object'] or '?'),
                      'line': entry['line']})
    for entry in constants:
        functional = not re.search(r'scan|test|bist|mode', entry['object'] + entry['text'], re.I)
        risks.append({'id': 'C-%02d' % len(risks), 'item': 'constant',
                      'severity': 'Critical' if functional else 'Medium',
                      'detail': 'constant %s on %s' % (entry['value'], entry['object'] or '?'),
                      'line': entry['line']})
    for entry in black_boxes:
        risks.append({'id': 'C-%02d' % len(risks), 'item': 'black_box', 'severity': 'High',
                      'detail': 'black box or library %s' % entry['object'], 'line': entry['line']})
    return risks


def parse_log(path):
    messages, fails = [], []
    counts = {'errors': 0, 'warnings': 0, 'failing': 0, 'passing': 0, 'unverified': 0, 'unmapped': 0}
    text = Path(path).read_text(encoding='utf-8', errors='replace')
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        lowered = line.lower()
        if re.search(r'^error|error:', lowered):
            counts['errors'] += 1
            cause, fix = classify(line)
            messages.append({'id': 'M-%03d' % (len(messages) + 1), 'severity': 'High', 'text': line,
                             'cause': cause, 'fix': fix, 'file': Path(path).name, 'line': line_no})
        elif re.search(r'^warning|warning:', lowered):
            counts['warnings'] += 1
            cause, fix = classify(line)
            messages.append({'id': 'M-%03d' % (len(messages) + 1), 'severity': 'Medium', 'text': line,
                             'cause': cause, 'fix': fix, 'file': Path(path).name, 'line': line_no})
        if 'verification failed' in lowered:
            counts['failing'] = counts['failing']
        passing = re.search(r'passing points\s*[:=]\s*(\d+)', lowered)
        if passing:
            counts['passing'] = int(passing.group(1))
        failing = re.search(r'failing points\s*[:=]\s*(\d+)', lowered)
        if failing:
            counts['failing'] = int(failing.group(1))
        unverified = re.search(r'unverified points\s*[:=]\s*(\d+)', lowered)
        if unverified:
            counts['unverified'] = int(unverified.group(1))
        unmatched = re.search(r'unmatched points\s*[:=]\s*(\d+)', lowered)
        if unmatched:
            counts['unmapped'] = int(unmatched.group(1))
        point = re.search(r'failing point\s*:\s*([\w./\[\]]+)\s*\(ref\).*?([\w./\[\]]+)\s*\(impl\)', line, re.I)
        if point:
            fails.append({'id': 'F-%02d' % (len(fails) + 1), 'compare_point': point.group(1),
                          'ref': point.group(1), 'impl': point.group(2), 'status': 'fail',
                          'file': Path(path).name, 'line': line_no})
    return messages, fails, counts


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--setup', required=True)
    parser.add_argument('--log', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--messages')
    args = parser.parse_args()
    commands, dont_verify, constants, mapping, black_boxes = parse_setup(args.setup)
    risks = risks_of(dont_verify, constants, black_boxes)
    config = {'tool': 'formality', 'setup': Path(args.setup).name, 'svf': '',
              'commands': commands, 'dont_verify': dont_verify, 'constants': constants,
              'mapping': mapping, 'black_boxes': black_boxes, 'risks': risks,
              'counts': {'commands': len(commands), 'dont_verify': len(dont_verify),
                         'constants': len(constants), 'black_boxes': len(black_boxes)}}
    Path(args.out).write_text(json.dumps(config, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    messages, fails, counts = parse_log(args.log)
    log = {'tool': 'formality', 'files': [{'path': Path(args.log).name, 'errors': counts['errors'],
                                           'warnings': counts['warnings']}],
           'messages': messages, 'fails': fails, 'counts': counts}
    if args.messages:
        Path(args.messages).write_text(json.dumps(log, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('tool=formality commands=%d dont_verify=%d constants=%d black_boxes=%d risks=%d'
          % (len(commands), len(dont_verify), len(constants), len(black_boxes), len(risks)))
    for risk in risks:
        print('%-4s %-10s %-8s line %-4s %s' % (risk['id'], risk['item'], risk['severity'],
                                                risk['line'], risk['detail']))
    print('messages=%d errors=%d warnings=%d fails=%d passing=%d unverified=%d unmapped=%d'
          % (len(messages), counts['errors'], counts['warnings'], len(fails),
             counts['passing'], counts['unverified'], counts['unmapped']))
    print('RESULT: config=%s log=%s' % (args.out, args.messages or 'not written'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
