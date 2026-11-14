#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_cdc_svg.py
# Function : draw one SVG figure per CDC synchronisation mechanism
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Write one figure per mechanism used in the report (rule R-018).

Usage   : vlsit_cdc_svg.py mechanisms.json --out OUT/svg
Output  : one SVG per mechanism.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

W, H = 900, 420


def text(x, y, value, size=12, anchor='start'):
    return ('<text x="%g" y="%g" text-anchor="%s" font-family="Helvetica,Arial" font-size="%d">%s</text>'
            % (x, y, anchor, size, escape(value)))


def box(x, y, w, h, label, fill='#fff'):
    return ('<rect x="%g" y="%g" width="%g" height="%g" fill="%s" stroke="#000" stroke-width="2"/>'
            % (x, y, w, h, fill) + text(x + w / 2, y + h / 2 + 5, label, 12, 'middle'))


def stroke(x1, y1, x2, y2, dash=False):
    return ('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#000" stroke-width="2"%s/>'
            % (x1, y1, x2, y2, ' stroke-dasharray="6,4"' if dash else ''))


def figure(name, entry):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H),
             '<rect width="100%" height="100%" fill="#fff"/>',
             text(30, 34, 'CDC mechanism: %s' % name, 20),
             text(30, 56, 'crossings: %s' % ', '.join(entry['crossings']), 12)]
    if name == 'sync_2ff':
        parts += [box(120, 130, 150, 60, 'source flop (A)'), box(340, 130, 150, 60, 'sync flop 1 (B)'),
                  box(560, 130, 150, 60, 'sync flop 2 (B)'), stroke(270, 160, 340, 160),
                  stroke(490, 160, 560, 160), text(300, 250, 'B clock'), stroke(415, 250, 415, 190),
                  text(30, 320, 'two flops in the destination domain: metastability is removed', 12)]
    elif name == 'pulse_toggle':
        parts += [box(120, 120, 160, 60, 'pulse A'), box(380, 120, 160, 60, 'toggle A'),
                  box(640, 120, 160, 60, 'sync + edge B'), stroke(280, 150, 380, 150),
                  stroke(540, 150, 640, 150), text(30, 300, 'a pulse becomes a toggle, crosses two flops and is turned back into a pulse', 12)]
    elif name == 'handshake':
        parts += [box(100, 100, 160, 60, 'requester A'), box(500, 100, 160, 60, 'completer B'),
                  stroke(260, 120, 500, 120), text(300, 110, 'req (A to B)'),
                  stroke(500, 250, 260, 250), text(300, 240, 'ack (B to A)'),
                  text(30, 330, 'req and ack each cross through a two-flop synchroniser; the ack closes the handshake', 12)]
    elif name == 'async_fifo':
        parts += [box(100, 120, 160, 80, 'write side A'), box(380, 120, 160, 80, 'dual-port memory'),
                  box(660, 120, 160, 80, 'read side B'), stroke(260, 160, 380, 160), stroke(540, 160, 660, 160),
                  text(30, 300, 'pointers cross through gray-code synchronisers, so a full or empty flag is safe', 12)]
    elif name == 'gray_counter':
        parts += [box(120, 120, 180, 60, 'binary counter A'), box(420, 120, 180, 60, 'gray encode'),
                  box(700, 120, 160, 60, 'gray decode B'), stroke(300, 150, 420, 150), stroke(600, 150, 700, 150),
                  text(30, 300, 'only one bit changes per step, so a two-flop synchroniser cannot capture a mixed value', 12)]
    elif name == 'mux_datapath':
        parts += [box(120, 120, 160, 60, 'data bus A'), box(420, 120, 160, 60, 'mux / register B'),
                  stroke(280, 150, 420, 150), text(300, 140, 'stable data'),
                  text(30, 300, 'a level bus that is stable before the destination samples it; confirm the stability window', 12)]
    elif name == 'none':
        parts += [box(120, 120, 160, 60, 'source flop (A)'), box(420, 120, 160, 60, 'dest flop (B)'),
                  stroke(280, 150, 420, 150), text(30, 300, 'no synchroniser and no protocol: this is a finding, not a mechanism', 12)]
    else:
        parts += [box(120, 120, 220, 60, 'named *_sync* but no chain'), stroke(80, 150, 120, 150),
                  text(30, 300, 'the name suggests a synchroniser and the RTL does not prove one', 12)]
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
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for entry in document['mechanisms']:
        target = out / Path(entry['figure']).name
        target.write_text(figure(entry['name'], entry), encoding='utf-8')
        print('%s  %d crossing(s)' % (target.name, len(entry['crossings'])))
    print('RESULT: %d figure(s) written to %s' % (len(document['mechanisms']), out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
