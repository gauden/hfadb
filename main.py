# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 13:46:49 2013

@author: Gauden Galea
"""
from __future__ import print_function
import glob
import os
import yaml

from hfa.importer import DataImporter
from hfa.indices import HFAIndex
from hfa.plot import Plot

YAML_DIR = os.path.join('yaml')
IDX_DIR = os.path.join('hfa', 'index_data')


def read_yaml_file(yaml_file):
    with open(yaml_file, 'rb') as f:
        specs = yaml.load(f.read())
        print('Processed: {}'.format(yaml_file))
    return specs


def expand_country_sets(countries):
    result = []
    country_sets = read_yaml_file(os.path.join(IDX_DIR, 'country_sets.yaml'))
    for idx in countries:
        if idx in country_sets:
            result.extend(country_sets[idx])
        else:
            result.append(idx)
    return set(result)


def get_yaml():
    plots = []
    basic_config = read_yaml_file(os.path.join(YAML_DIR, "config.yaml"))
    files = [f for f in glob.glob(os.path.join(YAML_DIR, "*.yaml"))]
    if files:
        for yaml_file in files:
            if 'config' not in yaml_file:
                specs = read_yaml_file(yaml_file)  # read specific config
                final = basic_config.copy() if basic_config else dict() # merge it with general config
                final.update(specs)
                final['countries'] = expand_country_sets(final['countries'])
                # TODO generalise this
                if final['indicator'] == 176:
                    final['indicator'] = '0260'
                plots.append(final)  # add final result to list of plots
    return plots

def main():
    hfa_db = DataImporter().DF
    index = HFAIndex()
    plot_specs = get_yaml()
    if plot_specs:
        for specs in plot_specs:
            plot = Plot(specs, index, hfa_db)
            plot.render()
            #print(plot)
    print('Run completed.')


if __name__ == '__main__':
    main()