#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_review_report.py
# Function : build and check the final review report with a per-item fix proposal
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Build or check `vlsit_<review>_<YYYY-MM-DD>.md` (rule: named final report with a fix proposal).

Purpose : one shared report shape for every review skill. Each finding carries an
          assessment, a verdict (waive, fix or none) and, when it can be fixed, the RTL
          change and the reason it works, with a short snippet when it fits.
Usage   : vlsit_review_report.py build --review spec --date 2026-11-14 --out DIR [--design IP]
          vlsit_review_report.py check DIR/vlsit_spec_2026-11-14.md
Output  : build writes the skeleton; check prints one line per problem and RESULT.
Exit    : 0 success or pass, 1 error or fail.
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

REVIEWS = {'spec': 'Specification review', 'impl': 'Implementation review',
           'sdc': 'SDC and timing review', 'rdc': 'Reset domain crossing review',
           'lec': 'Equivalence check review'}
NAME = re.compile(r'^vlsit_(spec|impl|sdc|rdc|lec)_(\d{4}-\d{2}-\d{2})\.md$')
VERDICTS = {'waive', 'fix', 'none'}
FIELDS = ('Evidence', 'Assessment', 'Verdict')


def build(review, date, out, design):
    if review not in REVIEWS:
        raise SystemExit('ERROR: unknown review %r, expected one of %s' % (review, ', '.join(REVIEWS)))
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        raise SystemExit('ERROR: date must be YYYY-MM-DD, got %r' % date)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    target = out / ('vlsit_%s_%s.md' % (review, date))
    if target.exists():
        raise SystemExit('ERROR: %s exists; remove it or choose another date' % target)
    lines = [
        '# %s of %s - %s' % (REVIEWS[review], design or '<design>', date), '',
        '## 1. Summary', '',
        '| Item | Value |', '|---|---|',
        '| Design | `%s` |' % (design or '<design>'),
        '| Review | %s |' % REVIEWS[review],
        '| Date | %s |' % date,
        '| Findings | 0 |', '| Critical | 0 |', '| High | 0 |', '| Medium | 0 |', '| Low | 0 |',
        '| Waivable | 0 |', '| Fixable | 0 |', '',
        '## 2. Findings', '',
        'Each finding has an assessment, a verdict and, when it can be fixed, the RTL change',
        'and the reason it works.', '',
        '### F-01 <short title>', '',
        '- Evidence: `<file>:<line>`',
        '- Assessment: <what is wrong and why it matters>',
        '- Verdict: `fix` | `waive` | `none`',
        '- Fix: <the RTL change, when the verdict is fix>',
        '- Why: <why the fix removes the problem, when the verdict is fix>',
        '',
        '```systemverilog',
        '// short snippet only when the change fits in a few lines',
        '```', '',
        '## 3. Actions', '',
        '| Action | Owner | Blocks sign-off |', '|---|---|---|', '',
        '## 4. Limits', '',
        '- <what was not checked and why>',
    ]
    target.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('RESULT: built %s' % target)
    return 0


def check(path):
    path = Path(path)
    problems, warnings = [], []
    match = NAME.match(path.name)
    if not match:
        problems.append('file name %r is not vlsit_<spec|impl|sdc|rdc|lec>_<YYYY-MM-DD>.md' % path.name)
    if not path.exists():
        print('ERROR: %s does not exist' % path)
        return 1
    text = path.read_text(encoding='utf-8')
    for heading in ('## 1. Summary', '## 2. Findings', '## 3. Actions', '## 4. Limits'):
        if heading not in text:
            problems.append('missing section %r' % heading)

    blocks = re.split(r'^### ', text, flags=re.M)[1:]
    counts = {'fix': 0, 'waive': 0, 'none': 0}
    severity_count = {level: 0 for level in ('Critical', 'High', 'Medium', 'Low')}
    for block in blocks:
        title = block.splitlines()[0].strip()
        if not re.match(r'^F-\d+', title):
            continue
        for field in FIELDS:
            if ('- %s:' % field) not in block:
                problems.append('finding %r has no %s field' % (title[:40], field))
        severity = re.search(r'^- Severity:\s*`?(Critical|High|Medium|Low)`?', block, re.M)
        if severity:
            severity_count[severity.group(1)] += 1
        verdict = re.search(r'^- Verdict:\s*`?(fix|waive|none)`?', block, re.M)
        if not verdict:
            problems.append('finding %r has no verdict of fix, waive or none' % title[:40])
            continue
        counts[verdict.group(1)] += 1
        if verdict.group(1) == 'fix':
            if '- Fix:' not in block or len(re.search(r'^- Fix:\s*(.+)$', block, re.M).group(1).strip()) < 20:
                problems.append('finding %r is a fix without a described change' % title[:40])
            if '- Why:' not in block or len(re.search(r'^- Why:\s*(.+)$', block, re.M).group(1).strip()) < 20:
                problems.append('finding %r is a fix without a reason' % title[:40])
        if verdict.group(1) == 'waive' and '- Why:' not in block:
            warnings.append('finding %r is waived without a reason' % title[:40])
    summary = text.split('## 2.')[0]
    for key, value in (('Findings', len(blocks)), ('Critical', severity_count['Critical']),
                       ('High', severity_count['High']), ('Medium', severity_count['Medium']),
                       ('Low', severity_count['Low']), ('Waivable', counts['waive']),
                       ('Fixable', counts['fix'])):
        row = re.search(r'\|\s*%s\s*\|\s*`?(\d+)`?' % key, summary)
        if row and int(row.group(1)) != value:
            problems.append('summary says %s=%s and the body has %d' % (key, row.group(1), value))

    for problem in problems:
        print('ERROR: %s' % problem)
    for warning in warnings:
        print('WARN: %s' % warning)
    print('RESULT: %s (%d error(s), %d warning(s), %d finding(s): fix %d, waive %d, none %d)'
          % ('PASS' if not problems else 'FAIL', len(problems), len(warnings), len(blocks),
             counts['fix'], counts['waive'], counts['none']))
    return 0 if not problems else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='action', required=True)
    b = sub.add_parser('build')
    b.add_argument('--review', required=True, choices=sorted(REVIEWS))
    b.add_argument('--date', required=True)
    b.add_argument('--out', required=True)
    b.add_argument('--design', default='')
    c = sub.add_parser('check')
    c.add_argument('report')
    args = parser.parse_args()
    if args.action == 'build':
        return build(args.review, args.date, args.out, args.design)
    return check(args.report)


if __name__ == '__main__':
    sys.exit(main())
