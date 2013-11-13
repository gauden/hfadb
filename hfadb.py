# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 13:46:49 2013

@author: Gauden Galea
"""
from __future__ import division, print_function
from math import ceil

from hfa.importer import DataImporter
from hfa.indices import HFAIndex

import prettyplotlib as ppl
from prettyplotlib import plt
import numpy as np

# -----------------------------------------------
# CREATE THE DATAFRAMES WITH DATA AND INDICES

HFA = DataImporter().DF
IDX = HFAIndex()

# -----------------------------------------------
# SET UP THE PLOTTING PARAMETERS

countries = sorted(['Russian Federation',
                    'Poland',
                    'Germany',
                    'Denmark',
                    'Sweden',
                    'Latvia',
                    'Lithuania',
                    'Estonia',
                    'Norway',
                    'Iceland',
                    'Belarus',
                    'Finland', ])

countries = IDX.get_countries(names=countries)
#print COUNTRIES.ix[0]['ru']
#print len(COUNTRIES)

comparators = ['European Region']
comparators = IDX.get_countries(names=comparators)

indicators = ['1021']
indicators = IDX.get_indicators(ids=indicators)

PLOT = dict(countries=countries,
            comparators=comparators,
            start=None,
            end=None,
            ymin=50,
            ymax=85,
            xmin=1970,
            xmax=2012,
            indicator=indicators,
            dpi=75,
            width=960,
            height=617,
            cols=4)

# -----------------------------------------------
# DRAW THE PLOT

plt.rc('font', **{'sans-serif': ['Helvetica', 'Arial'],
                  'family': 'sans-serif',
                  'size': 12})

# -----------------------------------------------
# Facet-drawing functions


def get_country_name(row, col, language):
    facet = row * PLOT['cols'] + col
    return PLOT['countries'].ix[facet][language]


def draw_facet(axis, language, series_list, row, col):
    for fun, x, y, kwargs in series_list:
        fun(axis, x, y, **kwargs)
    facet_title = get_country_name(row, col, language)
    axis.set_title(facet_title)
    axis.set_ylim(PLOT['ymin'], PLOT['ymax'])
    axis.set_xlim(PLOT['xmin'], PLOT['xmax'])
    start, end = axis.get_xlim()
    axis.xaxis.set_ticks(np.arange(start, end, 10))
    if not (facet_no in [0, 4, 8]):
        plt.setp(axis.get_yticklabels(), visible=False)
    if not (facet_no in [8, 9, 10, 11]):
        plt.setp(axis.get_xticklabels(), visible=False)


def get_country_series(series_indicator, series_country):
    data = HFA[(HFA.indicator == series_indicator) & (HFA.country == series_country)]
    data.sort('year', inplace=True)
    y = data.value
    x = data.year
    return x, y

# -----------------------------------------------
# Lay out the figure

# Find the number of subplots
cols = PLOT['cols']
rows = int(ceil(len(countries) / cols))
no_of_subplots = cols * rows

# Calculate width and height in inches
w = PLOT['width'] / PLOT['dpi']
h = PLOT['height'] / PLOT['dpi']

for lang in ['en', 'ru']:
    # Set up a figure with that number of plots and
    # dimensions width and height
    f, axarr = plt.subplots(rows, cols)
    f.set_size_inches(w, h)

    # Add a title assuming that only one indicator has been passed
    f.suptitle(PLOT['indicator'].ix[0][lang],
               fontweight='heavy',
               fontsize=18)
    # Add annotation giving the source URL for the HFA database
    f.text(0.01, 0.02,
           'http://data.euro.who.int/hfadb',
           fontsize=14)

    # Select the data for each sub-plot and draw
    indicator = PLOT['indicator'].ix[0]['en']
    comp_country = PLOT['comparators'].ix[0]['en']
    x_comp, y_comp = [list(series) for series in get_country_series(indicator, comp_country)]
    for facet_no in range(len(countries)):
        row = int(facet_no / cols)
        col = facet_no % cols
        ax = axarr[row, col]
        country = PLOT['countries'].ix[facet_no]['en']
        x_focus, y_focus = get_country_series(indicator, country)
        series = [(ppl.plot, x_comp, y_comp, dict(linewidth=3)),
                  (ppl.plot, x_focus, y_focus, dict(linewidth=3))]
        draw_facet(ax, lang, series, row, col)

    # Show and save the whole thing
    f.savefig('{}_{}.png'.format(indicator, lang))