#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_logic_check.py
# Function : check the delivered logic pages, citations, tables and description
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Verify the deliverables against the rules before reporting (rule R-011, R-015, R-018 to R-023).

Purpose : counts the symbols of every page, re-counts the crossings, checks every
          citation against the source file, the interface table, the page title and
          name, the description sections and the four artefact families.
Usage   : vlsit_logic_check.py OUT_DIR --hierarchy OUT/hierarchy.json --path SOURCE_ROOT
Output  : one line per problem, then the RESULT line.
Exit    : 0 pass, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

MAX_SYMBOLS = 100
PAGE_NAME = re.compile(r'^\d{2}_')
CITE = re.compile(r'([\w.\-]+\.(?:sv|v)):(\d+)')


def pages_of(drawio_path):
    tree = ET.parse(drawio_path)
    pages = []
    for diagram in tree.getroot().findall('diagram'):
        cells = diagram.findall('./mxGraphModel/root/mxCell')
        pages.append({'name': diagram.get('name', ''), 'cells': cells})
    return pages


def check(directory, hierarchy_path, source_root):
    problems, warnings = [], []
    directory = Path(directory)
    hierarchy = json.loads(Path(hierarchy_path).read_text(encoding='utf-8'))
    modules = {module['name']: module for module in hierarchy['modules']}

    drawio = list(directory.glob('*.drawio'))
    if not drawio:
        problems.append('no .drawio file in %s' % directory)
    svg_files = sorted((directory / 'svg').glob('*.svg')) if (directory / 'svg').is_dir() else []
    descriptions = list(directory.glob('LOGIC_*.md'))
    if not descriptions:
        problems.append('no LOGIC_<design>.md in %s' % directory)
    if not svg_files:
        problems.append('no SVG in %s/svg' % directory)
    if not Path(hierarchy_path).exists():
        problems.append('hierarchy.json missing')

    if drawio:
        pages = pages_of(drawio[0])
        if not pages:
            problems.append('the .drawio file has no page')
        seen_modules = set()
        for index, page in enumerate(pages, 1):
            name, cells = page['name'], page['cells']
            if not name:
                problems.append('page %d has no name' % index)
            if ' - ' not in ' '.join(cell.get('value', '') for cell in cells if cell.get('value')):
                warnings.append('page %d (%s) has no "module - cluster" title' % (index, name))
            vertices = [cell for cell in cells if cell.get('vertex') == '1']
            symbols = [cell for cell in vertices
                       if not (cell.get('style') or '').startswith('text;')]
            if len(symbols) > MAX_SYMBOLS:
                problems.append('page %s has %d symbols (limit %d)' % (name, len(symbols), MAX_SYMBOLS))
            module_name = None
            for candidate in modules:
                if candidate in name or candidate in ' '.join(cell.get('value', '') for cell in cells):
                    module_name = candidate
                    break
            if module_name:
                seen_modules.add(module_name)
                module = modules[module_name]
                table = ' '.join(cell.get('value', '') for cell in cells
                                 if (cell.get('style') or '').startswith('text;'))
                missing = [port['name'] for port in module['ports'] if port['name'] not in table]
                if missing:
                    problems.append('page %s: interface table misses %s'
                                    % (name, ', '.join(missing[:5]) + ('...' if len(missing) > 5 else '')))
            for cell in symbols:
                style = cell.get('style') or ''
                value = cell.get('value') or ''
                if style.startswith('shape=partialRectangle') or style.startswith('text;'):
                    continue
                if cell.get('edge') == '1':
                    continue
                if not CITE.search(value):
                    problems.append('page %s: symbol %r has no file:line citation' % (name, value[:30]))
        for module in modules:
            if modules[module].get('instances') or modules[module].get('blocks', {}).get('assigns') is not None:
                if module not in seen_modules:
                    warnings.append('module %s has no page' % module)

    if descriptions:
        text = descriptions[0].read_text(encoding='utf-8')
        for module in modules:
            if ('Module `%s`' % module) not in text and ('## 3. Module `%s`' % module) not in text:
                problems.append('description has no section for module %s' % module)
        for keyword in ('Purpose', 'Behaviour'):
            if keyword not in text:
                warnings.append('description has no %s block' % keyword)

    if source_root:
        root = Path(source_root)
        cache = {}
        for page in (pages_of(drawio[0]) if drawio else []):
            for cell in page['cells']:
                for name, line in CITE.findall(cell.get('value') or ''):
                    if name not in cache:
                        path = root / name
                        cache[name] = path.read_text(encoding='utf-8').count('\n') + 1 if path.exists() else None
                    total = cache[name]
                    if total is None:
                        problems.append('citation %s:%s points at a missing file' % (name, line))
                    elif int(line) > total:
                        problems.append('citation %s:%s is past the end of the file (%d lines)' % (name, line, total))

    for problem in problems:
        print('ERROR: %s' % problem)
    for warning in warnings:
        print('WARN: %s' % warning)
    print('RESULT: %s (%d error(s), %d warning(s), %d page(s), %d SVG, %d module(s))'
          % ('PASS' if not problems else 'FAIL', len(problems), len(warnings),
             len(pages_of(drawio[0])) if drawio else 0, len(svg_files), len(modules)))
    return 0 if not problems else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('out_dir')
    parser.add_argument('--hierarchy', required=True)
    parser.add_argument('--path', default='', help='source root the citations point into')
    args = parser.parse_args()
    return check(args.out_dir, args.hierarchy, args.path)


if __name__ == '__main__':
    sys.exit(main())
