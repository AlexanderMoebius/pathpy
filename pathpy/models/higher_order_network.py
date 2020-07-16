"""Higher-order network class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : higher_order_network.py -- Basic class for a HON
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2020-07-15 17:54 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

from __future__ import annotations
from typing import Any, Optional, Union
from itertools import islice
from singledispatchmethod import singledispatchmethod

from pathpy import logger
from pathpy.core.node import Node, NodeCollection
from pathpy.core.edge import Edge, EdgeCollection, EdgeSet
from pathpy.core.path import Path, PathCollection
from pathpy.core.network import Network

from pathpy.models.models import ABCHigherOrderNetwork

# create logger for the Network class
LOG = logger(__name__)


class HigherOrderNetwork(ABCHigherOrderNetwork, Network):
    """Base class for a Higher Order Network (HON)."""

    def __init__(self, uid: Optional[str] = None, order: int = 1,
                 **kwargs: Any) -> None:
        """Initialize the higer-order network object."""

        # initialize the base class
        super().__init__(uid=uid, directed=True, temporal=False,
                         multiedges=False, **kwargs)

        # order of the higher-order network
        self._order: int = order

        # a container for node objects
        self._nodes: Any = HigherOrderNodeCollection()

        # a container for edge objects
        self._edges: Any = HigherOrderEdgeCollection(nodes=self._nodes)

    @property
    def order(self) -> int:
        """Return the order of the higher-order network."""
        return self._order

    def degrees_of_freedom(self, mode: str = 'path') -> int:
        """Returns the degrees of freedom of the higher-order network.

        Since probabilities must sum to one, the effective degree of freedom is
        one less than the number of nodes

        .. math::

           \\text{dof} = \\sum_{n \\in N} \\max(0,\\text{outdeg}(n)-1)

        """
        # initialize degree of freedom
        degrees_of_freedom: int = 0
        return degrees_of_freedom

    def summary(self) -> str:
        """Returns a summary of the higher-order network.

        The summary contains the name, the used network class, the order, the
        number of nodes and edges.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        Returns
        -------
        str
            Returns a summary of important higher-order network properties.

        """
        summary = [
            'Uid:\t\t\t{}\n'.format(self.uid),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            # 'Directed:\t\t{}\n'.format(str(self.directed)),
            # 'Multi-Edges:\t\t{}\n'.format(str(self.multiedges)),
            'Order:\t\t\t{}\n'.format(self.order),
            'Number of nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of edges:\t{}'.format(self.number_of_edges()),
        ]
        attr = self.attributes.to_dict()
        if len(attr) > 0:
            summary.append('\n\nNetwork attributes\n')
            summary.append('------------------\n')
        for k, v in attr.items():
            summary.append('{}:\t{}\n'.format(k, v))

        return ''.join(summary)

    @singledispatchmethod
    def fit(self, data, order: int = 1, subpaths: bool = True) -> None:
        """Fit data to a HigherOrderNetwork"""
        raise NotImplementedError

    @fit.register(PathCollection)
    def _(self, data: PathCollection, order: int = 1, subpaths: bool = True) -> None:
        print("I'm a PathCollection object")

        # TODO: create function to transfer base data from PathCollection object
        # --- START ---
        nc = NodeCollection()
        for node in data.nodes.values():
            nc.add(node)

        ec = EdgeCollection(nodes=nc)
        for edge in data.edges.values():
            ec.add(edge)

        self._nodes = HigherOrderNodeCollection(nodes=nc, edges=ec)
        # --- END ---

        # iterate over all paths
        for path in data:

            # get frequency of the observed path
            # TODO: define keyword in config file
            frequency = path.attributes.get('frequency', 1)

            nodes: list = []
            if order == 0:
                for node in path.nodes:
                    if (node,) not in self.nodes:
                        self.nodes.add(node)
            elif order == 1:
                nodes.extend([tuple([n]) for n in path.nodes])

            elif 1 < order <= len(path):
                for subpath in self.window(path.edges, size=order-1):
                    nodes.append(subpath)

            elif order == len(path)+1:
                if tuple(path.edges) not in self.nodes:
                    self.nodes.add(tuple(path.edges))

            else:
                pass

            _edges = set()
            for _v, _w in zip(nodes[:-1], nodes[1:]):

                if _v not in self.nodes:
                    self.nodes.add(_v)

                if _w not in self.nodes:
                    self.nodes.add(_w)

                _nodes = (self.nodes[_v], self.nodes[_w])
                if _nodes not in self.edges:
                    self.edges.add(*_nodes, frequency=0, observed=0)

                _edges.add(self.edges[_nodes])

            for edge in _edges:
                edge['frequency'] += frequency
                if order == len(path):
                    edge['observed'] += frequency

    @staticmethod
    def window(iterable, size=2):
        """Sliding window for path length"""
        ite = iter(iterable)
        result = tuple(islice(ite, size))
        if len(result) == size:
            yield result
        for elem in ite:
            result = result[1:] + (elem,)
            yield result


class HigherOrderNode(Node, Path):
    """Base class of a higher order node."""

    def __init__(self, *args: Union[Node, Edge], uid: Optional[str] = None,
                 **kwargs: Any) -> None:

        # initializing the parent classes
        Node.__init__(self, uid, **kwargs)
        Path.__init__(self, *args, uid=uid, **kwargs)

        self['label'] = '-'.join([n.uid for n in self.nodes])

    @property
    def order(self) -> int:
        """Returns the order of the higher-order node."""
        return self.number_of_nodes(unique=False)

    def summary(self) -> str:
        """Returns a summary of the higher-order node.

        The summary contains the name, the used node class, the order, the
        number of nodes and the number of edges.

        If logging is enabled(see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        Returns
        -------
        str

        Return a summary of the path.

        """
        summary = [
            'Uid:\t\t\t{}\n'.format(self.uid),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Order:\t\t\t{}\n'.format(self.order),
            'Number of unique nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of unique edges:\t{}'.format(self.number_of_edges()),
        ]
        return ''.join(summary)


class HigherOrderNodeCollection(PathCollection):
    """Higher-order node collection."""

    def __init__(self, nodes=None, edges=None) -> None:
        """Initialize the NodeCollection object."""

        # initialize the base class
        super().__init__(nodes=nodes, edges=edges)

        # class of objects
        self._path_class = HigherOrderNode

    def _if_exist(self, path: Any, **kwargs: Any) -> None:
        """If the node already exists"""
        print('dddddddddd')


class HigherOrderEdge(Edge):
    """Base class of a higher order edge."""

    def __init__(self, v: HigherOrderNode, w: HigherOrderNode,
                 uid: Optional[str] = None, **kwargs: Any) -> None:
        # initializing the parent classes
        super().__init__(v=v, w=w, uid=uid, **kwargs)


class HigherOrderEdgeCollection(EdgeCollection):
    """Higher-order node collection."""

    def __init__(self, nodes: Optional[HigherOrderNodeCollection] = None) -> None:
        """Initialize the HigherOrderEdgeCollection object."""

        # initialize the base class
        super().__init__()

        self._nodes = HigherOrderNodeCollection()
        if nodes is not None:
            self._nodes = nodes

        # class of objects
        self._edge_class = HigherOrderEdge

    def __getitem__(self,
                    key: Union[str, tuple, Edge]) -> Union[Edge, EdgeSet, EdgeCollection]:
        """Returns a node object."""

        if isinstance(key, tuple):
            _node = tuple(self.nodes[i] for i in key)
            if self.multiedges:
                edge = self._nodes_map[_node]
            else:
                edge = self._nodes_map[_node][-1]

        elif isinstance(key, self._edge_class) and key in self:
            edge = key
        else:
            edge = self._map[key]
        return edge

    @singledispatchmethod
    def __contains__(self, item) -> bool:
        """Returns if item is in edges."""
        return super().__contains__(item)

    @__contains__.register(tuple)  # type: ignore
    @__contains__.register(list)
    def _(self, item: Union[tuple, list]) -> bool:
        """Returns if item is in edges."""
        _contain: bool = False

        if all([isinstance(i, (str, Node)) for i in item]):
            try:
                if tuple(self.nodes[i] for i in item) in self._nodes_map:
                    _contain = True
            except KeyError:
                pass
        elif all([isinstance(i, tuple) for i in item]):
            try:
                if self._nodes_map[(self.nodes[item[0]],
                                    self.nodes[item[1]])] is not None:
                    _contain = True
            except KeyError:
                pass

        return _contain

    @singledispatchmethod
    def add(self, *edge, **kwargs: Any) -> None:
        """Add multiple edges. """

        raise NotImplementedError

    @add.register(HigherOrderEdge)  # type: ignore
    def _(self, *edge: HigherOrderEdge, **kwargs: Any) -> None:
        super().add(*edge, **kwargs)

    @add.register(HigherOrderNode)  # type: ignore
    def _(self, *edge: HigherOrderNode, **kwargs: Any) -> None:
        super().add(*edge, **kwargs)

    @add.register(str)  # type: ignore
    def _(self, *edge: str, **kwargs: Any) -> None:
        super().add(*edge, **kwargs)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End: