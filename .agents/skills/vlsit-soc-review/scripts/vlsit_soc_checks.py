#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_soc_checks.py
# Function : tie, pulse and destination-limit checks on the top connection model
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Run the tie, pulse or limit check on rtl.json (rule R-023, R-024, R-025).

Usage   : vlsit_soc_checks.py tie   rtl.json --out ties.json
          vlsit_soc_checks.py pulse rtl.json [--has has.json] --out pulses.json
          vlsit_soc_checks.py limit rtl.json [--has has.json] --out limits.json
Output  : the findings and the summary line.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

PULSE = re.compile(r'(pulse|tog|evt|event|ack|done|valid)', re.I)
LEVEL = re.compile(r'(level|en|mode|cfg|stat|mask|ready|sel)', re.I)
LIMIT = {'axi': 'one outstanding per channel by default; check the ID width and the data width',
         'apb': 'one transfer at a time; PREADY must come within the wait limit',
         'ahb': 'one outstanding transfer; HREADYOUT must be driven every cycle',
         'tlul': 'A and D channel order is fixed; the size is a power of two bytes'}
TIE = re.compile(r"^(1'b[01]|'[01]|0|1|[0-9]+'[bdh][0-9a-fA-F_]+)$")


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='action', required=True)
    for name in ('tie', 'pulse', 'limit'):
        item = sub.add_parser(name)
        item.add_argument('rtl')
        item.add_argument('--out', required=True)
        item.add_argument('--has')
    args = parser.parse_args()
    document = load(args.rtl)
    findings = []

    if args.action == 'tie':
        for instance in document['instances']:
            connected = {connection['port'] for connection in instance['connections']}
            for connection in instance['connections']:
                net = connection['net'].strip()
                if net in ('', "1'b0", "1'b1", "'0", "'1", '0', '1') or TIE.match(net):
                    findings.append({'id': 'T-%02d' % (len(findings) + 1), 'kind': 'tie',
                                     'signal': connection['port'], 'instance': instance['name'],
                                     'value': net or 'unconnected', 'severity': 'High',
                                     'detail': 'the %s input of %s is tied to %s'
                                               % (connection['port'], instance['name'], net or 'nothing')})
            for port in [p for p in instance.get('ports', []) if p['direction'] == 'input']:
                if port['name'] not in connected:
                    findings.append({'id': 'T-%02d' % (len(findings) + 1), 'kind': 'float',
                                     'signal': port['name'], 'instance': instance['name'],
                                     'value': 'floating', 'severity': 'Critical',
                                     'detail': 'the input %s of %s has no connection'
                                               % (port['name'], instance['name'])})
    elif args.action == 'pulse':
        for net in document['nets']:
            name = net['name']
            if PULSE.search(name):
                kind = 'pulse'
            elif LEVEL.search(name):
                kind = 'level'
            else:
                continue
            severity = 'Medium'
            detail = '%s is classified %s' % (name, kind)
            if kind == 'pulse' and 'ready' in name:
                severity, detail = 'High', '%s looks like a pulse but is used as a ready handshake' % name
            findings.append({'id': 'P-%02d' % (len(findings) + 1), 'kind': kind, 'signal': name,
                             'severity': severity, 'detail': detail,
                             'capture': 'unknown without the destination clock frequency'})
    else:
        for net in document['nets']:
            roles = {load_item['role'] for load_item in net['fanout']}
            for role in roles:
                family = role.split('_')[0]
                if family in LIMIT and len(net['fanout']) > 1:
                    findings.append({'id': 'L-%02d' % (len(findings) + 1), 'kind': 'limit',
                                     'signal': net['name'], 'severity': 'Medium',
                                     'detail': '%s limit: %s' % (family, LIMIT[family])})

    document_out = {'schema': 'vlsit-soc-checks/1', 'action': args.action,
                    'findings': findings, 'count': len(findings)}
    Path(args.out).write_text(json.dumps(document_out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for finding in findings:
        print('%-6s %-8s %-22s %-8s %s' % (finding['id'], finding['kind'], finding['signal'],
                                            finding['severity'], finding['detail'][:70]))
    print('RESULT: %s check, %d finding(s), written %s' % (args.action, len(findings), args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
