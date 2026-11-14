#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_lec_equiv.py
# Function : prove or disprove the equivalence of each traced cone
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Compare the two cones structurally and by truth table (rule R-026).

Usage   : vlsit_lec_equiv.py lec_trace.json --out lec_equiv.json
Output  : one line per fail with the method and the status.
Exit    : 0 success, 1 error.
"""
import argparse
import itertools
import json
import re
import sys
from pathlib import Path

TOKEN = re.compile(r'\s*([&|^~!?:()]|[A-Za-z_]\w*|\d+\'[bodhBODH][0-9a-fA-FxXzZ_]+|\d+)')


def tokenize(text):
    return [match.group(1) for match in TOKEN.finditer(text)]


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def peek(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else ''

    def take(self):
        token = self.peek()
        self.position += 1
        return token

    def parse(self):
        return self.ternary()

    def ternary(self):
        condition = self.or_expr()
        if self.peek() == '?':
            self.take()
            first = self.ternary()
            if self.peek() != ':':
                raise ValueError('missing :')
            self.take()
            second = self.ternary()
            return ('mux', condition, first, second)
        return condition

    def or_expr(self):
        node = self.xor()
        while self.peek() == '|':
            self.take()
            node = ('or', node, self.xor())
        return node

    def xor(self):
        node = self.and_expr()
        while self.peek() == '^':
            self.take()
            node = ('xor', node, self.and_expr())
        return node

    def and_expr(self):
        node = self.unary()
        while self.peek() == '&':
            self.take()
            node = ('and', node, self.unary())
        return node

    def unary(self):
        token = self.peek()
        if token in ('~', '!'):
            self.take()
            return ('not', self.unary())
        return self.primary()

    def primary(self):
        token = self.take()
        if token == '(':
            node = self.ternary()
            if self.peek() != ')':
                raise ValueError('missing )')
            self.take()
            return node
        if re.match(r'^\d', token):
            return ('const', 0 if re.search(r"'[hHdD]0+$|^0$|'0$", token) else 1)
        return ('id', token)


def flatten(node, op):
    if node[0] == op:
        args = []
        for child in node[1:]:
            args += flatten(child, op)
        return args
    return [node]


def normalize(node):
    if node[0] in ('and', 'or'):
        args = [normalize(child) for child in flatten(node, node[0])]
        args.sort(key=repr)
        return (node[0],) + tuple(args)
    if node[0] == 'not':
        inner = normalize(node[1])
        if inner[0] == 'not':
            return inner[1]
        return ('not', inner)
    if node[0] == 'mux':
        return ('mux',) + tuple(normalize(child) for child in node[1:])
    return node


def evaluate(node, env):
    kind = node[0]
    if kind == 'id':
        return env.get(node[1], 0)
    if kind == 'const':
        return node[1]
    if kind == 'not':
        return 1 - evaluate(node[1], env)
    if kind == 'and':
        return min(evaluate(child, env) for child in node[1:])
    if kind == 'or':
        return max(evaluate(child, env) for child in node[1:])
    if kind == 'xor':
        value = 0
        for child in node[1:]:
            value ^= evaluate(child, env)
        return value
    if kind == 'mux':
        return evaluate(node[2], env) if evaluate(node[1], env) else evaluate(node[3], env)
    return 0


def inputs_of(node, found=None):
    found = found if found is not None else []
    if node[0] == 'id' and node[1] not in found:
        found.append(node[1])
    for child in node[1:]:
        if isinstance(child, tuple):
            inputs_of(child, found)
    return found


def expand(node):
    expr = node['expr']
    for child in node.get('inputs', []):
        expr = re.sub(r'\b%s\b' % re.escape(child['name']), '(%s)' % expand(child), expr)
    return expr


def compare(reference, implementation):
    ref_ast, impl_ast = normalize(reference), normalize(implementation)
    if repr(ref_ast) == repr(impl_ast):
        return {'status': 'equivalent', 'method': 'structure', 'detail': 'the two cones are identical after normalisation'}
    names = inputs_of(ref_ast) + [name for name in inputs_of(impl_ast) if name not in inputs_of(ref_ast)]
    if len(names) > 12:
        return {'status': 'unknown', 'method': 'structure',
                'detail': '%d inputs, too many for the truth table; the structures differ' % len(names)}
    for values in itertools.product((0, 1), repeat=len(names)):
        env = dict(zip(names, values))
        if evaluate(ref_ast, env) != evaluate(impl_ast, env):
            return {'status': 'different', 'method': 'truth-table',
                    'detail': 'row %s gives %d on the reference and %d on the implementation'
                              % (', '.join('%s=%d' % item for item in env.items()),
                                 evaluate(ref_ast, env), evaluate(impl_ast, env)),
                    'inputs': names}
    return {'status': 'equivalent', 'method': 'truth-table',
            'detail': 'all %d rows agree' % (2 ** len(names)), 'inputs': names}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('trace')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    document = json.loads(Path(args.trace).read_text(encoding='utf-8'))
    results = []
    for fail in document['fails']:
        entry = {'id': fail['id'], 'compare_point': fail['compare_point']}
        try:
            reference = Parser(tokenize(expand(fail['ref_cone']))).parse()
            implementation = Parser(tokenize(expand(fail['impl_cone']))).parse()
            entry.update(compare(reference, implementation))
        except (ValueError, IndexError) as error:
            entry.update({'status': 'unknown', 'method': 'structure',
                          'detail': 'the expression could not be parsed: %s' % error})
        if fail.get('opaque'):
            entry.update({'status': 'unknown', 'method': 'structure',
                          'detail': 'the cone stops at a point that is not in the source (opaque)'})
        entry['ref_expr'] = expand(fail['ref_cone'])
        entry['impl_expr'] = expand(fail['impl_cone'])
        entry['ref_nodes'] = fail['ref_nodes']
        entry['impl_nodes'] = fail['impl_nodes']
        results.append(entry)
    out = {'schema': 'vlsit-lec-equiv/1', 'traced': len(results), 'fails': results,
           'summary': {status: sum(1 for entry in results if entry['status'] == status)
                       for status in ('equivalent', 'different', 'unknown')}}
    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for entry in results:
        print('%-5s %-30s %-12s %-12s %s' % (entry['id'], entry['compare_point'], entry['status'],
                                              entry['method'], entry['detail'][:70]))
    print('RESULT: equivalent=%d different=%d unknown=%d, written %s'
          % (out['summary']['equivalent'], out['summary']['different'],
             out['summary']['unknown'], args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
