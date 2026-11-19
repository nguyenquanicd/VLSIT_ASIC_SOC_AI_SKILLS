#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_logic_svg.py
# Function : draw every logic page as a standalone SVG with real gate shapes
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Render layout.json to one SVG per cluster page (rule R-019, R-022).

Purpose : the SVG keeps the gate shapes that a generic draw.io renderer loses, so the
          picture can be read without draw.io installed.
Usage   : vlsit_logic_svg.py LAYOUT.json --out DIR [--hierarchy hierarchy.json]
Output  : DIR/<NN>_<module>_<cluster>.svg, one summary line per page.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

WIRE = '<polyline points="%s" fill="none" stroke="#000" stroke-width="2"/>'
BUBBLE = 7


def size_of(kind):
    return {'and': (96, 64), 'or': (96, 64), 'xor': (96, 64), 'nand': (96, 64), 'nor': (96, 64),
            'not': (72, 64), 'mux': (96, 64), 'add': (96, 64), 'dff': (90, 90),
            'block': (150, 70), 'instance': (170, 80), 'pad': (54, 30),
            'const': (70, 26), 'text': (90, 26)}.get(kind, (96, 64))


def shape(kind, x, y, w, h):
    if kind == 'and':
        return '<path d="M %g,%g H %g A %g,%g 0 0 1 %g,%g H %g Z" fill="#fff" stroke="#000" stroke-width="2"/>' % (
            x, y, x + w * 0.55, w * 0.45, h / 2, x + w * 0.55, y + h, x)
    if kind in ('or', 'xor', 'nor', 'nxor'):
        body = ('<path d="M %g,%g Q %g,%g %g,%g Q %g,%g %g,%g Q %g,%g %g,%g Z" fill="#fff" stroke="#000" stroke-width="2"/>'
                % (x + 6, y, x + 0.35 * w, y, x + w, y + h / 2, x + 0.35 * w, y + h, x + 6, y + h,
                   x + 0.28 * w, y + h / 2, x + 6, y))
        extra = ''
        if kind in ('xor', 'nxor'):
            extra = '<path d="M %g,%g Q %g,%g %g,%g" fill="none" stroke="#000" stroke-width="2"/>' % (
                x, y, x + 0.22 * w, y + h / 2, x, y + h)
        if kind in ('nor', 'nxor'):
            extra += '<circle cx="%g" cy="%g" r="%d" fill="#fff" stroke="#000" stroke-width="2"/>' % (
                x + w + BUBBLE, y + h / 2, BUBBLE)
        return body + extra
    if kind == 'not':
        return ('<path d="M %g,%g L %g,%g L %g,%g Z" fill="#fff" stroke="#000" stroke-width="2"/>'
                '<circle cx="%g" cy="%g" r="%d" fill="#fff" stroke="#000" stroke-width="2"/>' % (
                    x, y, x, y + h, x + w - 2 * BUBBLE, y + h / 2, x + w - BUBBLE, y + h / 2, BUBBLE))
    if kind == 'mux':
        return ('<polygon points="%g,%g %g,%g %g,%g %g,%g %g,%g" fill="#fff" stroke="#000" stroke-width="2"/>'
                % (x, y, x + 0.7 * w, y, x + w, y + h / 2, x + 0.7 * w, y + h, x, y + h))
    if kind == 'pad':
        return '<rect x="%g" y="%g" width="%g" height="%g" fill="#f5f5f5" stroke="#000" stroke-width="2"/>' % (x, y, w, h)
    if kind == 'instance':
        return '<rect x="%g" y="%g" width="%g" height="%g" fill="#dae8fc" stroke="#000" stroke-width="2"/>' % (x, y, w, h)
    if kind == 'block':
        return '<rect x="%g" y="%g" width="%g" height="%g" fill="#fff2cc" stroke="#000" stroke-width="2"/>' % (x, y, w, h)
    return '<rect x="%g" y="%g" width="%g" height="%g" fill="#fff" stroke="#000" stroke-width="2"/>' % (x, y, w, h)


