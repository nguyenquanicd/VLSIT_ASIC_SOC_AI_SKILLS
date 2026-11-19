#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_gate_model.py
# Function : derive gates, blocks and clusters from RTL expressions, then lay them out
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Turn the assignments of every module into a gate netlist and lay it out (rule R-012 to R-017).

Purpose : one gate per operator, one rectangle per child instance and per construct that
          has no gate form, clusters of at most 100 symbols, and a layered layout whose
          crossing count is printed before and after the ordering passes.
Usage   : vlsit_gate_model.py build SCAN.json --hierarchy hierarchy.json --out gates.json
          vlsit_gate_model.py layout gates.json --out layout.json [--max 100]
Output  : the JSON file and a summary line per cluster.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

BINARY = ['||', '&&', '|', '^', '&', '==', '!=', '<=', '>=', '<', '>', '<<', '>>', '+', '-', '*', '/', '%']
KIND = {'&': 'and', '|': 'or', '^': 'xor', '&&': 'and', '||': 'or', '?': 'mux', '~': 'not', '!': 'not',
        '+': 'add', '==': 'cmp', '!=': 'cmp', '<': 'cmp', '>': 'cmp', '<=': 'cmp', '>=': 'cmp'}


def strip_outer(text):
    text = text.strip()
    while text.startswith('(') and text.endswith(')'):
        depth, inner_ok = 0, True
        for index, char in enumerate(text):
            depth += 1 if char == '(' else -1 if char == ')' else 0
            if depth == 0 and index != len(text) - 1:
                inner_ok = False
                break
        if not inner_ok:
            break
        text = text[1:-1].strip()
    return text


def split_op(text, operator):
    """Split at every occurrence of operator outside brackets; None when there is none."""
    parts, depth, start, index = [], 0, 0, 0
    while index < len(text):
        char = text[index]
        if char in '([{':
            depth += 1
        elif char in ')]}':
            depth -= 1
        elif depth == 0 and text.startswith(operator, index):
            before = text[index - 1] if index else ''
            after = text[index + len(operator)] if index + len(operator) < len(text) else ''
            if operator in ('|', '&') and (before == operator or after == operator):
                index += 1
                continue
            parts.append(text[start:index])
            start = index + len(operator)
            index = start
            continue
        index += 1
    if not parts:
        return None
    parts.append(text[start:])
    return [part.strip() for part in parts]


def find_colon(text):
    depth = 0
    for index, char in enumerate(text):
        if char in '([{':
            depth += 1
        elif char in ')]}':
            depth -= 1
        elif char == ':' and depth == 0:
            return index
    return -1


IDENT = re.compile(r'^[A-Za-z_]\w*(?:\[[^\]]*\])?$')
NUMBER = re.compile(r"^(?:\d[\d_]*)?'[sS]?[bodhBODH][0-9a-fA-FxXzZ_]+$|^'[01xXzZ]$|^\d[\d_]*$")


def parse(expression):
    text = strip_outer(expression)
    position = split_op(text, '?')
    if position and len(position) == 2:
        colon = find_colon(position[1])
        if colon >= 0:
            return {'op': '?', 'args': [parse(position[0]), parse(position[1][:colon]), parse(position[1][colon + 1:])]}
    for operator in BINARY:
        parts = split_op(text, operator)
        if parts and len(parts) > 1:
            return {'op': operator, 'args': [parse(part) for part in parts]}
    if text.startswith('~'):
        return {'op': '~', 'args': [parse(text[1:])]}
    if text.startswith('!'):
        return {'op': '!', 'args': [parse(text[1:])]}
    if IDENT.match(text):
        return {'wire': text}
    if NUMBER.match(text):
        return {'const': text}
    return {'block': text}


