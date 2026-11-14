#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_conn_review.py
# Function : judge every top connection by the role of its source and destination
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Flag a protocol change, a role mismatch and an inferred role on the top connections (rule R-018 to R-022).

Usage   : vlsit_conn_review.py rtl.json --out connections.json [--has has.json]
Output  : the findings and one line per reviewed net.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import sys
from pathlib import Path

FAMILY = {'axi_ar': 'axi', 'axi_r': 'axi', 'axi_aw': 'axi', 'axi_w': 'axi', 'axi_b': 'axi',
          'apb': 'apb', 'ahb': 'ahb', 'tlul_a': 'tlul', 'tlul_d': 'tlul'}
CRITICAL_FAMILY = {('axi', 'apb'), ('axi', 'ahb'), ('apb', 'axi'), ('ahb', 'axi'),
                   ('tlul', 'apb'), ('apb', 'tlul'), ('tlul', 'axi'), ('axi', 'tlul')}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('rtl')
    parser.add_argument('--out', required=True)
    parser.add_argument('--has')
    args = parser.parse_args()
    document = json.loads(Path(args.rtl).read_text(encoding='utf-8'))
    findings = []
    for net in document['nets']:
        roles = [(load['role'], load) for load in net['fanout'] if load['role'] not in ('unknown', 'clock', 'reset')]
        families = {FAMILY.get(role) for role, _ in roles if FAMILY.get(role)}
        if len(families) >= 2:
            pair = tuple(sorted(families))[:2]
            severity = 'Critical' if pair in CRITICAL_FAMILY else 'High'
            findings.append({'id': 'C-%02d' % (len(findings) + 1), 'kind': 'protocol_change',
                             'net': net['name'], 'severity': severity,
                             'detail': 'the net joins %s and %s roles: %s'
                                       % (pair[0], pair[1], ', '.join('%s (%s)' % (role, load['instance']) for role, load in roles)),
                             'inferred': False})
        if len(families) == 1:
            names = {role for role, _ in roles}
            if len(names) > 1 and not {'ar', 'r'} <= {n[-2:] for n in names}:
                findings.append({'id': 'C-%02d' % (len(findings) + 1), 'kind': 'role_mismatch',
                                 'net': net['name'], 'severity': 'High',
                                 'detail': 'one protocol family with different roles: %s' % ', '.join(sorted(names)),
                                 'inferred': False})
        if any(load['role'] == 'unknown' for load in net['fanout']) and roles:
            findings.append({'id': 'C-%02d' % (len(findings) + 1), 'kind': 'inferred_role',
                             'net': net['name'], 'severity': 'Low',
                             'detail': 'at least one port has no role in the dictionary or the HAS',
                             'inferred': True})
    document_out = {'schema': 'vlsit-soc-connections/1', 'findings': findings,
                    'counts': {'nets': len(document['nets']), 'findings': len(findings),
                               'inferred': sum(1 for f in findings if f['inferred'])}}
    Path(args.out).write_text(json.dumps(document_out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for finding in findings:
        print('%-6s %-16s %-8s %-22s %s' % (finding['id'], finding['kind'], finding['severity'],
                                             finding['net'], finding['detail'][:70]))
    print('RESULT: %d net(s), %d finding(s), %d inferred, written %s'
          % (len(document['nets']), len(findings), document_out['counts']['inferred'], args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
