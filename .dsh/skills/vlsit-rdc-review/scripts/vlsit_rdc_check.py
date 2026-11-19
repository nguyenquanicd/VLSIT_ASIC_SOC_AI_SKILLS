#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_rdc_check.py
# Function : verify the RDC report, its counts, citations, figures and verdicts
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Check the delivered report against the rules before it is reported (rule R-026 to R-028, R-031, R-032).

Usage   : vlsit_rdc_check.py OUT --data OUT/rdc_data.json --path RTL_ROOT
Output  : one line per problem, then the RESULT line.
Exit    : 0 pass, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SECTIONS = ['## 1. Summary', '## 2. Inputs', '## 3. Reset domains', '## 4. Reset domain crossings',
            '## 5. Reset mechanisms', '## 6. Tool violation summary', '## 7. Groups by root cause',
            '## 8. SDC gaps', '## 9. Open questions']
VERDICTS = {'fix RTL', 'fix SDC', 'waive', 'not RDC'}
CITE = re.compile(r'([\w.\-]+\.(?:sv|v|sdc)):(\d+)')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('out')
    parser.add_argument('--data', required=True)
    parser.add_argument('--path', default='')
    args = parser.parse_args()
    out = Path(args.out)
    problems, warnings = [], []

    reports = list(out.glob('RDC_REVIEW_*.md'))
    if not reports:
        problems.append('no RDC_REVIEW_<design>.md in %s' % out)
    data_path = Path(args.data)
    if not data_path.exists():
        problems.append('no rdc_data.json at %s' % args.data)
        data = {}
    else:
        data = json.loads(data_path.read_text(encoding='utf-8'))
    if not (out / 'violations.json').exists():
        problems.append('no violations.json in %s' % out)
    svg = sorted((out / 'svg').glob('*.svg')) if (out / 'svg').is_dir() else []
    if not svg:
        problems.append('no SVG figure in %s/svg' % out)

    if reports:
        text = reports[0].read_text(encoding='utf-8')
        position = -1
        for heading in SECTIONS:
            found = text.find(heading)
            if found < 0:
                problems.append('missing section %r' % heading)
            elif found < position:
                problems.append('section %r is out of order' % heading)
            else:
                position = found
        mechanisms = data.get('mechanisms', [])
        for entry in mechanisms:
            name = Path(entry.get('figure', '')).name
            if name and name not in text:
                problems.append('figure %s is not linked from the report' % name)
        groups = data.get('groups', [])
        listed = len(re.findall(r'^\|\s*G-\d+', text, re.M))
        if listed and groups and listed < len(groups):
            warnings.append('the report lists %d group row(s) and the data has %d' % (listed, len(groups)))
        counts = data.get('counts', {})
        summary = text.split('## 2.')[0]
        for key in ('domains', 'crossings', 'groups'):
            if key in counts and ('| %s |' % key) in summary.lower():
                value = re.search(r'\|\s*%s\s*\|\s*`?(\d+)`?' % key, summary, re.I)
                if value and int(value.group(1)) != counts[key]:
                    problems.append('summary says %s=%s and the data says %d' % (key, value.group(1), counts[key]))
        if args.path:
            root = Path(args.path)
            cache = {}
            for name, line in CITE.findall(text):
                if name not in cache:
                    candidate = root / name
                    cache[name] = (candidate.read_text(encoding='utf-8', errors='replace').count('\n') + 1
                                   if candidate.exists() else None)
                total = cache[name]
                if total is None:
                    problems.append('citation %s:%s points at a missing file' % (name, line))
                elif int(line) > total:
                    problems.append('citation %s:%s is past the end of the file (%d lines)' % (name, line, total))

    for group in data.get('groups', []):
        verdict = group.get('verdict', '')
        if verdict not in VERDICTS:
            problems.append('group %s has verdict %r, not one of %s' % (group.get('id'), verdict, sorted(VERDICTS)))
        if verdict == 'waive' and not (group.get('mechanism') and group.get('risk')):
            problems.append('group %s is waived without a mechanism and a risk' % group.get('id'))
        if verdict == 'fix SDC' and not group.get('sdc_command'):
            problems.append('group %s is a fix SDC without a command' % group.get('id'))
    for entry in data.get('mechanisms', []):
        if entry.get('name') and Path(entry.get('figure', '')).name not in {p.name for p in svg}:
            warnings.append('mechanism %s has no figure file' % entry.get('name'))

    for problem in problems:
        print('ERROR: %s' % problem)
    for warning in warnings:
        print('WARN: %s' % warning)
    print('RESULT: %s (%d error(s), %d warning(s), %d section(s), %d figure(s), %d group(s))'
          % ('PASS' if not problems else 'FAIL', len(problems), len(warnings), len(SECTIONS),
             len(svg), len(data.get('groups', []))))
    return 0 if not problems else 1


if __name__ == '__main__':
    sys.exit(main())
