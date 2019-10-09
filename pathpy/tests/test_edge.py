#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_edge.py -- Test environment for the Edge class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2019-10-09 14:27 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest

from pathpy import Edge, Node, config


@pytest.fixture(params=[True, False])
def nodes(request):
    """Generate node objects."""
    if not request.param:

        v = Node('v')
        w = Node('w')
    else:
        config.set('computation', 'check_code', 'true')
        v = 'v'
        w = 'w'
    return v, w


def test_uid(nodes):
    """Test the uid assignment."""

    v, w = nodes

    vw = Edge(v, w)

    assert isinstance(vw, Edge)
    assert isinstance(vw.uid, str)
    assert vw.uid == 'v-w'
    assert isinstance(vw.v, Node) and vw.v.uid == 'v'
    assert isinstance(vw.w, Node) and vw.w.uid == 'w'

    vw = Edge(v, w, uid='vw')

    assert isinstance(vw, Edge)
    assert isinstance(vw.uid, str)
    assert vw.uid == 'vw'


def test_setitem(nodes):
    """Test the assignment of attributes."""

    v, w = nodes

    vw = Edge(v, w)
    vw['capacity'] = 5.5

    assert vw['capacity'] == 5.5


def test_getitem(nodes):
    """Test the extraction of attributes."""

    v, w = nodes

    vw = Edge(v, w, length=10)

    assert vw['length'] == 10
    with pytest.raises(KeyError):
        vw['attribute not in dict']


def test_repr(nodes):
    """Test printing the node."""

    v, w = nodes

    vw = Edge(v, w)

    assert vw.__repr__() == 'Edge v-w'


def test_update(nodes):
    """Test update node attributes."""
    v, w = nodes
    vw = Edge(v, w, length=5)

    assert vw['length'] == 5

    vw.update(length=10, capacity=6)

    assert vw['length'] == 10
    assert vw['capacity'] == 6


def test_copy(nodes):
    """Test to make a copy of a node."""

    v, w = nodes
    vw = Edge(v, w)
    ab = vw.copy()

    assert ab.uid == vw.uid == 'v-w'


def test_weight(nodes):
    """Test the weight assigment."""

    v, w = nodes

    vw = Edge(v, w)

    assert vw.weight() == 1.0

    vw['weight'] = 4

    assert vw.weight() == 4.0
    assert vw.weight(weight=None) == 1.0
    assert vw.weight(weight=False) == 1.0

    vw['length'] = 5
    assert vw.weight('length') == 5.0

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
