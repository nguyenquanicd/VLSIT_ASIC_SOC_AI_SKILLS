#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_cdc_mechanism.py
# Function : assign one synchronisation mechanism to every crossing
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Classify each crossing into one CDC mechanism of the catalogue (rule R-017, R-019).

Usage   : vlsit_cdc_mechanism.py --crossings cdc_crossings.json --rtl cdc_rtl.json --out mechanisms.json
Output  : the JSON file and the mechanism table.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

FIGURES = {
    'sync_2ff': '01_2ff_synchroniser.svg',
    'pulse_toggle': '02_pulse_toggle.svg',
    'handshake': '03_handshake.svg',
    'async_fifo': '04_async_fifo.svg',
    'gray_counter': '05_gray_counter.svg',
    'mux_datapath': '06_mux_datapath.svg',
    'none': '07_no_mechanism.svg',
    'claimed': '08_claimed_mechanism.svg',
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
    targets = {chain['to'] for chain in chains}
    sources = {chain['from'] for chain in chains}
    chain_line = {chain['to']: '%s:%d' % (chain['file'], chain['line']) for chain in chains}

    per_crossing, mechanisms = {}, {}
    for crossing in crossings['crossings']:
        name = (crossing['signal'] + ' ' + crossing['from_flop'] + ' ' + crossing['to_flop']).lower()
        claimed = False
        if crossing['to_flop'] in targets or crossing['to_flop'] in sources:
            mechanism, evidence = 'sync_2ff', chain_line.get(crossing['to_flop'], crossing['evidence'])
        elif re.search(r'fifo|async_fifo', name):
            mechanism, evidence, claimed = 'async_fifo', crossing['evidence'], True
        elif re.search(r'gray|grey', name):
            mechanism, evidence, claimed = 'gray_counter', crossing['evidence'], True
        elif re.search(r'req|ack|handshake|valid.*ready', name):
            mechanism, evidence, claimed = 'handshake', crossing['evidence'], True
        elif re.search(r'toggle|pulse', name):
            mechanism, evidence, claimed = 'pulse_toggle', crossing['evidence'], True
        elif crossing.get('pulse') == 'pulse':
            mechanism, evidence = 'none', crossing['evidence']
        else:
            mechanism, evidence, claimed = 'mux_datapath', crossing['evidence'], True
        if crossing.get('pulse') == 'pulse' and mechanism == 'sync_2ff':
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
                                 'crossings': [cid for cid in per_crossing], 'evidence': [], 'claimed': 1}
    document = {'schema': 'vlsit-cdc-mechanisms/1', 'per_crossing': per_crossing,
                'mechanisms': [mechanisms[key] for key in sorted(mechanisms)]}
    Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('%-20s %-5s %-6s %s' % ('mechanism', 'n', 'claim', 'figure'))
    for entry in document['mechanisms']:
        print('%-20s %-5d %-6d %s' % (entry['name'], len(entry['crossings']), entry['claimed'], entry['figure']))
    print('RESULT: %d mechanism(s), %d crossing(s) classified'
          % (len(document['mechanisms']), len(per_crossing)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
