#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_review_gate.py
# Function : gate metrics, deterministic audit sample and root-cause grouping
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Compute the gate metrics, draw the review-the-review sample and group by root cause.

Purpose : turn the seven review methods into one command: the gate either passes or
          names the finding that blocks it, the audit sample is deterministic, and the
          findings are grouped by cause rather than by report line.
Usage   : vlsit_review_gate.py metrics findings.json [--waiver-budget 10] [--min-sampling 0.1] --out gate.json
          vlsit_review_gate.py sample  findings.json [--ratio 0.1] --out audit.json
          vlsit_review_gate.py group   findings.json --out grouped.json
Output  : the JSON file and a table.
Exit    : 0 gate pass or command ok, 1 gate fail or bad input.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

SEVERITIES = ('Critical', 'High', 'Medium', 'Low')
VERDICTS = ('fix RTL', 'fix SDC', 'fix HAS', 'waive', 'not a defect', 'accepted risk')


SEVERITY_MAP = {'Error': 'High', 'Warning': 'Medium', 'Info': 'Low'}


def adapt(document, kind):
    """Read the canonical list, or one of the tool-review files of the other skills."""
    if kind == 'auto':
        kind = 'canonical' if 'findings' in document else (
            'rdc' if 'violations' in document else 'soc' if 'design' in document else 'canonical')
    if kind in ('rdc', 'cdc'):
        out = []
        for item in document.get('violations', []):
            waived = bool(item.get('waived'))
            severity = item.get('severity')
            severity = severity if severity in SEVERITIES else SEVERITY_MAP.get(severity, 'Medium')
            out.append({'id': item.get('id'), 'severity': severity,
                        'verdict': 'waive' if waived else 'fix RTL',
                        'root_cause': '%s %s' % (item.get('rule', ''), item.get('path', '') or item.get('from', '')),
                        'evidence': '%s:%s' % (item.get('file', ''), item.get('line', '')),
                        'owner': item.get('waiver_owner', '') if waived else '',
                        'invalidation': item.get('waiver_invalidation', '') if waived else '',
                        'traced': False})
        return out
    return document.get('findings', [])


def load(path, kind='auto'):
    document = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if isinstance(document, list):
        return document, document
    return document, adapt(document, kind)


def key_of(finding):
    return finding.get('root_cause') or finding.get('evidence') or finding.get('id', '')


def metrics(findings, budget, min_sampling):
    counts = {level: sum(1 for item in findings if item.get('severity') == level) for level in SEVERITIES}
    waived = [item for item in findings if item.get('verdict') == 'waive']
    fixed = [item for item in findings if item.get('verdict', '').startswith('fix')]
    open_critical = [item for item in findings if item.get('severity') == 'Critical'
                     and item.get('verdict') != 'waive']
    missing_verdict = [item['id'] for item in findings if item.get('verdict') not in VERDICTS]
    missing_owner = [item['id'] for item in findings if item.get('verdict') == 'waive'
                     and not item.get('owner')]
    missing_invalidation = [item['id'] for item in findings if item.get('verdict') == 'waive'
                            and not item.get('invalidation')]
    traced = sum(1 for item in findings if item.get('traced'))
    sampling = (traced / len(findings)) if findings else 0.0
    closure = (len(fixed) / (len(fixed) + len(waived))) if (fixed or waived) else 1.0
    reasons = []
    if open_critical:
        reasons.append('%d unwaived Critical finding(s): %s'
                       % (len(open_critical), ', '.join(item['id'] for item in open_critical)))
    if len(waived) > budget:
        reasons.append('%d waiver(s) exceed the budget of %d' % (len(waived), budget))
    if missing_verdict:
        reasons.append('%d finding(s) without a verdict: %s' % (len(missing_verdict),
                                                                ', '.join(missing_verdict[:5])))
    if missing_owner:
        reasons.append('%d waiver(s) without an owner' % len(missing_owner))
    if missing_invalidation:
        reasons.append('%d waiver(s) without an invalidation condition' % len(missing_invalidation))
    status = 'FAIL' if reasons else 'PASS'
    warnings = []
    if sampling < min_sampling:
        warnings.append('sampling %.0f%% is below the %.0f%% policy'
                        % (sampling * 100, min_sampling * 100))
    return {'status': status, 'reasons': reasons, 'warnings': warnings,
            'counts': counts, 'findings': len(findings), 'waived': len(waived),
            'fixed': len(fixed), 'waiver_budget': budget,
            'waiver_usage': ('%d/%d' % (len(waived), budget)),
            'open_critical': len(open_critical), 'sampling': round(sampling, 3),
            'closure_rate': round(closure, 3)}


