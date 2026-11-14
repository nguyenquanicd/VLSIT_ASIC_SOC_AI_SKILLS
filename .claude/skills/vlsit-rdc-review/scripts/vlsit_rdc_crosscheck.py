#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_rdc_crosscheck.py
# Function : reconcile the RTL reset model with the SDC constraint model
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Build the crossing table and the RTL-versus-SDC mismatch list (rule R-012, R-014 to R-016).

Purpose : a crossing is a flop-to-flop edge whose two ends have different resets, and a
          mismatch is a domain the SDC does not constrain or an exception that names no
          reset.
Usage   : vlsit_rdc_crosscheck.py --rtl rdc_rtl.json --sdc rdc_sdc.json --out rdc_crossings.json
Output  : the JSON file, the crossing table and the mismatch count.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--rtl', required=True)
    parser.add_argument('--sdc', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    rtl = json.loads(Path(args.rtl).read_text(encoding='utf-8'))
    sdc = json.loads(Path(args.sdc).read_text(encoding='utf-8'))

    flops = {flop['name']: flop for flop in rtl['flops']}
    crossings, seen = [], set()
    for edge in rtl['edges']:
        source = flops.get(edge['from'])
        target = flops.get(edge['to'])
        if not source or not target:
            continue
        if source['reset'] == target['reset'] and source['clock'] == target['clock']:
            continue
        key = (edge['from'], edge['to'])
        if key in seen:
            continue
        seen.add(key)
        relationship = 'asynchronous' if source['reset'] != target['reset'] else 'same reset, different clock'
        crossings.append({
            'id': 'X-%03d' % (len(crossings) + 1),
            'signal': edge['to'],
            'from_flop': edge['from'], 'from_domain': source['reset'] or '(none)',
            'from_clock': source['clock'],
            'to_flop': edge['to'], 'to_domain': target['reset'] or '(none)',
            'to_clock': target['clock'],
            'function': '', 'pulse': ('pulse' if 'pulse' in edge['to'].lower() or 'pulse' in edge['from'].lower() else 'level'), 'relationship': relationship,
            'mechanism': '', 'claimed': False,
            'evidence': '%s:%d' % (source['file'], source['line']) + ' -> ' + '%s:%d' % (target['file'], target['line']),
        })

    reset_names = {reset['name'] for reset in rtl['resets']}
    sdc_reset_names = {ref['name'] for ref in sdc['reset_refs']}
    sdc_clock_names = {clock['name'] for clock in sdc['clocks']}
    rtl_clock_names = {flop['clock'] for flop in rtl['flops'] if flop['clock']}
    mismatches = []
    for name in sorted(reset_names - sdc_reset_names):
        mismatches.append({'kind': 'unconstrained_domain', 'detail': 'reset %s has no exception in the SDC' % name,
                           'line': None})
    for name in sorted(sdc_reset_names - reset_names):
        mismatches.append({'kind': 'orphan_exception', 'detail': 'the SDC names %s but the RTL has no such reset' % name,
                           'line': None})
    if not sdc_clock_names:
        mismatches.append({'kind': 'group_mismatch', 'detail': 'the SDC defines no clock', 'line': None})
    elif len(sdc_clock_names) < len(rtl_clock_names):
        mismatches.append({'kind': 'group_mismatch',
                           'detail': 'the RTL uses %d clock(s) and the SDC defines %d'
                                     % (len(rtl_clock_names), len(sdc_clock_names)), 'line': None})
    for group in sdc['groups']:
        if group['asynchronous'] and len(group['groups']) < 2:
            mismatches.append({'kind': 'group_mismatch',
                               'detail': 'an asynchronous clock group at line %d has fewer than two groups' % group['line'],
                               'line': group['line']})

    document = {'schema': 'vlsit-rdc-crossings/1',
                'domains': rtl['domains'], 'resets': rtl['resets'],
                'crossings': crossings, 'mismatches': mismatches,
                'sdc': {'clocks': sdc['clocks'], 'groups': sdc['groups'],
                        'exceptions': sdc['exceptions'], 'reset_refs': sdc['reset_refs']}}
    Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    print('%-7s %-22s %-18s %-18s %-13s %s' % ('id', 'signal', 'from domain', 'to domain', 'relationship', 'evidence'))
    for crossing in crossings:
        print('%-7s %-22s %-18s %-18s %-13s %s' % (crossing['id'], crossing['signal'],
                                                   crossing['from_domain'], crossing['to_domain'],
                                                   crossing['relationship'], crossing['evidence']))
    for mismatch in mismatches:
        print('MISMATCH %-20s %s' % (mismatch['kind'], mismatch['detail']))
    print('RESULT: %d crossing(s), %d mismatch(es), written %s' % (len(crossings), len(mismatches), args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
