#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_rtl_top.py
# Function : build the top-down connection model of the SoC top
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Strip the comments, then extract the tree, the connections, the fanout and the functions.

Usage   : vlsit_rtl_top.py RTL_DIR --top TOP --out rtl.json [--work DIR] [--has has.json]
Output  : the JSON model, the tree, the pure-RTL count and the fanout summary.
Exit    : 0 success, 1 error.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROLE = [
    (r'ar(valid|ready|addr|id|len|size|burst)', 'axi_ar'), (r'r(valid|ready|data|resp|id|last)', 'axi_r'),
    (r'aw(valid|ready|addr|id|len|size|burst)', 'axi_aw'), (r'w(valid|ready|data|strb|last)', 'axi_w'),
    (r'b(valid|ready|resp|id)', 'axi_b'), (r'p(sel|enable|write|addr|wdata|strb|prot|ready|rdata|slverr)', 'apb'),
    (r'h(sel|addr|trans|write|size|burst|ready|rdata|resp|wdata)', 'ahb'),
    (r'a_(valid|ready|opcode|param|size|source|address|mask|data|user)', 'tlul_a'),
    (r'd_(valid|ready|opcode|param|size|source|sink|data|user|error)', 'tlul_d'),
    (r'(clk|clock)', 'clock'), (r'(rst|reset)', 'reset'), (r'(irq|int_)', 'interrupt'),
    (r'(scan|dft|test)', 'dft'), (r'(pwr|iso)', 'power'),
]
FAMILY = {'axi_ar': 'axi', 'axi_r': 'axi', 'axi_aw': 'axi', 'axi_w': 'axi', 'axi_b': 'axi',
          'apb': 'apb', 'ahb': 'ahb', 'tlul_a': 'tlul', 'tlul_d': 'tlul'}


def role_of(name):
    lowered = name.lower()
    for pattern, role in ROLE:
        if re.search(pattern, lowered):
            return role
    return 'unknown'


def strip_comments(text):
    out, index, in_string = [], 0, False
    while index < len(text):
        char, nxt = text[index], text[index + 1] if index + 1 < len(text) else ''
        if in_string:
            out.append(char)
            if char == '\\' and nxt:
                out.append(nxt)
                index += 2
                continue
            if char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
        if char == '/' and nxt == '/':
            while index < len(text) and text[index] != '\n':
                out.append(' ')
                index += 1
            continue
        if char == '/' and nxt == '*':
            end = text.find('*/', index + 2)
            end = len(text) if end < 0 else end + 2
            out.append(''.join('\n' if c == '\n' else ' ' for c in text[index:end]))
            index = end
            continue
        out.append(char)
        index += 1
    return ''.join(out)


def parse(text):
    modules, instances = [], []
    for match in re.finditer(r'^\s*module\s+(\w+)', text, re.M):
        name = match.group(1)
        line = text.count('\n', 0, match.start()) + 1
        end = re.search(r'^\s*endmodule', text[match.end():], re.M)
        body = text[match.end():match.end() + (end.start() if end else len(text))]
        ports = re.findall(r'^\s*(input|output|inout)\b[^;]*?(\w+)\s*(?:,|;|\))', body, re.M)
        modules.append({'name': name, 'line': line, 'ports': [{'name': p[1], 'direction': p[0]} for p in ports],
                        'body': body})
        for inst in re.finditer(r'^[ \t]*([A-Za-z_]\w*)\s*(?:#\s*\([^;]*?\)\s*)?([A-Za-z_]\w*)\s*\(', body, re.M | re.S):
            if inst.group(1) in ('module', 'endmodule', 'input', 'output', 'inout', 'wire', 'logic'):
                continue
            open_paren = inst.end() - 1
            depth, position = 0, open_paren
            while position < len(body):
                if body[position] == '(':
                    depth += 1
                elif body[position] == ')':
                    depth -= 1
                    if depth == 0:
                        break
                position += 1
            connections = re.findall(r'\.(\w+)\s*\(\s*([^)]*?)\s*\)', body[open_paren:position])
            instances.append({'name': inst.group(2), 'module': inst.group(1),
                              'line': line + body.count('\n', 0, inst.start()),
                              'connections': [{'port': c[0], 'net': c[1]} for c in connections]})
    return modules, instances


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('rtl')
    parser.add_argument('--top', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--work')
    parser.add_argument('--has')
    args = parser.parse_args()
    root = Path(args.rtl)
    files = [root] if root.is_file() else sorted(list(root.rglob('*.sv')) + list(root.rglob('*.v')))
    if not files:
        print('ERROR: no RTL under %s' % root)
        return 1
    work = Path(args.work) if args.work else None
    if work:
        work.mkdir(parents=True, exist_ok=True)

    modules, instances, sources = [], [], []
    for path in files:
        text = path.read_text(encoding='utf-8', errors='replace')
        cleaned = strip_comments(text)
        if work:
            (work / path.name).write_text(cleaned, encoding='utf-8')
        if cleaned.count('\n') != text.count('\n'):
            print('ERROR: %s changed its line count' % path.name)
            return 1
        found, inst = parse(cleaned)
        for module in found:
            module['file'] = path.name
            module['pure_rtl'] = len(re.findall(r'\b(always_ff|always_comb|always_latch|always)\b', module['body']))
            module['assigns'] = len(re.findall(r'\bassign\b', module['body']))
            del module['body']
        modules += found
        instances += inst
        sources.append({'path': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})

    top_module = next((m for m in modules if m['name'] == args.top), None)
    if not top_module:
        print('ERROR: top %s not found in %s' % (args.top, ', '.join(m['name'] for m in modules)))
        return 1
    top_instances = [i for i in instances if i['module'] in {m['name'] for m in modules}]
    nets = {}
    for instance in top_instances:
        for connection in instance['connections']:
            net = connection['net'].strip()
            if not re.match(r'^[A-Za-z_]\w*$', net):
                continue
            nets.setdefault(net, {'name': net, 'fanout': [], 'function_source': '', 'function_destination': ''})
            nets[net]['fanout'].append({'instance': instance['name'], 'port': connection['port'],
                                        'role': role_of(connection['port']),
                                        'function': 'port %s of %s' % (connection['port'], instance['module'])})
    for net in nets.values():
        roles = {load['role'] for load in net['fanout'] if load['role'] != 'unknown'}
        net['function_source'] = 'driver of net %s' % net['name']
        net['function_destination'] = ', '.join(sorted(roles)) or 'unknown'
    top_pure = top_module['pure_rtl'] + top_module['assigns']
    document = {'schema': 'vlsit-soc-rtl/1', 'top': args.top, 'sources': sources,
                'modules': modules, 'instances': top_instances,
                'nets': list(nets.values()), 'pure_rtl': {'statements': top_pure,
                                                          'always': top_module['pure_rtl'],
                                                          'assigns': top_module['assigns']}}
    Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('top: %s (%d ports), instances: %d' % (args.top, len(top_module['ports']), len(top_instances)))
    for instance in top_instances:
        print('  %-20s %-20s %d connection(s)' % (instance['name'], instance['module'],
                                                  len(instance['connections'])))
    for net in document['nets']:
        print('  net %-22s fanout %d  roles %s' % (net['name'], len(net['fanout']),
                                                  net['function_destination']))
    print('pure RTL in the top: %d statement(s) (always %d, assign %d)'
          % (top_pure, top_module['pure_rtl'], top_module['assigns']))
    print('RESULT: %d file(s), %d module(s), %d instance(s), %d net(s), written %s'
          % (len(files), len(modules), len(top_instances), len(document['nets']), args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