def sample(findings, ratio):
    if not findings:
        return []
    count = max(1, math.ceil(ratio * len(findings)))
    ordered = sorted(findings, key=lambda item: hashlib.sha1(str(item.get('id', '')).encode()).hexdigest())
    picked = ordered[:count]
    return [{'id': item['id'], 'severity': item.get('severity'), 'root_cause': key_of(item),
             'verdict': '', 'result': ''} for item in picked]


def group(findings):
    groups = {}
    for item in findings:
        groups.setdefault(key_of(item), []).append(item)
    out = []
    for index, (key, members) in enumerate(sorted(groups.items()), 1):
        out.append({'id': 'G-%02d' % index, 'root_cause': key,
                    'members': [member['id'] for member in members],
                    'severities': sorted({member.get('severity') for member in members}),
                    'count': len(members),
                    'merged': len(members) > 1})
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='action', required=True)
    m = sub.add_parser('metrics')
    m.add_argument('findings')
    m.add_argument('--from', dest='source', default='auto', choices=('auto', 'canonical', 'rdc', 'cdc', 'soc', 'lec'))
    m.add_argument('--waiver-budget', type=int, default=10)
    m.add_argument('--min-sampling', type=float, default=0.1)
    m.add_argument('--out', required=True)
    s = sub.add_parser('sample')
    s.add_argument('findings')
    s.add_argument('--from', dest='source', default='auto', choices=('auto', 'canonical', 'rdc', 'cdc', 'soc', 'lec'))
    s.add_argument('--ratio', type=float, default=0.1)
    s.add_argument('--out', required=True)
    g = sub.add_parser('group')
    g.add_argument('findings')
    g.add_argument('--from', dest='source', default='auto', choices=('auto', 'canonical', 'rdc', 'cdc', 'soc', 'lec'))
    g.add_argument('--out', required=True)
    args = parser.parse_args()
    path = Path(getattr(args, 'findings'))
    if not path.exists():
        print('ERROR: %s does not exist' % path)
        return 1
    document, findings = load(path, getattr(args, 'source', 'auto'))

    if args.action == 'metrics':
        result = metrics(findings, args.waiver_budget, args.min_sampling)
        Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print('%-10s %s' % ('gate', result['status']))
        for level in SEVERITIES:
            print('%-10s %d' % (level, result['counts'][level]))
        print('waivers   %s, closure %.0f%%, sampling %.0f%%'
              % (result['waiver_usage'], result['closure_rate'] * 100, result['sampling'] * 100))
        for reason in result['reasons']:
            print('ERROR: %s' % reason)
        for warning in result['warnings']:
            print('WARN: %s' % warning)
        print('RESULT: %s, %d finding(s), written %s'
              % (result['status'], result['findings'], args.out))
        return 0 if result['status'] == 'PASS' else 1

    if args.action == 'sample':
        entries = sample(findings, args.ratio)
        Path(args.out).write_text(json.dumps({'schema': 'vlsit-gate-audit/1', 'ratio': args.ratio,
                                              'sample': entries}, indent=2) + '\n', encoding='utf-8')
        for entry in entries:
            print('audit %-8s %-8s %s' % (entry['id'], entry['severity'], entry['root_cause'][:60]))
        print('RESULT: %d of %d finding(s) sampled, written %s' % (len(entries), len(findings), args.out))
        return 0

    grouped = group(findings)
    Path(args.out).write_text(json.dumps({'schema': 'vlsit-gate-groups/1', 'groups': grouped,
                                          'count': len(grouped)}, indent=2) + '\n', encoding='utf-8')
    for item in grouped:
        print('%-6s %-3d %-20s %s' % (item['id'], item['count'], ','.join(item['severities']),
                                      item['root_cause'][:70]))
    print('RESULT: %d finding(s) in %d group(s), written %s' % (len(findings), len(grouped), args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
