from __future__ import division
import os
from pprint import pformat

import prettyplotlib as ppl
from prettyplotlib import plt
import numpy as np
import pandas as pd


class SmallMultipleChart(object):
    def __init__(self, plot, langs=['en', 'ru']):
        self.plot = plot
        self.langs = langs
        self._set_defaults()

        self.figures = {}
        for lang in self.langs:
            self.plot.specs['facets'] = len(self.plot.specs['countries'])
            rows, cols = self._get_grid(self.plot.specs['facets'])
            self.plot.specs['cols'] = cols
            self.plot.specs['rows'] = rows
            figure, ax_array = plt.subplots(rows, cols)
            ax_array = self._hide_axes(ax_array, rows, cols)
            self.figures[lang] = (figure, ax_array)

    def render(self):
        # Set global font to ensure ability to display Cyrillic
        plt.rc('font', **{'sans-serif': ['Helvetica', 'Arial'],
                          'family': 'sans-serif'})
        for lang in self.langs:
            figure, ax_array = self.figures[lang]
            figure, title = self._set_up_figure(figure, lang)
            self._get_axis_limits()
            self._render_axes(ax_array, lang)
            self._save_fig(figure, title, lang)

    def _get_axis_limits(self):
        xmin = self.plot.specs.get('xmin', '')
        if xmin != '':
            xmin = self.plot.data.year.min()

        xmax = self.plot.specs.get('xmax', '')
        if xmax != '':
            xmax = self.plot.data.year.max()
        self.plot.specs['xlim'] = (xmin, xmax)

        ymin = self.plot.specs.get('ymin', '')
        if ymin == '':
            ymin = 100 * int((self.plot.data.value.min() - 95) / 100)
        ymax = self.plot.specs.get('ymax', '')
        if ymax == '':
            ymax = 100 * int((self.plot.data.value.max() + 95) / 100)
        self.plot.specs['ylim'] = (ymin, ymax)

    def _render_axes(self, ax_array, lang):
        comp_series = {}
        for comp in self.plot.specs['comparators']:
            y_comp = self.plot.data[self.plot.data.country == comp].value
            x_comp = self.plot.data[self.plot.data.country == comp].year
            comp_series[comp] = (x_comp, y_comp)

        for facet in range(self.plot.specs['facets']):
            cols = self.plot.specs['cols']
            r = facet // cols
            c = facet % cols
            ax = ax_array[r][c]

            country = self.plot.specs['countries'][facet]
            country = self.plot.index.get_countries(names=[country])
            y = self.plot.data[self.plot.data.country == country['en'][0]].value
            x = self.plot.data[self.plot.data.country == country['en'][0]].year

            ax_title = country[lang][0]
            ax.text(0.5, 0.95, ax_title,
                    verticalalignment='bottom', horizontalalignment='center',
                    transform=ax.transAxes, color=self.plot.specs.get('color', None),
                    fontsize=10, fontweight='bold')

            ax.set_ylim(self.plot.specs['ylim'])
            if self.plot.specs.get('ystep', None):
                ax.yaxis.set_ticks(np.arange(self.plot.specs['ylim'][0], 
                                             self.plot.specs['ylim'][1], 
                                             self.plot.specs['ystep']))

            start, end = self.plot.specs['xlim']
            if self.plot.specs.get('xstep', None):
                ax.xaxis.set_ticks(np.arange(self.plot.specs['xlim'][0], 
                                             self.plot.specs['xlim'][1], 
                                             self.plot.specs['xstep']))
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(10)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(10)

            # Draw in-focus series: strong colour and opaque
            ppl.plot(ax, x, y, alpha=1.0, linewidth=1, color=self.plot.specs.get('color', None))
            ppl.scatter(ax, x, y, s=12.0, alpha=1.0, color=self.plot.specs.get('color', None))

            # Draw comparators: light, translucent, overlapping main series
            for x_comp, y_comp in comp_series.values():
                ppl.plot(ax, x_comp, y_comp, alpha=0.35, linewidth=5)

    def _set_up_figure(self, figure, lang):
        title = self._get_title(lang)
        data_source = self._get_data_source(lang)

        dpi = self.plot.specs['dpi']
        width = self.plot.specs['width'] / dpi
        height = self.plot.specs['height'] / dpi

        figure.set_size_inches(width, height)

        # Add a main title
        figure.suptitle(title, fontweight='heavy', fontsize=18)
        # Add annotation crediting the source of data at bottom of slide
        figure.text(0.5, 0.02, data_source, fontsize=14, horizontalalignment='center')

        caption = self.plot.specs.get('caption', None)
        if caption:
            figure.text(caption['x'], caption['y'], 
                        caption[lang], fontsize=caption['size'])

        return figure, title

    def _hide_axes(self, ax_array, rows, cols):
        for fct in range(rows * cols):
            r = fct // cols
            c = fct % cols
            ax = ax_array[r][c]

            if fct >= self.plot.specs['facets']:
                ax.axis('off')

            # Hide y axis labels
            if c > 0:
                plt.setp(ax.get_yticklabels(), visible=False)
            ## Hide x axis labels
            if fct + cols < self.plot.specs['facets']:
                plt.setp(ax.get_xticklabels(), visible=False)
        return ax_array

    def _get_grid(self, facets):
        """
        Private function to calculate optimal layout of the grid,
        with one facet for each country in the dataset.
        Allows a maximum of 100 x 99 facets -- it is up to the user
        to ensure that the size of the plot, labels, etc, are
        proportionate.

        @return: tuple (rows, cols).
        """
        #if facets > 20:
        #    raise IndexError('This type of graph cannot have more than 20 facets.')
        for cols in range(1, 100):
            for rows in range(1, 99):
                if (cols * rows >= facets
                    and cols - rows < 3
                    and cols >= rows):
                    return rows, cols

    def _get_title(self, lang):
        title = self.plot.specs.get('title', {}).get(lang, '')
        if not title:
            key = self.plot.specs.get('indicator', '')
            title = self.plot.index[key][lang][0]
        return title

    def _get_data_source(self, lang):
        data_source = self.plot.specs.get('data_source', {}).get(lang, '')
        if not data_source:
            data_source = 'http://data.euro.who.int/hfadb/'
        return data_source

    def _save_fig(self, figure, title, lang):
        # Show and save the whole thing
        stub = self.plot.specs.get('filename', '')
        stub = stub if stub else self.plot.specs['indicator']
        fn = '{}_{}.png'.format(stub, lang)
        fn = os.path.join('img', fn)
        figure.savefig(fn)

    def _set_defaults(self):
        self.plot.specs['color'] = self.plot.specs.get('color', 'red')


