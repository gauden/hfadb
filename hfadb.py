# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 13:46:49 2013

@author: Gauden Galea
"""
from __future__ import division
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

indicators = ['1320']
indicators = IDX.get_indicators(ids=indicators)

PLOT = dict(countries=countries,
            comparators=comparators,
            start=None,
            end=None,
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


def get_country_name(r, c, lang):
    facet = r * PLOT['cols'] + c
    return PLOT['countries'].ix[facet][lang]


def draw_facet(ax, lang, series, r, c):
    for fun, x, y in series:
        fun(ax, x, y, alpha=1)
    facet_title = get_country_name(r, c, lang)
    ax.set_title(facet_title)
    ax.set_ylim(0, 900)
    ax.set_xlim(1970, 2013)
    start, end = ax.get_xlim()
    ax.xaxis.set_ticks(np.arange(start, end, 10))
    if not (facet_no in [0, 4, 8]):
        plt.setp(ax.get_yticklabels(), visible=False)
    if not (facet_no in [8, 9, 10, 11]):
        plt.setp(ax.get_xticklabels(), visible=False)


def get_country_series(indicator, country):
    data = HFA[(HFA.indicator == indicator) & (HFA.country == country)]
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
        r = int(facet_no / cols)
        c = facet_no % cols
        ax = axarr[r, c]
        country = PLOT['countries'].ix[facet_no]['en']
        x_focus, y_focus = get_country_series(indicator, country)
        series = [(ppl.scatter, x_comp, y_comp),
                  (ppl.scatter, list(x_focus), list(y_focus))]
        draw_facet(ax, lang, series, r, c)

    plt.ylim([0, 1000])
    # Show and save the whole thing
    f.savefig('{}_{}.png'.format(indicator, lang))