class Builder:
    def __init__(self, module, hierarchy_module):
        self.module = module
        self.hierarchy = hierarchy_module
        self.nodes = []
        self.producers = {}
        self.pads = {}
        self.counter = 0
        self.signal_refs = []
        for port in hierarchy_module.get('ports', []):
            node = self.add('pad', port['name'], 1, port.get('line') or hierarchy_module['line'],
                            'port %s %s' % (port.get('direction', ''), port.get('width', '')))
            self.pads[port['name']] = node['id']
            node['direction'] = port.get('direction', 'input')
            node['width'] = port.get('width', '1')

    def add(self, kind, label, width, line, note=''):
        self.counter += 1
        node = {'id': 'n%d' % self.counter, 'kind': kind, 'label': label, 'width': width,
                'file': self.hierarchy['file'], 'line': line, 'note': note, 'inputs': []}
        self.nodes.append(node)
        return node

    def emit(self, ast, line, cluster, counter):
        if 'wire' in ast:
            return ('wire', ast['wire'])
        if 'const' in ast:
            node = self.add('const', ast['const'], 1, line, 'constant')
            node['cluster'] = cluster
            return ('node', node['id'])
        if 'block' in ast:
            node = self.add('block', ast['block'][:40], 1, line, 'construct without a gate form')
            node['cluster'] = cluster
            return ('node', node['id'])
        operator = ast.get('op')
        children = [self.emit(child, line, cluster, counter) for child in ast.get('args', [])]
        if operator == '?':
            kind = 'mux'
        else:
            kind = KIND.get(operator, 'block')
        if kind == 'block':
            node = self.add('block', (operator or '?') + ' (' + str(len(children)) + ' inputs)', 1, line,
                            'operator without a gate form')
        else:
            node = self.add(kind, operator, 1, line)
        node['cluster'] = cluster
        node['inputs'] = children
        return ('node', node['id'])

    def assignment(self, lhs, rhs, line, cluster):
        ast = parse(rhs)
        result = self.emit(ast, line, cluster, None)
        node_id = result[1] if result[0] == 'node' else None
        if node_id:
            self.producers[lhs.split('[')[0].strip()] = node_id
            self.nodes[[n['id'] for n in self.nodes].index(node_id)]['output'] = lhs
        return node_id

    def resolve(self):
        for node in self.nodes:
            resolved = []
            for kind, name in node.get('inputs', []):
                if kind == 'node':
                    resolved.append(name)
                else:
                    base = name.split('[')[0].strip()
                    if base in self.producers:
                        resolved.append(self.producers[base])
                    elif base in self.pads:
                        resolved.append(self.pads[base])
                    else:
                        const = self.add('wire', base, 1, node['line'], 'signal without a driver')
                        const['cluster'] = node.get('cluster')
                        const['kind'] = 'text'
                        resolved.append(const['id'])
            node['inputs'] = resolved
        for port in self.hierarchy.get('ports', []):
            if port.get('direction') != 'output':
                continue
            pad_id = self.pads.get(port['name'])
            producer = self.producers.get(port['name'])
            if pad_id and producer:
                for node in self.nodes:
                    if node['id'] == pad_id:
                        node['inputs'] = [producer]
                        break


