#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_logic_drawio.py
# Function : write one draw.io page per logic cluster, with gates and citations
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Write the draw.io deliverable from layout.json (rule R-014, R-018, R-019).

Purpose : every cluster becomes one page whose title, page name, interface table,
          gates, blocks, pads and file:line citations can be edited in draw.io.
Usage   : vlsit_logic_drawio.py LAYOUT.json --out DESIGN_logic.drawio [--hierarchy hierarchy.json]
Output  : the .drawio file and one summary line per page.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

STYLE = {
    'and': 'shape=mxgraph.electrical.logic_gates.logic_gate;operation=and;strokeWidth=2;fontSize=18;',
    'or': 'shape=mxgraph.electrical.logic_gates.logic_gate;operation=or;strokeWidth=2;fontSize=18;',
    'xor': 'shape=mxgraph.electrical.logic_gates.logic_gate;operation=xor;strokeWidth=2;fontSize=18;',
    'nand': 'shape=mxgraph.electrical.logic_gates.logic_gate;operation=nand;strokeWidth=2;fontSize=18;',
    'nor': 'shape=mxgraph.electrical.logic_gates.logic_gate;operation=nor;strokeWidth=2;fontSize=18;',
    'not': 'shape=mxgraph.electrical.logic_gates.logic_gate;operation=not;strokeWidth=2;fontSize=18;',
    'mux': 'shape=triangle;whiteSpace=wrap;html=1;rotation=-90;strokeWidth=2;fontSize=18;',
    'add': 'rounded=0;whiteSpace=wrap;html=1;strokeWidth=2;fontSize=18;',
    'dff': 'shape=mxgraph.electrical.logic_gates.d_type_flip-flop;strokeWidth=2;fontSize=14;',
    'block': 'rounded=0;whiteSpace=wrap;html=1;strokeWidth=2;fontSize=12;fillColor=#fff2cc;',
    'instance': 'rounded=0;whiteSpace=wrap;html=1;strokeWidth=2;fontSize=14;fillColor=#dae8fc;',
    'pad': 'shape=partialRectangle;whiteSpace=wrap;html=1;bottom=0;right=0;fillColor=none;strokeWidth=2;fontSize=12;',
    'const': 'text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=14;',
    'text': 'text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=14;',
}
SIZE = {
    'and': (96, 64), 'or': (96, 64), 'xor': (96, 64), 'nand': (96, 64), 'nor': (96, 64),
    'not': (72, 64), 'mux': (96, 64), 'add': (96, 64), 'dff': (90, 90),
    'block': (150, 70), 'instance': (170, 80), 'pad': (54, 30), 'const': (70, 26), 'text': (90, 26),
}


def size_of(node):
    return SIZE.get(node['kind'], (96, 64))


def node_cell(node, page_index, index):
    width, height = size_of(node)
    label = '%s\n%s:%s' % (node.get('label', ''), node.get('file', ''), node.get('line', ''))
    if node['kind'] in ('pad', 'const', 'text'):
        label = node.get('label', '')
    return ('<mxCell id="p%d_n%d" value=%s style=%s vertex="1" parent="1">'
            '<mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>'
            % (page_index, index, quoteattr(label), quoteattr(STYLE.get(node['kind'], STYLE['block'])),
               node['x'], node['y'], width, height))


def edge_cell(edge, page_index, index):
    return ('<mxCell id="p%d_e%d" edge="1" source="p%d_%s" target="p%d_%s" parent="1" '
            'style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jetSize=auto;'
            'endArrow=block;endFill=1;strokeWidth=2;">'
            '<mxGeometry relative="1" as="geometry"/></mxCell>'
            % (page_index, index, page_index, edge['from'], page_index, edge['to']))


def interface_table(cluster, hierarchy):
    if not hierarchy:
        return ''
    module = next((m for m in hierarchy['modules'] if m['name'] == cluster['module']), None)
    if not module:
        return ''
    rows = ['<b>Interface of %s</b>' % escape(module['name'])]
    for port in module['ports']:
        rows.append('%s (%s, %s)' % (escape(port['name']), escape(port.get('direction', '')),
                                     escape(str(port.get('width', '1')))))
    return '<br>'.join(rows)


def page(cluster, page_index, hierarchy):
    name = '%02d_%s_%s' % (page_index, cluster['module'], cluster['cluster'])
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    title = '%s  [%s]  symbols: %d  crossings: %d' % (
        cluster['title'], name, cluster['symbols'], cluster['crossings'])
    cells.append('<mxCell id="p%d_t" value=%s style="text;html=1;fontSize=18;fontStyle=1;" vertex="1" parent="1">'
                 '<mxGeometry x="40" y="6" width="1100" height="26" as="geometry"/></mxCell>'
                 % (page_index, quoteattr(title)))
    table = interface_table(cluster, hierarchy)
    if table:
        cells.append('<mxCell id="p%d_if" value=%s style="text;html=1;fontSize=11;align=left;verticalAlign=top;" '
                     'vertex="1" parent="1"><mxGeometry x="40" y="34" width="420" height="240" as="geometry"/>'
                     '</mxCell>' % (page_index, quoteattr(table)))
    for index, node in enumerate(cluster['nodes']):
        cells.append(node_cell(node, page_index, index))
    for index, edge in enumerate(cluster['edges']):
        cells.append(edge_cell(edge, page_index, index))
    body = ''.join(cells)
    return ('<diagram id="page%d" name=%s><mxGraphModel dx="1600" dy="1000" grid="1" gridSize="10" '
            'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
            'pageWidth="1400" pageHeight="900" math="0" shadow="0"><root>%s</root></mxGraphModel></diagram>'
            % (page_index, quoteattr(name), body))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('layout')
    parser.add_argument('--out', required=True)
    parser.add_argument('--hierarchy', help='hierarchy.json, to write the interface table')
    args = parser.parse_args()
    document = json.loads(Path(args.layout).read_text(encoding='utf-8'))
    hierarchy = json.loads(Path(args.hierarchy).read_text(encoding='utf-8')) if args.hierarchy else None
    pages = []
    for index, cluster in enumerate(document['clusters'], 1):
        pages.append(page(cluster, index, hierarchy))
        print('%02d  %-22s %-10s %3d symbols, crossings %d'
              % (index, cluster['module'], cluster['cluster'], cluster['symbols'], cluster['crossings']))
    content = '<mxfile host="vlsit" version="1">' + ''.join(pages) + '</mxfile>\n'
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding='utf-8')
    print('RESULT: %d page(s) written to %s' % (len(pages), out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