class Plot(object):
    def __init__(self, specs, index, hfa_db):
        self.specs = specs
        self.specs['countries'] = sorted(self.specs['countries'])
        self.index = index
        self.data = self.get_plot_dataset(hfa_db)

    def render(self):
        if self.specs['type'] == 'Small multiples':
            chart = SmallMultipleChart(self)
            chart.render()

    def get_plot_dataset(self, hfa_db):
        key = self.specs.get('indicator', '')
        indicator = self.index[key]
        countries = self.specs.get('countries', [])
        comparators = self.specs.get('comparators', [])
        all_countries = countries + comparators
        end = self.specs.get('xmax', None)
        start = self.specs.get('xmin', None)
        dataset = self._get_plot_data(all_countries,
                                      indicator,
                                      start,
                                      end,
                                      hfa_db)
        return dataset

    def _get_plot_data(self, all_countries, indicator, start, end, hfa_db):
        assert isinstance(all_countries, list)
        assert isinstance(indicator, pd.DataFrame)
        assert isinstance(hfa_db, pd.DataFrame)

        if not start or not isinstance(start, int):
            start = hfa_db.year.min()
        if not end or not isinstance(end, int):
            end = hfa_db.year.max()

        data = hfa_db[hfa_db.country.isin(all_countries)]
        data = data[data.indicator == indicator.en[0]]
        data = data[data.year >= start]
        data = data[data.year <= end]
        data.sort('year', inplace=True)
        return data

    def __repr__(self):
        return pformat(dict(specs=self.specs,
                            index=self.index,
                            data=self.data))
