#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_rtl_resets.py
# Function : build the reset model of an RTL design (domains, flops, chains)
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Read the RTL alone and report every reset, the flops it resets and the flop chains (rule R-010).

Purpose : the reset model is built before the SDC is opened, so the constraint file is
          checked against the RTL instead of being repeated by it.
Usage   : vlsit_rtl_resets.py RTL --out rdc_rtl.json [--ext .sv,.v]
Output  : the JSON file, the reset domain table and the chain count.
Exit    : 0 success, 1 error.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

DEFAULT_EXT = ('.sv', '.v')
FLOP = re.compile(r'^\s*([A-Za-z_]\w*)\s*<=\s*([^;]+);', re.M)
ALWAYS = re.compile(r'always_ff\s*@\s*\(([^)]*)\)|always\s*@\s*\(([^)]*)\)')


def blocks(text):
    """Yield (sensitivity, start_line, body) for every always_ff / always @ block."""
    for match in ALWAYS.finditer(text):
        sensitivity = (match.group(1) or match.group(2) or '').strip()
        start = match.end()
        line = text.count('\n', 0, match.start()) + 1
        tail = text[start:]
        begin = re.match(r'\s*begin\b', tail)
        if begin:
            depth, position = 1, start + begin.end()
            token = re.compile(r'\b(begin|end)\b')
            while depth:
                found = token.search(text, position)
                if not found:
                    break
                depth += 1 if found.group(1) == 'begin' else -1
                position = found.end()
            body = text[start + begin.end():position - 3]
            end_line = text.count('\n', 0, position)
        else:
            semi = tail.find(';')
            end = start + (semi + 1 if semi >= 0 else len(tail))
            body = text[start:end]
            end_line = text.count('\n', 0, end)
        yield sensitivity, line, end_line, body


def split_events(sensitivity):
    clocks, resets = [], []
    for event in re.split(r'\s*(?:,| or )\s*', sensitivity):
        event = event.strip()
        edge = re.match(r'(posedge|negedge)\s+([A-Za-z_]\w*)', event)
        if not edge:
            continue
        kind, name = edge.group(1), edge.group(2)
        lowered = name.lower()
        if kind == 'negedge' and ('rst' in lowered or 'reset' in lowered):
            resets.append({'name': name, 'edge': kind, 'async': True})
        elif kind == 'posedge' and 'rst' in lowered:
            resets.append({'name': name, 'edge': kind, 'async': True})
        else:
            clocks.append(name)
    return clocks, resets


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('rtl')
    parser.add_argument('--out', required=True)
    parser.add_argument('--ext', default=','.join(DEFAULT_EXT))
    args = parser.parse_args()
    root = Path(args.rtl)
    if not root.exists():
        print('ERROR: %s does not exist' % root)
        return 1
    extensions = tuple(part.strip() for part in args.ext.split(',') if part.strip())
    files = [root] if root.is_file() else [p for s in extensions for p in sorted(root.rglob('*' + s))]
    if not files:
        print('ERROR: no RTL file under %s' % root)
        return 1

    flops, resets, edges = [], {}, []
    for path in files:
        text = path.read_text(encoding='utf-8', errors='replace')
        for sensitivity, line, end_line, body in blocks(text):
            clocks, block_resets = split_events(sensitivity)
            clock = clocks[0] if clocks else ''
            reset = block_resets[0]['name'] if block_resets else ''
            if reset:
                entry = resets.setdefault(reset, {'name': reset, 'async': True, 'flops': 0,
                                                  'file': path.name, 'line': line})
                entry['flops'] += 1
            for match in FLOP.finditer(body):
                name = match.group(1)
                source = match.group(2).strip()
                source_name = re.match(r'([A-Za-z_]\w*)', source)
                flops.append({'name': name, 'clock': clock, 'reset': reset,
                              'file': path.name, 'line': line + body.count('\n', 0, match.start())})
                if source_name:
                    edges.append({'from': source_name.group(1), 'to': name,
                                  'file': path.name, 'line': line})
    unique, seen_names = [], set()
    for flop in flops:
        if flop['name'] in seen_names:
            continue
        seen_names.add(flop['name'])
        unique.append(flop)
    flops = unique
    unique_edges, seen_edges = [], set()
    for edge in edges:
        if (edge['from'], edge['to']) in seen_edges:
            continue
        seen_edges.add((edge['from'], edge['to']))
        unique_edges.append(edge)
    edges = unique_edges
    for flop in flops:
        if flop['reset'] in resets:
            resets[flop['reset']]['flops'] = sum(1 for item in flops if item['reset'] == flop['reset'])
    by_name = {flop['name']: flop for flop in flops}
    chains = []
    for edge in edges:
        source = by_name.get(edge['from'])
        target = by_name.get(edge['to'])
        if source and target and source['clock'] == target['clock'] and source['reset'] == target['reset']:
            chains.append({'from': edge['from'], 'to': edge['to'], 'clock': target['clock'],
                           'reset': target['reset'], 'file': edge['file'], 'line': edge['line']})
    domains = {}
    for flop in flops:
        domains.setdefault(flop['reset'] or '(none)', []).append(flop['name'])
    document = {'schema': 'vlsit-rdc-rtl/1',
                'files': [{'path': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
                'resets': sorted(resets.values(), key=lambda item: item['name']),
                'domains': [{'name': name, 'reset': name, 'flops': sorted(names)}
                            for name, names in sorted(domains.items())],
                'flops': flops, 'edges': edges, 'sync_chains': chains}
    Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('%-24s %-6s %-6s %s' % ('reset domain', 'async', 'flops', 'source'))
    for reset in document['resets']:
        print('%-24s %-6s %-6d %s:%d' % (reset['name'], reset['async'], reset['flops'],
                                         reset['file'], reset['line']))
    print('flops: %d, flop-to-flop edges: %d, chains of two or more: %d'
          % (len(flops), len(edges), sum(1 for _ in chains)))
    print('RESULT: %d file(s), %d reset domain(s), %d flop(s), written %s'
          % (len(files), len(document['resets']), len(flops), args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
