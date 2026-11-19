#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_soc_check.py
# Function : verify the SoC review report, its findings and its artefacts
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Check the delivered SoC report against the rules (rule R-005, R-027 to R-031).

Usage   : vlsit_soc_check.py OUT --data OUT/soc_data.json [--path RTL_ROOT]
Output  : one line per problem, then the RESULT line.
Exit    : 0 pass, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SECTIONS = ['## 1. Summary', '## 2. Inputs', '## 3. HAS coverage', '## 4. System facts',
            '## 5. Hierarchy and connections', '## 6. Connection findings',
            '## 7. Tie, pulse and limitation findings', '## 8. Findings and fixes',
            '## 9. Actions and limits']
NAME = re.compile(r'^vlsit_soc_(\d{4}-\d{2}-\d{2})\.md$')
SEVERITIES = {'Critical', 'High', 'Medium', 'Low'}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('out')
    parser.add_argument('--data', required=True)
    parser.add_argument('--path', default='')
    args = parser.parse_args()
    out = Path(args.out)
    problems, warnings = [], []
    reports = list(out.glob('vlsit_soc_*.md'))
    if not reports:
        problems.append('no vlsit_soc_<YYYY-MM-DD>.md in %s' % out)
    elif not NAME.match(reports[0].name):
        problems.append('file name %r is not vlsit_soc_<YYYY-MM-DD>.md' % reports[0].name)
    data = {}
    if Path(args.data).exists():
        data = json.loads(Path(args.data).read_text(encoding='utf-8'))
    else:
        problems.append('no soc_data.json at %s' % args.data)
    for artefact in ('has.md', 'has.json', 'rtl.json', 'findings.json'):
        if not (out / artefact).exists():
            problems.append('missing artefact %s' % artefact)
    if not (out / 'assets').is_dir():
        warnings.append('no assets/ folder; the HAS figures were not extracted')

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
        if len(re.findall('Tiếng Việt', text)) < 8:
            problems.append('the report has %d Vietnamese block(s); the sections need one each'
                            % len(re.findall('Tiếng Việt', text)))
        for block in re.split(r'^### F-', text, flags=re.M)[1:]:
            title = block.splitlines()[0].strip()
            for field in ('Severity', 'Evidence', 'Verdict'):
                if ('- %s:' % field) not in block:
                    problems.append('finding %r has no %s' % (title[:40], field))
            severity = re.search(r'^- Severity:\s*`?(Critical|High|Medium|Low)`?', block, re.M)
            if severity and severity.group(1) not in SEVERITIES:
                problems.append('finding %r has severity %r' % (title[:40], severity.group(1)))
            verdict = re.search(r'^- Verdict:\s*`?([a-z ]+)`?', block, re.M)
            if verdict and verdict.group(1).strip() == 'fix RTL':
                if '- Fix:' not in block or '- Why:' not in block:
                    problems.append('finding %r is a fix RTL without a change or a reason' % title[:40])
        counts = data.get('counts', {})
        summary = text.split('## 2.')[0]
        for key in ('instances', 'nets', 'findings'):
            if key in counts:
                value = re.search(r'\|\s*%s\s*\|\s*`?(\d+)`?' % key, summary, re.I)
                if value and int(value.group(1)) != counts[key]:
                    problems.append('summary says %s=%s and the data says %d' % (key, value.group(1), counts[key]))
        if args.path:
            for name in re.findall(r'([\w.\-]+\.(?:sv|v)):(\d+)', text):
                path = Path(args.path) / name[0]
                if path.exists() and int(name[1]) > path.read_text(encoding='utf-8', errors='replace').count('\n') + 1:
                    problems.append('citation %s:%s is past the end of the file' % name)

    for problem in problems:
        print('ERROR: %s' % problem)
    for warning in warnings:
        print('WARN: %s' % warning)
    print('RESULT: %s (%d error(s), %d warning(s), %d section(s), %d finding(s) in data)'
          % ('PASS' if not problems else 'FAIL', len(problems), len(warnings), len(SECTIONS),
             len(data.get('findings', []))))
    return 0 if not problems else 1


if __name__ == '__main__':
    sys.exit(main())
