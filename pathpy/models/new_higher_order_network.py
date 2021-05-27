"""Higher-order network class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : higher_order_network.py -- Basic class for a HON
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2021-05-26 18:01 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from typing import Any, Optional
from itertools import islice
from collections import Counter
from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9
import numpy as np

from pathpy import logger
from pathpy.core.core import PathPyRelation
from pathpy.core.edge import Edge, EdgeCollection
from pathpy.core.path import Path, PathCollection
from pathpy.models.classes import BaseHigherOrderNetwork
from pathpy.models.network import Network

# create logger for the Network class
LOG = logger(__name__)


class HigherOrderNode(Path):
    """Base class of a higher-order node."""

    @property
    def order(self):
        "Return the order of the higher-oder node"
        return len(self)

    @property
    def first_order_relations(self):
        """converts edge relations to first order"""
        return self.relations


class HigherOrderNodeCollection(PathCollection):
    """A collection of edges"""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the EdgeCollection object."""

        # initialize the base class
        super().__init__(*args, **kwargs)

        # class of objects
        self._default_class: Any = HigherOrderNode


class HigherOrderEdge(Edge):
    """Base class of an higher-order edge."""

    @property
    def first_order_relations(self):
        """converts edge relations to first order"""
        return PathPyRelation(self.v.relations +
                              (self.w.relations[-1],),
                              directed=self.directed)


class HigherOrderEdgeCollection(EdgeCollection):
    """A collection of edges"""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the EdgeCollection object."""

        # initialize the base class
        super().__init__(*args, **kwargs)

        # class of objects
        self._default_class: Any = HigherOrderEdge


class HigherOrderNetwork(BaseHigherOrderNetwork, Network):
    """Base class for a Higher Order Network (HON)."""

    def __init__(self, uid: Optional[str] = None, order: int = 1,
                 **kwargs: Any) -> None:
        """Initialize the higer-order network object."""

        # initialize the base class
        super().__init__(uid=uid, directed=True, multiedges=False, **kwargs)

        # order of the higher-order network
        self._order: int = order

        # a container for node objects
        self._nodes: Any = HigherOrderNodeCollection()

        # a container for edge objects
        self._edges: Any = HigherOrderEdgeCollection()

        # a counter for observed paths
        self._observed: Counter = Counter()

        # a counter for (observed) subpaths paths
        self._subpaths: Counter = Counter()

    @property
    def order(self) -> int:
        """Return the order of the higher-order network."""
        return self._order

    @property
    def subpaths(self) -> Counter:
        """Return a counter of (observed) subpaths."""
        return self._subpaths

    @property
    def observed(self) -> Counter:
        """Return a counter of observed paths."""
        return self._observed

    @singledispatchmethod
    def fit(self, data, order: Optional[int] = None,
            subpaths: bool = True) -> None:
        """Fit data to a HigherOrderNetwork"""
        raise NotImplementedError

    @fit.register(PathCollection)
    def _(self, data: PathCollection, order: Optional[int] = None,
          subpaths: bool = True) -> None:

        # update
        if order is not None:
            self._order = order

        # iterate over all paths
        for uid, path in data.items():

            # generate subpaths of order-1 for higher-order nodes
            nodes = path.subpaths(min_length=self.order-1,
                                  max_length=self.order-1,
                                  include_self=True, paths=False)
            # add higher-order nodes to the network
            for node in nodes:
                if node not in self.nodes:
                    self.add_node(*node, frequency=0)
                self.nodes.counter[self.nodes[node].uid] += data.counter[uid]

            # generat higher-order edges
            for _v, _w in zip(nodes[:-1], nodes[1:]):
                _v, _w = self.nodes[_v], self.nodes[_w]

                # check if edge exist otherwise add new edge
                if (_v, _w) not in self.edges:
                    self.add_edge(_v, _w, frequency=0)

                # get edge and update counters
                edge = self.edges[_v, _w]
                self.edges.counter[edge.uid] += data.counter[uid]

                if order == len(path):
                    self._observed[edge.first_order_relations] += data.counter[uid]
                else:
                    self._subpaths[edge.first_order_relations] += data.counter[uid]

        # create all possible higher-order nodes
        if subpaths and self.order > 1:
            for node in self.possible_relations(data, self.order-1):
                if node not in self.nodes:
                    self.add_node(*node, frequency=0)

    def possible_relations(self, collection, length: int) -> list:
        """Return a list of paths of given length."""

        # get paths of length 1
        edges = set(e for p in collection for e in p.subpaths(
            min_length=1, max_length=1, paths=False))

        possible = list(edges)
        for _ in range(length - 1):
            new = list()
            for _v in possible:
                for _w in edges:
                    if _v[-1] == _w[0]:
                        path = PathPyRelation(
                            _v + (_w[1],), directed=self.directed)
                        new.append(path)
            possible = new

        return possible

    def likelihood(self, data: PathCollection, log: bool = False) -> float:
        """Returns the likelihood given some observation data."""

        # some information for debugging
        LOG.debug('I\'m a likelihood of a HigherOrderNetwork')

        # get a list of nodes for the matrix indices
        n = self.nodes.index

        # get the transition matrix
        # TODO Fix this statement
        T = self.transition_matrix(weight='frequency', transposed=True)

        # initialize likelihood
        if log:
            likelihood = 0.0
            _path_likelihood = 0.0
        else:
            likelihood = 1.0
            _path_likelihood = 1.0

        # iterate over observed hon paths
        for uid, path in data.items():

            # get frequency of the observed path
            frequency = data.counter[uid]

            # initial path likelihood
            path_likelihood = _path_likelihood

            # generate subpaths of order-1 for higher-order nodes
            nodes = path.subpaths(min_length=self.order-1,
                                  max_length=self.order-1,
                                  include_self=True, paths=False)

            for _v, _w in zip(nodes[:-1], nodes[1:]):

                # calculate path likelihood
                if log:
                    path_likelihood += np.log(T[n[self.nodes[_w].uid],
                                                n[self.nodes[_v].uid]])
                else:
                    path_likelihood *= T[n[self.nodes[_w].uid],
                                         n[self.nodes[_v].uid]]

            # calculate likelihood
            if log:
                likelihood += path_likelihood * frequency
            else:
                likelihood *= path_likelihood ** frequency

        return likelihood

    @staticmethod
    def window(iterable, size=2):
        """Sliding window for path length"""
        _iter = iter(iterable)
        result = tuple(islice(_iter, size))
        if len(result) == size:
            yield result
        for element in _iter:
            result = result[1:] + (element,)
            yield result


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End: