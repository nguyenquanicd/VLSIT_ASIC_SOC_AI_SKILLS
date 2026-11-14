#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_cdc_check.py
# Function : verify the CDC report, its findings, figures and counts
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Check the delivered CDC report against the rules (rule R-019, R-022, R-023, R-031, R-032).

Usage   : vlsit_cdc_check.py OUT --data OUT/cdc_data.json --path RTL_ROOT
Output  : one line per problem, then the RESULT line.
Exit    : 0 pass, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SECTIONS = ['## 1. Summary', '## 2. Clock domains', '## 3. Crossings', '## 4. Mechanisms',
            '## 5. Tool violations', '## 6. Groups and verdicts', '## 7. Actions', '## 8. Limits']
NAME = re.compile(r'^vlsit_cdc_(\d{4}-\d{2}-\d{2})\.md$')
VERDICTS = {'fix RTL', 'fix SDC', 'waive', 'not CDC'}
CITE = re.compile(r'([\w.\-]+\.(?:sv|v|sdc|tcl|log|rpt)):(\d+)')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('out')
    parser.add_argument('--data', required=True)
    parser.add_argument('--path', default='')
    args = parser.parse_args()
    out = Path(args.out)
    problems, warnings = [], []
    reports = list(out.glob('vlsit_cdc_*.md'))
    if not reports:
        problems.append('no vlsit_cdc_<YYYY-MM-DD>.md in %s' % out)
    if not NAME.match(reports[0].name) if reports else False:
        problems.append('file name %r is not vlsit_cdc_<YYYY-MM-DD>.md' % reports[0].name)
    data_path = Path(args.data)
    if not data_path.exists():
        problems.append('no cdc_data.json at %s' % args.data)
        data = {}
    else:
        data = json.loads(data_path.read_text(encoding='utf-8'))
    if not (out / 'violations.json').exists():
        problems.append('no violations.json in %s' % out)
    svg = sorted((out / 'svg').glob('*.svg')) if (out / 'svg').is_dir() else []
    if not svg:
        problems.append('no mechanism figure in %s/svg' % out)

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
        for entry in data.get('mechanisms', []):
            name = Path(entry.get('figure', '')).name
            if name and name not in text:
                problems.append('mechanism figure %s is not linked from the report' % name)
        blocks = re.split(r'^### F-', text, flags=re.M)[1:]
        for block in blocks:
            title = block.splitlines()[0].strip()
            for field in ('Severity', 'Evidence', 'Verdict'):
                if ('- %s:' % field) not in block:
                    problems.append('finding %r has no %s' % (title[:40], field))
            verdict = re.search(r'^- Verdict:\s*`?(fix RTL|fix SDC|waive|not CDC)`?', block, re.M)
            if verdict and verdict.group(1).startswith('fix') and '- Fix:' not in block:
                problems.append('finding %r is a fix without a described change' % title[:40])
            if verdict and verdict.group(1).startswith('fix') and '- Why:' not in block:
                problems.append('finding %r is a fix without a reason' % title[:40])
        counts = data.get('counts', {})
        summary = text.split('## 2.')[0]
        for key in ('crossings', 'violations', 'groups'):
            if key in counts:
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
                    warnings.append('citation %s:%s points outside the RTL root' % (name, line))
                elif int(line) > total:
                    problems.append('citation %s:%s is past the end of the file (%d lines)' % (name, line, total))

    for group in data.get('groups', []):
        if group.get('verdict') not in VERDICTS:
            problems.append('group %s has verdict %r' % (group.get('id'), group.get('verdict')))

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
