#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_rtl_clocks.py
# Function : build the clock domain model of an RTL design
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Read the RTL alone and report every clock, its flops, the flop chains and the domains (rule R-010).

Usage   : vlsit_rtl_clocks.py RTL --out cdc_rtl.json [--ext .sv,.v]
Output  : the JSON file, the clock table and the chain count.
Exit    : 0 success, 1 error.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

DEFAULT_EXT = ('.sv', '.v')
FLOP = re.compile(r'^[ \t]*([A-Za-z_]\w*)\s*<=\s*([^;]+);', re.M)
ALWAYS = re.compile(r'always_ff\s*@\s*\(([^)]*)\)|always\s*@\s*\(([^)]*)\)')


def blocks(text):
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
        edge = re.match(r'(posedge|negedge)\s+([A-Za-z_]\w*)', event.strip())
        if not edge:
            continue
        kind, name = edge.group(1), edge.group(2)
        if 'rst' in name.lower() or 'reset' in name.lower():
            resets.append(name)
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

    flops, clocks, edges = [], {}, []
    for path in files:
        text = path.read_text(encoding='utf-8', errors='replace')
        for sensitivity, line, end_line, body in blocks(text):
            clock_names, resets = split_events(sensitivity)
            clock = clock_names[0] if clock_names else ''
            reset = resets[0] if resets else ''
            if clock:
                clocks.setdefault(clock, {'name': clock, 'flops': 0, 'file': path.name, 'line': line,
                                          'resets': set()})
                if reset:
                    clocks[clock]['resets'].add(reset)
            for match in FLOP.finditer(body):
                name = match.group(1)
                source = match.group(2).strip()
                source_name = re.match(r'([A-Za-z_]\w*)', source)
                flops.append({'name': name, 'clock': clock, 'reset': reset, 'file': path.name,
                              'line': line + body.count('\n', 0, match.start())})
                if source_name:
                    edges.append({'from': source_name.group(1), 'to': name, 'file': path.name, 'line': line})
    unique, seen = [], set()
    for flop in flops:
        if flop['name'] in seen:
            continue
        seen.add(flop['name'])
        unique.append(flop)
    flops = unique
    for clock in clocks.values():
        clock['flops'] = sum(1 for flop in flops if flop['clock'] == clock['name'])
        clock['resets'] = sorted(clock['resets'])
    by_name = {flop['name']: flop for flop in flops}
    chains = []
    for edge in edges:
        source, target = by_name.get(edge['from']), by_name.get(edge['to'])
        if source and target and source['clock'] == target['clock']:
            chains.append({'from': edge['from'], 'to': edge['to'], 'clock': target['clock'],
                           'file': edge['file'], 'line': edge['line']})
    document = {'schema': 'vlsit-cdc-rtl/1',
                'files': [{'path': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
                'clocks': sorted(clocks.values(), key=lambda item: item['name']),
                'flops': flops, 'edges': edges, 'sync_chains': chains}
    Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('%-24s %-6s %-6s %s' % ('clock domain', 'flops', 'async', 'source'))
    for clock in document['clocks']:
        print('%-24s %-6d %-6s %s:%d' % (clock['name'], clock['flops'], 'n/a',
                                         clock['file'], clock['line']))
    print('flops: %d, flop-to-flop edges: %d, chains of two or more: %d'
          % (len(flops), len(edges), len(chains)))
    print('RESULT: %d file(s), %d clock domain(s), %d flop(s), written %s'
          % (len(files), len(document['clocks']), len(flops), args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