def build(scan, hierarchy, max_symbols, merge_min=6):
    scan_modules = {module['name']: module for module in scan['modules']}
    clusters = []
    for module in hierarchy['modules']:
        raw = scan_modules.get(module['name'], {})
        builder = Builder(raw, module)
        counter = 0
        for index, block in enumerate(raw.get('always_comb', [])):
            cluster = 'comb%d' % index
            for assignment in block['assignments']:
                counter += 1
                builder.assignment(assignment['lhs'], assignment['rhs'], assignment['line'], cluster)
        for index, block in enumerate(raw.get('always_ff', [])):
            cluster = 'seq%d' % index
            for assignment in block['assignments']:
                counter += 1
                builder.assignment(assignment['lhs'], assignment['rhs'], assignment['line'], cluster)
        for index, assignment in enumerate(raw.get('assigns', [])):
            counter += 1
            builder.assignment(assignment['lhs'], assignment['rhs'], assignment['line'], 'assign%d' % index)
        for index, instance in enumerate(module.get('instances', [])):
            node = builder.add('instance', '%s\n(%s)' % (instance['name'], instance['module']),
                               1, instance['line'], 'child module')
            node['cluster'] = 'inst%d' % index
            node['inputs'] = [('wire', connection['signal']) for connection in instance['connections']
                              if connection.get('port')]
            node['instance'] = instance['name']
        builder.resolve()

        parent = {node['id']: node['id'] for node in builder.nodes}

        def find(item):
            while parent[item] != item:
                parent[item] = parent[parent[item]]
                item = parent[item]
            return item

        def union(first, second):
            root_first, root_second = find(first), find(second)
            if root_first != root_second:
                parent[root_second] = root_first

        for node in builder.nodes:
            for source in node.get('inputs', []):
                union(source, node['id'])
        groups = {}
        for node in builder.nodes:
            groups.setdefault(find(node['id']), []).append(node)
        ordered_groups = [groups[key] for key in sorted(groups, key=lambda key: min(
            int(node['id'][1:]) for node in groups[key]))]

        split_groups = []
        for nodes in ordered_groups:
            instances = [node for node in nodes if node['kind'] == 'instance']
            if len(instances) < 2:
                split_groups.append(nodes)
                continue
            for instance in instances:
                sources = [node for node in nodes
                           if node['id'] in instance.get('inputs', [])]
                part = [instance] + sources
                split_groups.append(part)
        ordered_groups = split_groups
        small = [group for group in ordered_groups if len(group) < merge_min]
        if small:
            ordered_groups = [group for group in ordered_groups if len(group) >= merge_min]
            merged = [node for group in small for node in group]
            if merged:
                ordered_groups.append(merged)

        for index, nodes in enumerate(ordered_groups, 1):
            if all(node['kind'] in ('pad', 'text', 'const') for node in nodes) and not any(
                    edge['to'] in {node['id'] for node in nodes} for edge in
                    [{'to': source} for node in nodes for source in node.get('inputs', [])]):
                continue
            name = 'inst' if any(node['kind'] == 'instance' for node in nodes) else 'logic%d' % index
            if not nodes:
                continue
            chunks = [nodes] if len(nodes) <= max_symbols else [
                nodes[i:i + max_symbols] for i in range(0, len(nodes), max_symbols)]
            for part, chunk in enumerate(chunks, 1):
                suffix = '' if len(chunks) == 1 else '_%d' % part
                ids = {node['id'] for node in chunk}
                edges = [{'from': source, 'to': node['id']}
                         for node in chunk for source in node.get('inputs', [])]
                clusters.append({
                    'module': module['name'], 'cluster': name + suffix,
                    'title': '%s - %s%s' % (module['name'], name, suffix),
                    'file': module['file'], 'line': module['line'],
                    'symbols': len(chunk),
                    'nodes': [{k: v for k, v in node.items() if k != 'inputs'} for node in chunk],
                    'edges': [edge for edge in edges if edge['to'] in ids],
                    'cross_cluster': [edge for edge in edges if edge['from'] not in ids],
                })
    return {'schema': 'vlsit-gates/1', 'design': hierarchy['design'], 'top': hierarchy['top'],
            'source': hierarchy['source'], 'clusters': clusters}


def layer_nodes(cluster):
    nodes = {node['id']: dict(node, layer=0) for node in cluster['nodes']}
    incoming = {node_id: [] for node_id in nodes}
    for edge in cluster['edges']:
        if edge['to'] in nodes:
            incoming[edge['to']].append(edge['from'])
    changed = True
    guard = 0
    while changed and guard < 200:
        changed, guard = False, guard + 1
        for node_id, sources in incoming.items():
            depth = max([nodes[source]['layer'] + 1 for source in sources if source in nodes] + [0])
            if depth != nodes[node_id]['layer'] and depth < 100:
                nodes[node_id]['layer'] = depth
                changed = True
    return nodes, incoming


def crossings(layers, incoming):
    count = 0
    ids = [[node['id'] for node in layer] for layer in layers]
    for index in range(len(ids) - 1):
        left, right = ids[index], ids[index + 1]
        pairs = []
        for position, node_id in enumerate(right):
            for source in incoming.get(node_id, []):
                if source in left:
                    pairs.append((left.index(source), position))
        for first in range(len(pairs)):
            for second in range(first + 1, len(pairs)):
                if (pairs[first][0] - pairs[second][0]) * (pairs[first][1] - pairs[second][1]) < 0:
                    count += 1
    return count