def text_lines(label, cx, cy, size=13):
    parts = str(label).split('\n')
    out = []
    top = cy - (len(parts) - 1) * size * 0.6
    for index, part in enumerate(parts):
        out.append('<text x="%g" y="%g" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" '
                   'font-size="%d">%s</text>' % (cx, top + index * size * 1.2 + size / 3, size, escape(part)))
    return ''.join(out)


def page_svg(cluster, index, hierarchy):
    nodes = cluster['nodes']
    width = max([node['x'] + size_of(node['kind'])[0] for node in nodes] + [600]) + 60
    height = max([node['y'] + size_of(node['kind'])[1] for node in nodes] + [400]) + 80
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
           % (width, height, width, height),
           '<rect width="100%" height="100%" fill="#fff"/>',
           '<text x="40" y="32" font-family="Helvetica,Arial,sans-serif" font-size="20" font-weight="bold">%s</text>'
           % escape(cluster['title']),
           '<text x="40" y="52" font-family="Helvetica,Arial,sans-serif" font-size="12" fill="#444">'
           'page %02d_%s_%s | symbols %d | crossings %d</text>'
           % (index, escape(cluster['module']), escape(cluster['cluster']), cluster['symbols'], cluster['crossings'])]
    if hierarchy:
        module = next((m for m in hierarchy['modules'] if m['name'] == cluster['module']), None)
        if module:
            lines = ['Interface of %s' % module['name']] + [
                '%s (%s, %s)' % (port['name'], port.get('direction', ''), port.get('width', '1'))
                for port in module['ports']]
            for row, line in enumerate(lines):
                out.append('<text x="40" y="%d" font-family="Helvetica,Arial,sans-serif" font-size="11" '
                           'fill="#333">%s</text>' % (76 + row * 15, escape(line)))
    positions = {node['id']: node for node in nodes}
    for node in nodes:
        w, h = size_of(node['kind'])
        out.append(shape(node['kind'], node['x'], node['y'], w, h))
        if node['kind'] in ('const', 'text'):
            out.append(text_lines(node.get('label', ''), node['x'] + w / 2, node['y'] + h / 2, 12))
        else:
            out.append(text_lines(node.get('label', ''), node['x'] + w / 2, node['y'] + h / 2 - 6, 13))
            if node.get('file'):
                out.append('<text x="%g" y="%g" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" '
                           'font-size="9" fill="#666">%s:%s</text>'
                           % (node['x'] + w / 2, node['y'] + h + 11, escape(node['file']),
                              node.get('line', '')))
    for edge in cluster['edges']:
        source, target = positions.get(edge['from']), positions.get(edge['to'])
        if not source or not target:
            continue
        sw, sh = size_of(source['kind'])
        tw, th = size_of(target['kind'])
        x1, y1 = source['x'] + sw, source['y'] + sh / 2
        x2, y2 = target['x'], target['y'] + th / 2
        mid = (x1 + x2) / 2
        out.append(WIRE % ('%g,%g %g,%g %g,%g %g,%g' % (x1, y1, mid, y1, mid, y2, x2, y2)))
    out.append('</svg>')
    return '\n'.join(out) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('layout')
    parser.add_argument('--out', required=True)
    parser.add_argument('--hierarchy')
    args = parser.parse_args()
    document = json.loads(Path(args.layout).read_text(encoding='utf-8'))
    hierarchy = json.loads(Path(args.hierarchy).read_text(encoding='utf-8')) if args.hierarchy else None
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    for index, cluster in enumerate(document['clusters'], 1):
        name = '%02d_%s_%s.svg' % (index, cluster['module'], cluster['cluster'])
        target = out_dir / name
        if target.exists():
            print('WARN: %s exists and is replaced' % target.name)
        target.write_text(page_svg(cluster, index, hierarchy), encoding='utf-8')
        print('%s  %d symbols' % (name, cluster['symbols']))
    print('RESULT: %d SVG page(s) written to %s' % (len(document['clusters']), out_dir))
    return 0


if __name__ == '__main__':
    sys.exit(main())
