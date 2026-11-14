#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_rdc_mechanism.py
# Function : assign one reset mechanism to every crossing and collect the evidence
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Classify each crossing into one mechanism of the catalogue (rule R-017, R-019).

Purpose : the verdict depends on the mechanism, and a mechanism supported only by a name
          is marked claimed instead of accepted.
Usage   : vlsit_rdc_mechanism.py --crossings rdc_crossings.json --rtl rdc_rtl.json --out mechanisms.json
Output  : the JSON file, the mechanism table and the claimed count.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

FIGURES = {
    'sync': '01_reset_synchroniser.svg',
    'async_assert_sync_deassert': '02_async_assert_sync_deassert.svg',
    'sequencer': '03_reset_sequencer.svg',
    'crossing_flop': '04_crossing_flop.svg',
    'tree_balance': '05_reset_tree.svg',
    'none': '06_no_mechanism.svg',
    'claimed': '07_claimed_mechanism.svg',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--crossings', required=True)
    parser.add_argument('--rtl', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    crossings = json.loads(Path(args.crossings).read_text(encoding='utf-8'))
    rtl = json.loads(Path(args.rtl).read_text(encoding='utf-8'))
    chains = rtl['sync_chains']
    chain_targets = {chain['to'] for chain in chains}
    chain_sources = {chain['from'] for chain in chains}
    chain_line = {chain['to']: '%s:%d' % (chain['file'], chain['line']) for chain in chains}

    per_crossing, mechanisms = {}, {}
    for crossing in crossings['crossings']:
        name = crossing['signal'].lower()
        claimed = False
        if crossing['to_flop'] in chain_targets or crossing['to_flop'] in chain_sources:
            mechanism, evidence = 'sync', chain_line.get(crossing['to_flop'], crossing['evidence'])
        elif re.search(r'rst[_-]?sync|reset[_-]?sync', name):
            mechanism, evidence, claimed = 'sync', crossing['evidence'], True
        elif re.search(r'seq|sequenc|order', name):
            mechanism, evidence, claimed = 'sequencer', crossing['evidence'], True
        elif crossing.get('pulse') == 'pulse':
            mechanism, evidence = 'none', crossing['evidence']
        else:
            mechanism, evidence, claimed = 'crossing_flop', crossing['evidence'], True
        if crossing.get('pulse') == 'pulse' and mechanism == 'sync':
            mechanism, claimed = 'none', False
            evidence = crossing['evidence'] + ' (a two-flop chain does not carry a pulse)'
        crossing['mechanism'] = mechanism
        crossing['claimed'] = claimed
        per_crossing[crossing['id']] = mechanism
        entry = mechanisms.setdefault(mechanism, {'name': mechanism, 'figure': 'svg/' + FIGURES[mechanism],
                                                  'crossings': [], 'evidence': [], 'claimed': 0})
        entry['crossings'].append(crossing['id'])
        if evidence and evidence not in entry['evidence']:
            entry['evidence'].append(evidence)
        entry['claimed'] += 1 if claimed else 0
    if any(entry['claimed'] for entry in mechanisms.values()):
        mechanisms['claimed'] = {'name': 'claimed', 'figure': 'svg/' + FIGURES['claimed'],
                                 'crossings': [cid for cid, name in per_crossing.items()
                                               if any(entry['name'] == name and entry['claimed'] for entry in mechanisms.values())],
                                 'evidence': [], 'claimed': 1}
    document = {'schema': 'vlsit-rdc-mechanisms/1', 'per_crossing': per_crossing,
                'mechanisms': [mechanisms[key] for key in sorted(mechanisms)]}
    Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('%-28s %-6s %-6s %s' % ('mechanism', 'n', 'claim', 'figure'))
    for entry in document['mechanisms']:
        print('%-28s %-6d %-6d %s' % (entry['name'], len(entry['crossings']), entry['claimed'], entry['figure']))
    print('RESULT: %d mechanism(s), %d crossing(s) classified, %d claimed'
          % (len(document['mechanisms']), len(per_crossing),
             sum(entry['claimed'] for entry in document['mechanisms'])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
