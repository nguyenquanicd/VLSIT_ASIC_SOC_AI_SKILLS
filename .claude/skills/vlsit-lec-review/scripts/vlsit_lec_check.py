#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_lec_check.py
# Function : verify the LEC report, its language blocks, severities and counts
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Check the delivered report against the rules (rule R-019, R-029 to R-031, R-034, R-035).

Usage   : vlsit_lec_check.py OUT --data OUT/lec_data.json --path RTL_ROOT
Output  : one line per problem, then the RESULT line.
Exit    : 0 pass, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SECTIONS = ['## 1. Environment', '## 2. Configuration risks', '## 3. Logs',
            '## 4. Five failing points', '## 5. Summary and actions']
VI_BLOCKS = ['Tiếng Việt']
SEVERITIES = {'Critical', 'High', 'Medium', 'Low'}
CITE = re.compile(r'([\w.\-]+\.(?:sv|v|tcl|do|log|rpt)):(\d+)')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('out')
    parser.add_argument('--data', required=True)
    parser.add_argument('--path', default='')
    args = parser.parse_args()
    out = Path(args.out)
    problems, warnings = [], []
    reports = list(out.glob('LEC_REVIEW_*.md'))
    if not reports:
        problems.append('no LEC_REVIEW_<design>.md in %s' % out)
    data_path = Path(args.data)
    if not data_path.exists():
        problems.append('no lec_data.json at %s' % args.data)
        data = {}
    else:
        data = json.loads(data_path.read_text(encoding='utf-8'))
    if not (out / 'checks.json').exists():
        problems.append('no checks.json in %s' % out)
    svg = sorted((out / 'svg').glob('*.svg')) if (out / 'svg').is_dir() else []
    if not svg:
        problems.append('no cone figure in %s/svg' % out)

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
        if len(re.findall('Tiếng Việt', text)) < 5:
            problems.append('the report has %d Vietnamese block(s), the five sections need one each'
                            % len(re.findall('Tiếng Việt', text)))
        for fail in data.get('traced', []):
            figure = '%s_cone.svg' % fail.get('id')
            if figure not in text:
                problems.append('cone figure %s is not linked from the report' % figure)
            if ('`%s`' % fail.get('id', '')) not in text:
                warnings.append('fail %s has no table row in the report' % fail.get('id'))
        counts = data.get('counts', {})
        summary = text.split('## 2.')[0]
        for key in ('fails', 'errors', 'warnings', 'traced'):
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
                    warnings.append('citation %s:%s points at a file outside the RTL root' % (name, line))
                elif int(line) > total:
                    problems.append('citation %s:%s is past the end of the file (%d lines)' % (name, line, total))

    for finding in data.get('findings', []):
        if finding.get('severity') not in SEVERITIES:
            problems.append('finding %s has severity %r' % (finding.get('id'), finding.get('severity')))
    if data.get('traced') and len(data['traced']) > 5:
        problems.append('%d fails are traced; the rule allows five before asking (rule R-024)' % len(data['traced']))

    for problem in problems:
        print('ERROR: %s' % problem)
    for warning in warnings:
        print('WARN: %s' % warning)
    print('RESULT: %s (%d error(s), %d warning(s), %d section(s), %d figure(s), %d traced fail(s))'
          % ('PASS' if not problems else 'FAIL', len(problems), len(warnings), len(SECTIONS),
             len(svg), len(data.get('traced', []))))
    return 0 if not problems else 1


if __name__ == '__main__':
    sys.exit(main())