def order_pass(layers, incoming, outgoing, direction):
    index_of = {node['id']: position for layer in layers for position, node in enumerate(layer)}
    ordered = []
    sequence = layers if direction == 'down' else list(reversed(layers))
    for layer in sequence:
        def key(node):
            neighbours = incoming.get(node['id'], []) if direction == 'down' else outgoing.get(node['id'], [])
            values = [index_of[other] for other in neighbours if other in index_of]
            return sum(values) / len(values) if values else index_of[node['id']]
        ordered.append(sorted(layer, key=key))
    return ordered if direction == 'down' else list(reversed(ordered))


def layout(document, max_symbols):
    out = []
    for cluster in document['clusters']:
        nodes, incoming = layer_nodes(cluster)
        outgoing = {}
        for edge in cluster['edges']:
            outgoing.setdefault(edge['from'], []).append(edge['to'])
        depth = max([node['layer'] for node in nodes.values()] + [0])
        layers = [[] for _ in range(depth + 1)]
        for node in sorted(nodes.values(), key=lambda n: n['id']):
            layers[node['layer']].append(node)
        best = [list(layer) for layer in layers]
        best_crossings = crossings(layers, incoming)
        start = best_crossings
        for _ in range(3):
            for direction in ('down', 'up'):
                candidate = order_pass(best, incoming, outgoing, direction)
                value = crossings(candidate, incoming)
                if value < best_crossings:
                    best, best_crossings = candidate, value
        for layer_index, layer in enumerate(best):
            for order_index, node in enumerate(layer):
                node['x'] = 40 + layer_index * 220
                node['y'] = 40 + order_index * 90
                node['layer'] = layer_index
                node['order'] = order_index
        out.append({'module': cluster['module'], 'cluster': cluster['cluster'],
                    'title': cluster['title'], 'file': cluster['file'],
                    'nodes': [node for layer in best for node in layer],
                    'edges': cluster['edges'], 'cross_cluster': cluster['cross_cluster'],
                    'crossings': best_crossings, 'crossings_before': start,
                    'symbols': len(cluster['nodes'])})
    return {'schema': 'vlsit-layout/1', 'design': document['design'], 'top': document['top'],
            'source': document['source'], 'clusters': out}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='action', required=True)
    b = sub.add_parser('build')
    b.add_argument('scan')
    b.add_argument('--hierarchy', required=True)
    b.add_argument('--out', required=True)
    b.add_argument('--max', type=int, default=100)
    b.add_argument('--merge-min', type=int, default=6, help='groups with fewer symbols are merged into one page')
    l = sub.add_parser('layout')
    l.add_argument('gates')
    l.add_argument('--out', required=True)
    l.add_argument('--max', type=int, default=100)
    args = parser.parse_args()

    if args.action == 'build':
        scan = json.loads(Path(args.scan).read_text(encoding='utf-8'))
        hierarchy = json.loads(Path(args.hierarchy).read_text(encoding='utf-8'))
        document = build(scan, hierarchy, args.max, args.merge_min)
        Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        for cluster in document['clusters']:
            print('%-24s %-12s %3d symbols %3d edges' % (cluster['module'], cluster['cluster'],
                                                          cluster['symbols'], len(cluster['edges'])))
        print('RESULT: %d cluster(s), %d symbol(s), written %s'
              % (len(document['clusters']),
                 sum(c['symbols'] for c in document['clusters']), args.out))
        return 0

    document = json.loads(Path(args.gates).read_text(encoding='utf-8'))
    result = layout(document, args.max)
    Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for cluster in result['clusters']:
        print('%-24s %-12s %3d symbols, crossings %d -> %d'
              % (cluster['module'], cluster['cluster'], cluster['symbols'],
                 cluster['crossings_before'], cluster['crossings']))
    print('RESULT: %d page(s), crossings %d -> %d, written %s'
          % (len(result['clusters']), sum(c['crossings_before'] for c in result['clusters']),
             sum(c['crossings'] for c in result['clusters']), args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
