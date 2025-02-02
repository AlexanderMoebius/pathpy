"""Methods to analyze clustering patterns in networks"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : clustering.py -- Module to calculate clustering statistics
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Mon 2021-03-29 16:56 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Set
import numpy as np

from pathpy import logger

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.models.api import Network
    from pathpy.core.api import Node
# create logger
LOG = logger(__name__)


def local_clustering_coefficient(network: Network, v: str) -> float:
    """Calculates the local clustering coefficient of a node in a network.


    The local clustering coefficient of any node with an (out-)degree smaller
    than two is defined as zero. For all other nodes, it is defined as:

        cc(c) := 2*k(i)/(d_i(d_i-1))

        or

        cc(c) := k(i)/(d_out_i(d_out_i-1))

        in undirected and directed networks respectively.

    Parameters
    ----------
    network : Network

        The network in which to calculate the local clustering coefficient

    node : str

        The node for which the local clustering coefficient shall be calculated

    """
    lcc: float = 0.
    d = network.degrees()
    o = network.outdegrees()

    if network.directed and o[v] >= 2 or network.directed == False and d[v] >= 2:
        k: int = 0
        # compute set of closed triads
        closed = closed_triads(network, v)
        k = len(closed)

        if network.directed:
            return k/(o[v]*(o[v]-1))
        else:
            return 2*k/(d[v]*(d[v]-1))
    else:
        return 0.


def avg_clustering_coefficient(network: Network) -> float:
    """Calculates the average (global) clustering coefficient.

    Parameters
    ----------

    network : Network

        The network in which to calculate the local clustering coefficient.

    """
    return np.mean([ local_clustering_coefficient(network, v.uid) for v in network.nodes ])


def closed_triads(network: Network, v: str) -> Set:
    """Calculates the set of edges that represent a closed triad
    around a given node v.

    Parameters
    ----------

    network : Network

        The network in which to calculate the list of closed triads

    """
    ct: set = set()
    edges = set()
    for w in network.successors[v]:
        for e in network.incident_edges[w.uid]:
            edges.add(e)
    for edge in edges:
        if (edge.v in network.successors[v] and
                edge.w in network.successors[v]):
            ct.add(edge)
    return ct