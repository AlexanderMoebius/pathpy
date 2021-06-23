"""Network plots with tikz"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network_plots.py -- Network plots with tikz
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2021-06-23 16:31 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations

from typing import Any


from pathpy import logger
from pathpy.visualisations._tikz.core import TikzPlot

# create logger
LOG = logger(__name__)


class NetworkPlot(TikzPlot):
    """Network plot class for a static network."""

    _kind = 'network'

    def __init__(self, data, **kwargs: Any):
        """Initialize network plot class"""
        super().__init__()
        self.data = data
        self.config = kwargs
        self.generate()

    def generate(self):
        """Clen up data"""
        self._compute_node_data()
        self._compute_edge_data()

    def _compute_node_data(self):
        """Generate the data structure for the nodes"""
        default = {'uid', 'x', 'y', 'size', 'color', 'opacity'}
        mapping = {}

        for node in self.data['nodes']:
            for key in list(node):
                if key in mapping:
                    node[mapping[key]] = node.pop(key)
                if key not in default:
                    node.pop(key)

    def _compute_edge_data(self):
        """Generate the data structure for the edges"""
        default = {'uid', 'source', 'target', 'lw', 'color', 'opacity'}
        mapping = {'size': 'lw'}

        for edge in self.data['edges']:
            for key in list(edge):
                if key in mapping:
                    edge[mapping[key]] = edge.pop(key)
                if key not in default:
                    edge.pop(key)

    def to_tikz(self):
        """Converter to Tex"""

        def _add_args(args: dict):
            string = ''
            for key, value in args.items():
                string += f',{key}' if value == bool else f',{key}={value}'
            return string

        tikz = ''
        for node in self.data['nodes']:
            uid = node.pop('uid')
            string = '\\Vertex['
            string += _add_args(node)
            string += ']{{{}}}\n'.format(uid)
            tikz += string

        for edge in self.data['edges']:
            uid = edge.pop('uid')
            source = edge.pop('source')
            target = edge.pop('target')
            string = '\\Edge['
            string += _add_args(edge)
            string += ']({})({})\n'.format(source, target)
            tikz += string
        return tikz
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
