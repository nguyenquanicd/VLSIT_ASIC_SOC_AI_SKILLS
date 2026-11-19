#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_lec_svg.py
# Function : draw one cone figure per traced failing point
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Write one SVG per traced fail, reference cone on the left, netlist cone on the right (rule R-030).

Usage   : vlsit_lec_svg.py lec_equiv.json --trace lec_trace.json --out OUT/svg
Output  : F-01_cone.svg ... and a summary line each.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

COLOR = {'equivalent': '#2e7d32', 'different': '#c62828', 'unknown': '#ef6c00'}


def text(x, y, value, size=12, anchor='start', color='#000', bold=False):
    return ('<text x="%g" y="%g" text-anchor="%s" font-family="Helvetica,Arial" font-size="%d" '
            'fill="%s"%s>%s</text>'
            % (x, y, anchor, size, color, ' font-weight="bold"' if bold else '', escape(value)))


def box(x, y, w, h, label, color='#fff'):
    return ('<rect x="%g" y="%g" width="%g" height="%g" fill="%s" stroke="#000" stroke-width="1.5"/>'
            % (x, y, w, h, color) + text(x + w / 2, y + h / 2 + 4, label, 11, 'middle'))


def figure(fail, status):
    width, height = 900, 500
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
             % (width, height, width, height),
             '<rect width="100%" height="100%" fill="#fff"/>',
             text(30, 32, '%s  %s' % (fail['id'], fail['compare_point']), 18, color='#000', bold=True),
             text(30, 54, 'status: %s | rtl nodes %d | netlist nodes %d'
                  % (status, fail['ref_nodes'], fail['impl_nodes']), 12, color=COLOR.get(status, '#000')),
             text(60, 90, 'RTL cone (reference)', 13, color='#1565c0', bold=True),
             text(520, 90, 'Netlist cone (implementation)', 13, color='#6a1b9a', bold=True),
             box(60, 110, 380, 60, fail['ref_cone']['name'], '#e3f2fd'),
             box(520, 110, 380, 60, fail['impl_cone']['name'], '#f3e5f5'),
             text(30, 220, 'RTL: %s' % fail['ref_cone']['expr'][:110], 11),
             text(30, 240, 'NET: %s' % fail['impl_cone']['expr'][:110], 11),
             text(30, 300, 'trace steps: %d (file:line of every step is in the report table)'
                  % len(fail.get('steps', [])), 11)]
    line = '<line x1="450" y1="180" x2="450" y2="270" stroke="%s" stroke-width="3" stroke-dasharray="6,4"/>' % COLOR.get(status, '#000')
    parts.append(line)
    parts.append(text(450, 290, status, 13, 'middle', COLOR.get(status, '#000'), True))
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('equiv')
    parser.add_argument('--trace', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    equiv = {entry['id']: entry['status'] for entry in
             json.loads(Path(args.equiv).read_text(encoding='utf-8'))['fails']}
    trace = json.loads(Path(args.trace).read_text(encoding='utf-8'))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    written = 0
    for fail in trace['fails']:
        target = out / ('%s_cone.svg' % fail['id'])
        target.write_text(figure(fail, equiv.get(fail['id'], 'unknown')), encoding='utf-8')
        written += 1
        print('%s  %s' % (target.name, equiv.get(fail['id'], 'unknown')))
    print('RESULT: %d cone figure(s) written to %s' % (written, out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
