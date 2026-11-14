#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_cdc_crosscheck.py
# Function : reconcile the RTL clock model with the SDC clock and group model
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Build the crossing table and the RTL-versus-SDC mismatch list (rule R-012, R-014 to R-016).

Usage   : vlsit_cdc_crosscheck.py --rtl cdc_rtl.json --sdc cdc_sdc.json --out cdc_crossings.json
Output  : the JSON file and the crossing table.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import sys
from pathlib import Path


def groups_of(sdc):
    pairs = set()
    for group in sdc.get('groups', []):
        members = [name for part in group.get('groups', []) for name in part]
        for first in members:
            for second in members:
                pairs.add((first, second))
    return pairs


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--rtl', required=True)
    parser.add_argument('--sdc', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    rtl = json.loads(Path(args.rtl).read_text(encoding='utf-8'))
    sdc = json.loads(Path(args.sdc).read_text(encoding='utf-8'))
    flops = {flop['name']: flop for flop in rtl['flops']}
    sdc_names = {clock['name'] for clock in sdc['clocks']}

    def resolve(name):
        if name in sdc_names:
            return name
        for prefix in ('i_', 'clk_', 'c_'):
            if name.startswith(prefix) and name[len(prefix):] in sdc_names:
                return name[len(prefix):]
        for candidate in sdc_names:
            if candidate in name or name.replace('i_', '') == candidate.replace('clk_', ''):
                return candidate
        return None

    mapping = {name: resolve(name) for name in {clock['name'] for clock in rtl['clocks']}}
    async_pairs = groups_of(sdc)

    crossings, seen = [], set()
    for edge in rtl['edges']:
        source, target = flops.get(edge['from']), flops.get(edge['to'])
        if not source or not target or source['clock'] == target['clock']:
            continue
        key = (edge['from'], edge['to'])
        if key in seen:
            continue
        seen.add(key)
        left, right = mapping.get(source['clock']), mapping.get(target['clock'])
        if (left, right) in async_pairs:
            relationship = 'asynchronous' if any(group.get('asynchronous') for group in sdc['groups']) else 'synchronous group'
        elif (right, left) in async_pairs:
            relationship = 'asynchronous' if any(group.get('asynchronous') for group in sdc['groups']) else 'synchronous group'
        else:
            relationship = 'unknown (no clock group)'
        crossings.append({'id': 'X-%03d' % (len(crossings) + 1), 'signal': edge['to'],
                          'from_flop': edge['from'], 'from_clock': source['clock'],
                          'to_flop': edge['to'], 'to_clock': target['clock'],
                          'function': '', 'pulse': ('pulse' if 'pulse' in edge['to'].lower()
                                                    or 'pulse' in edge['from'].lower() else 'level'),
                          'relationship': relationship, 'mechanism': '', 'claimed': False,
                          'evidence': '%s:%d -> %s:%d' % (source['file'], source['line'],
                                                          target['file'], target['line'])})

    mismatches = []
    for name, mapped in sorted(mapping.items()):
        if mapped is None:
            mismatches.append({'kind': 'unconstrained_clock',
                               'detail': 'clock %s of the RTL has no create_clock in the SDC' % name})
    used = {mapped for mapped in mapping.values() if mapped}
    for name in sorted(sdc_names - used):
        mismatches.append({'kind': 'orphan_clock',
                           'detail': 'the SDC creates clock %s that the RTL never uses' % name})
    if not sdc['groups']:
        mismatches.append({'kind': 'no_clock_group',
                           'detail': 'the SDC has no set_clock_groups, so no pair is declared asynchronous'})

    document = {'schema': 'vlsit-cdc-crossings/1', 'clocks': rtl['clocks'],
                'crossings': crossings, 'mismatches': mismatches,
                'sdc': {'clocks': sdc['clocks'], 'groups': sdc['groups'],
                        'exceptions': sdc['exceptions']}}
    Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('%-7s %-20s %-16s %-16s %-24s %s' % ('id', 'signal', 'from clock', 'to clock',
                                               'relationship', 'evidence'))
    for crossing in crossings:
        print('%-7s %-20s %-16s %-16s %-24s %s' % (crossing['id'], crossing['signal'],
                                                   crossing['from_clock'], crossing['to_clock'],
                                                   crossing['relationship'], crossing['evidence']))
    for mismatch in mismatches:
        print('MISMATCH %-20s %s' % (mismatch['kind'], mismatch['detail']))
    print('RESULT: %d crossing(s), %d mismatch(es), written %s'
          % (len(crossings), len(mismatches), args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
