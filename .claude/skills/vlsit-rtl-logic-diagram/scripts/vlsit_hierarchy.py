#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_hierarchy.py
# Function : build and check the hierarchy and interface JSON of a design
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Build hierarchy.json from scan.json and check it against the schema (rule R-009, R-010).

Purpose : one JSON file holds the tree, every port and every instance connection, so
          the pages and the interface tables are derived from a single source.
Usage   : vlsit_hierarchy.py build SCAN.json --top MODULE --out hierarchy.json
          vlsit_hierarchy.py check hierarchy.json
Output  : build writes the file and prints the tree; check prints one line per problem
          and a RESULT line.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import sys
from pathlib import Path


def build(scan, top):
    modules = {module['name']: module for module in scan['modules']}
    if top not in modules:
        raise SystemExit('ERROR: top module %s is not in the scan (%s)' % (top, ', '.join(sorted(modules))))
    children = {}
    for module in scan['modules']:
        for instance in module['instances']:
            if instance['module'] in modules:
                children.setdefault(module['name'], []).append(instance['module'])
    ordered, seen = [], set()

    def walk(name):
        if name in seen:
            return
        seen.add(name)
        ordered.append(name)
        for child in children.get(name, []):
            walk(child)

    walk(top)
    for name in sorted(modules):
        walk(name)

    out_modules = []
    for name in ordered:
        module = modules[name]
        out_modules.append({
            'name': module['name'], 'file': module['file'], 'line': module['line'],
            'parent': scan['parents'].get(name),
            'purpose': '', 'behaviour': '', 'evidence': [],
            'parameters': module['params'],
            'ports': [{'name': p['name'], 'direction': p.get('direction') or 'input',
                       'width': p.get('width') or '1', 'domain': '', 'description': ''}
                      for p in module['ports']],
            'instances': [{'name': i['name'], 'module': i['module'], 'line': i['line'],
                           'connections': i['connections']} for i in module['instances']],
            'blocks': {'assigns': module['assigns'],
                       'always_comb': module['always_comb'],
                       'always_ff': module['always_ff']},
        })
    design = top[2:] if top.startswith('m_') else top
    return {'schema': 'vlsit-hierarchy/1', 'design': design, 'top': top,
            'source': {'root': scan.get('source', ''), 'files': scan.get('files', [])},
            'modules': out_modules}


def check(document):
    problems = []
    names = {module['name'] for module in document.get('modules', [])}
    top = document.get('top')
    if top not in names:
        problems.append('top %r is not a module of the document' % top)
    for module in document.get('modules', []):
        where = module.get('name', '?')
        if not module.get('file'):
            problems.append('%s: missing file' % where)
        if not module.get('line'):
            problems.append('%s: missing line' % where)
        if module.get('parent') is not None and module['parent'] not in names:
            problems.append('%s: parent %r is not a module' % (where, module['parent']))
        if module.get('parent') is None and where != top:
            problems.append('%s: no parent but it is not the top' % where)
        if not module.get('purpose'):
            problems.append('%s: purpose is empty' % where)
        if not module.get('behaviour'):
            problems.append('%s: behaviour is empty' % where)
        if not module.get('evidence'):
            problems.append('%s: evidence is empty' % where)
        for port in module.get('ports', []):
            if not port.get('direction'):
                problems.append('%s: port %s has no direction' % (where, port.get('name')))
            if not port.get('width'):
                problems.append('%s: port %s has no width' % (where, port.get('name')))
            if not port.get('description'):
                problems.append('%s: port %s has no description' % (where, port.get('name')))
        for instance in module.get('instances', []):
            if instance.get('module') not in names:
                problems.append('%s: instance %s names an unknown module %r'
                                % (where, instance.get('name'), instance.get('module')))
            for connection in instance.get('connections', []):
                if connection.get('port') is None:
                    problems.append('%s: instance %s has a positional connection'
                                    % (where, instance.get('name')))
    return problems


def tree(document):
    by_parent = {}
    for module in document['modules']:
        by_parent.setdefault(module['parent'], []).append(module['name'])
    lines = []

    def walk(name, depth):
        lines.append('%s%s' % ('  ' * depth, name))
        for child in by_parent.get(name, []):
            walk(child, depth + 1)

    walk(document['top'], 0)
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='action', required=True)
    b = sub.add_parser('build')
    b.add_argument('scan')
    b.add_argument('--top', required=True)
    b.add_argument('--out', required=True)
    b.add_argument('--force', action='store_true')
    c = sub.add_parser('check')
    c.add_argument('hierarchy')
    args = parser.parse_args()

    if args.action == 'build':
        scan = json.loads(Path(args.scan).read_text(encoding='utf-8'))
        document = build(scan, args.top)
        out = Path(args.out)
        if out.exists() and not args.force:
            print('ERROR: %s exists; pass --force to overwrite it' % out)
            return 1
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print('tree:')
        for line in tree(document):
            print('  ' + line)
        print('RESULT: %d module(s) written to %s' % (len(document['modules']), out))
        print('NEXT: fill purpose, behaviour, evidence and the port descriptions (SKILL.md step 7),')
        print('      then re-run: vlsit_hierarchy.py check %s' % out)
        return 0

    document = json.loads(Path(args.hierarchy).read_text(encoding='utf-8'))
    problems = check(document)
    for problem in problems:
        print('ERROR: %s' % problem)
    print('RESULT: %s (%d error(s))' % ('PASS' if not problems else 'FAIL', len(problems)))
    return 0 if not problems else 1


if __name__ == '__main__':
    sys.exit(main())
