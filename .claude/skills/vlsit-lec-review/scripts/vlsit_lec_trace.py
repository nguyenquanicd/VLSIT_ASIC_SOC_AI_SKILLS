#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_lec_trace.py
# Function : trace the cone of the first failing compare points on both sides
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Build the reference and implementation cones of the first N fails (rule R-024, R-025).

Usage   : vlsit_lec_trace.py lec_log.json --rtl RTL_DIR --netlist NET.v --limit 5 --out lec_trace.json
Output  : the trace model and one line per traced fail.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

CELLS = [('AND', '&'), ('OR', '|'), ('XOR', '^'), ('NAND', 'nand'), ('NOR', 'nor'),
         ('INV', '~'), ('NOT', '~'), ('BUF', 'buf'), ('MUX', 'mux'), ('DFF', 'dff'),
         ('TIEHI', '1'), ('TIELO', '0')]
IDENT = re.compile(r'[A-Za-z_]\w*')


def base(name):
    name = name.split('/')[-1].split('.')[-1]
    return re.sub(r'\[[^\]]*\]', '', name)


def identifiers(expr):
    found = []
    for token in IDENT.findall(expr):
        if token.lower() in ('and', 'or', 'not', 'if', 'else', 'posedge', 'negedge'):
            continue
        if token not in found:
            found.append(token)
    return found


def parse_rtl(paths):
    drivers, inputs = {}, {}
    for path in paths:
        text = path.read_text(encoding='utf-8', errors='replace')
        for line_no, line in enumerate(text.splitlines(), 1):
            stripped = line.split('//', 1)[0].strip()
            port = re.match(r'^(input|output|inout)\b.*?([A-Za-z_]\w*)\s*[,;]?$', stripped)
            if port:
                inputs[port.group(2)] = {'direction': port.group(1), 'file': path.name, 'line': line_no}
            assign = re.match(r'^assign\s+([A-Za-z_]\w*)\s*=\s*(.+);$', stripped)
            if assign:
                drivers[assign.group(1)] = {'expr': assign.group(2), 'file': path.name, 'line': line_no}
            flop = re.match(r'^([A-Za-z_]\w*)\s*<=\s*(.+);$', stripped)
            if flop:
                drivers.setdefault(flop.group(1), {'expr': flop.group(2), 'file': path.name, 'line': line_no})
    return drivers, inputs


def cell_expr(cell, ports):
    kind = next((value for name, value in CELLS if cell.upper().startswith(name)), 'unknown')
    by_name = {key.upper(): value for key, value in ports.items()}
    if kind in ('&', '|', '^'):
        args = [value for key, value in by_name.items() if key in ('A', 'B', 'C', 'D')]
        return '(%s)' % (' %s ' % kind).join(args) if args else None
    if kind in ('nand', 'nor'):
        operator = '&' if kind == 'nand' else '|'
        args = [value for key, value in by_name.items() if key in ('A', 'B', 'C', 'D')]
        return '~(%s)' % (' %s ' % operator).join(args) if args else None
    if kind in ('~', 'buf'):
        value = by_name.get('A') or by_name.get('I')
        return ('~%s' % value) if kind == '~' and value else value
    if kind == 'mux':
        select = by_name.get('S') or by_name.get('SEL')
        first = by_name.get('A') or by_name.get('I0')
        second = by_name.get('B') or by_name.get('I1')
        return '(%s ? %s : %s)' % (select, first, second) if select and first and second else None
    if kind == 'dff':
        return by_name.get('D') or by_name.get('DATA')
    if kind in ('0', '1'):
        return kind
    return None


def parse_netlist(path):
    drivers, inputs = {}, {}
    text = path.read_text(encoding='utf-8', errors='replace')
    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.split('//', 1)[0].strip()
        port = re.match(r'^(input|output|inout)\b.*?([A-Za-z_]\w*)\s*[,;)]?$', stripped)
        if port:
            inputs[port.group(2)] = {'direction': port.group(1), 'file': path.name, 'line': line_no}
        assign = re.match(r'^assign\s+([A-Za-z_]\w*)\s*=\s*(.+);$', stripped)
        if assign:
            drivers[assign.group(1)] = {'expr': assign.group(2), 'file': path.name, 'line': line_no}
        cell = re.match(r'^([A-Za-z_]\w*)\s+(?:#\s*\([^)]*\)\s*)?([A-Za-z_]\w*)\s*\((.*)\)\s*;$', stripped)
        if not cell or cell.group(1) in ('module', 'endmodule', 'input', 'output', 'wire', 'reg'):
            continue
        ports = dict(re.findall(r'\.(\w+)\s*\(\s*([^)]*?)\s*\)', cell.group(3)))
        expression = cell_expr(cell.group(1), ports)
        output = ports.get('Y') or ports.get('Q') or ports.get('Z') or ports.get('ZN')
        if expression and output:
            drivers[base(output)] = {'expr': expression, 'file': path.name, 'line': line_no}
    return drivers, inputs


