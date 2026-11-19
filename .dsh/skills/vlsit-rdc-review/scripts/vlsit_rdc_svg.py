#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_rdc_svg.py
# Function : draw one SVG figure per reset mechanism used in the report
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Write one figure per mechanism so every reset claim has a picture (rule R-018).

Usage   : vlsit_rdc_svg.py mechanisms.json --out OUT/svg
Output  : one SVG per mechanism and a summary line each.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

W, H = 900, 420


def box(x, y, w, h, label, fill='#ffffff'):
    return ('<rect x="%g" y="%g" width="%g" height="%g" fill="%s" stroke="#000" stroke-width="2"/>'
            '<text x="%g" y="%g" text-anchor="middle" font-family="Helvetica,Arial" font-size="13">%s</text>'
            % (x, y, w, h, fill, x + w / 2, y + h / 2 + 5, escape(label)))


def text(x, y, value, size=12, anchor='start'):
    return ('<text x="%g" y="%g" text-anchor="%s" font-family="Helvetica,Arial" font-size="%d">%s</text>'
            % (x, y, anchor, size, escape(value)))


def line(x1, y1, x2, y2, dash=''):
    extra = ' stroke-dasharray="6,4"' if dash else ''
    return ('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#000" stroke-width="2"%s/>'
            % (x1, y1, x2, y2, extra))


def figure(name, entry):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H),
             '<rect width="100%" height="100%" fill="#fff"/>',
             text(30, 34, 'Reset mechanism: %s' % name, 20)]
    parts.append(text(30, 56, 'crossings: %s' % ', '.join(entry['crossings']), 12))
    if name == 'sync':
        parts += [box(120, 120, 170, 60, 'flop 1 (async assert)'), box(340, 120, 170, 60, 'flop 2 (sync deassert)'),
                  line(290, 150, 340, 150), text(150, 110, 'reset in'), line(80, 150, 120, 150),
                  text(360, 210, 'dest clock'), line(425, 200, 425, 180), line(425, 200, 460, 220),
                  text(30, 300, 'deassertion leaves the second stage on a dest-clock edge; assertion is asynchronous', 12)]
    elif name == 'async_assert_sync_deassert':
        parts += [box(120, 110, 220, 60, 'reset synchroniser module'),
                  line(80, 140, 120, 140), text(150, 100, 'reset in'),
                  line(340, 140, 420, 140), text(350, 170, 'o_rst_sync to both domains'),
                  box(420, 200, 120, 60, 'domain A flops'), box(600, 200, 120, 60, 'domain B flops'),
                  line(480, 140, 480, 200), line(660, 140, 660, 200),
                  text(30, 320, 'one synchronised reset feeds both domains, so both leave reset on the same edge', 12)]
    elif name == 'sequencer':
        parts += [box(80, 120, 150, 60, 'sequencer FSM'), box(300, 90, 150, 50, 'reset A stage'),
                  box(300, 170, 150, 50, 'reset B stage'), box(540, 130, 190, 60, 'domains A and B'),
                  line(230, 140, 300, 115), line(230, 160, 300, 195), line(450, 115, 540, 150),
                  line(450, 195, 540, 170), text(30, 300, 'the release order is a state, not a skew; B is released only after A is ready', 12)]
    elif name == 'crossing_flop':
        parts += [box(120, 130, 160, 60, 'source flop (domain A)'), box(420, 130, 160, 60, 'dest flop (domain B)'),
                  line(280, 160, 420, 160), text(300, 150, 'level only'), text(430, 210, 'own reset from domain B'),
                  text(30, 300, 'safe only for a level that is stable before the destination leaves reset', 12)]
    elif name == 'tree_balance':
        parts += [box(120, 90, 200, 50, 'reset source'), box(120, 210, 200, 50, 'balanced tree'),
                  box(420, 150, 160, 60, 'domain A flops'), box(640, 150, 160, 60, 'domain B flops'),
                  line(220, 140, 220, 210), line(320, 235, 420, 180), line(320, 235, 640, 180),
                  text(30, 300, 'the skew between the two branches must stay below one clock period', 12)]
    elif name == 'none':
        parts += [box(120, 130, 160, 60, 'source flop (domain A)'), box(420, 130, 160, 60, 'dest flop (domain B)'),
                  line(280, 160, 420, 160), line(200, 100, 200, 60, '-'), line(500, 100, 500, 60, '-'),
                  text(120, 90, 'reset A'), text(420, 90, 'reset B'),
                  text(30, 300, 'no ordering between the two releases: this is a finding, not a mechanism', 12)]
    else:
        parts += [box(120, 130, 200, 60, 'named *_sync* but no chain'), line(80, 160, 120, 160),
                  text(30, 300, 'the name suggests a synchroniser and the RTL does not prove one: claimed only', 12)]
    if entry.get('evidence'):
        parts.append(text(30, 380, 'evidence: %s' % ', '.join(entry['evidence'][:4]), 11))
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('mechanisms')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    document = json.loads(Path(args.mechanisms).read_text(encoding='utf-8'))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for entry in document['mechanisms']:
        name = entry['name']
        target = out_dir / Path(entry['figure']).name
        target.write_text(figure(name, entry), encoding='utf-8')
        written += 1
        print('%s  %d crossing(s)' % (target.name, len(entry['crossings'])))
    print('RESULT: %d figure(s) written to %s' % (written, out_dir))
    return 0


if __name__ == '__main__':
    sys.exit(main())
