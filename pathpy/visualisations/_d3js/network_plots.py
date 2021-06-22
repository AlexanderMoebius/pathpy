"""Network plots with d3js"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network_plots.py -- Network plots with d3js
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2021-06-22 10:24 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations

import json

from typing import TYPE_CHECKING, Any

from pathpy import logger
from pathpy.visualisations._d3js.core import D3jsPlot

# create logger
LOG = logger(__name__)


class NetworkPlot(D3jsPlot):
    """Network plot class for a static network."""

    _kind = 'network'

    def __init__(self, data, **kwargs: Any):
        """Initialize network plot class"""
        super().__init__()
        self.data = data
        self.config = kwargs

    # def generate(self):
    #     """Function to generate the plot"""
    #     self._compute_edge_data()
    #     self._compute_node_data()

    # def _compute_node_data(self):
    #     """Generate the data structure for the nodes"""
    #     nodes: list = []
    #     for uid, node in self.network.nodes.items():
    #         nodes.append({**{'uid': uid},
    #                       **node.attributes.copy()})
    #     self.data['nodes'] = nodes

    # def _compute_edge_data(self):
    #     """Generate the data structure for the edges"""
    #     edges: list = []
    #     for uid, edge in self.network.edges.items():
    #         edges.append({**{'uid': uid,
    #                          'source': edge.v.uid,
    #                          'target': edge.w.uid,
    #                          'weight': edge.weight('weight')},
    #                       **edge.attributes.copy()})
    #     self.data['edges'] = edges

    def to_json(self):
        """Converter data to json"""
        return json.dumps(self.data)
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