def cone(signal, drivers, depth=0, seen=None, steps=None):
    seen = seen if seen is not None else set()
    steps = steps if steps is not None else []
    name = base(signal)
    if name in seen or depth > 12:
        return {'name': name, 'expr': name, 'inputs': [], 'file': '', 'line': 0}
    seen.add(name)
    driver = drivers.get(name)
    if not driver:
        return {'name': name, 'expr': name, 'inputs': [], 'file': '', 'line': 0}
    node = {'name': name, 'expr': driver['expr'], 'file': driver['file'], 'line': driver['line'],
            'inputs': []}
    for child in identifiers(driver['expr']):
        child_node = cone(child, drivers, depth + 1, seen, steps)
        node['inputs'].append(child_node)
        steps.append({'side': '', 'from': name, 'to': child,
                      'file': driver['file'], 'line': driver['line']})
    return node


def leaves(node, found=None):
    found = found if found is not None else []
    if not node['inputs']:
        if node['name'] not in found:
            found.append(node['name'])
        return found
    for child in node['inputs']:
        leaves(child, found)
    return found


def expand(node):
    expr = node['expr']
    for child in node['inputs']:
        expr = re.sub(r'\\b%s\\b' % re.escape(child['name']), '(%s)' % expand(child), expr)
    return expr


def count(node):
    return 1 + sum(count(child) for child in node['inputs'])


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('log')
    parser.add_argument('--rtl', required=True)
    parser.add_argument('--netlist', required=True)
    parser.add_argument('--limit', type=int, default=5)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    log = json.loads(Path(args.log).read_text(encoding='utf-8'))
    rtl_root = Path(args.rtl)
    rtl_files = [rtl_root] if rtl_root.is_file() else sorted(rtl_root.rglob('*.sv')) + sorted(rtl_root.rglob('*.v'))
    rtl_drivers, rtl_inputs = parse_rtl(rtl_files)
    net_drivers, net_inputs = parse_netlist(Path(args.netlist))

    traced = []
    for fail in log['fails'][:args.limit]:
        reference = cone(fail['ref'], rtl_drivers)
        implementation = cone(fail['impl'], net_drivers)
        steps = []
        for side, node, source in (('rtl', reference, rtl_drivers), ('netlist', implementation, net_drivers)):
            stack = [node]
            while stack:
                current = stack.pop()
                for child in current['inputs']:
                    steps.append({'side': side, 'from': current['name'], 'to': child['name'],
                                  'file': current['file'], 'line': current['line']})
                    stack.append(child)
        traced.append({'id': fail['id'], 'compare_point': fail['compare_point'],
                       'ref': fail['ref'], 'impl': fail['impl'],
                       'ref_cone': reference, 'impl_cone': implementation,
                       'ref_nodes': count(reference), 'impl_nodes': count(implementation),
                       'ref_inputs': leaves(reference), 'impl_inputs': leaves(implementation),
                       'opaque': count(reference) == 1 or count(implementation) == 1,
                       'steps': steps, 'log_line': fail['line'],
                       'ref_expr': expand(reference), 'impl_expr': expand(implementation)})
    document = {'schema': 'vlsit-lec-trace/1', 'limit': args.limit,
                'total_fails': len(log['fails']), 'traced': len(traced),
                'remaining': max(0, len(log['fails']) - len(traced)), 'fails': traced}
    Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for fail in traced:
        print('%-5s %-30s rtl nodes %-3d netlist nodes %-3d%s'
              % (fail['id'], fail['compare_point'], fail['ref_nodes'], fail['impl_nodes'],
                 ' (opaque)' if fail['opaque'] else ''))
    print('RESULT: %d of %d fail(s) traced, %d remaining, written %s'
          % (len(traced), len(log['fails']), document['remaining'], args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
