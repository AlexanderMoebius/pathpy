"""Initialize matplotlib plotting functions"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : __init__.py -- matplotlib plotting cunctions
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2021-06-22 13:46 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
# flake8: noqa
# pylint: disable=unused-import

from pathpy.visualisations._matplotlib.network_plots import NetworkPlot

PLOT_CLASSES: dict = {
    "network": NetworkPlot,
}


def plot(data, kind, **kwargs):
    """Plot function"""
    return PLOT_CLASSES[kind](data, **kwargs)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
