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


def read_yaml_file(yaml_file):
    with open(yaml_file, 'rb') as f:
        specs = yaml.load(f.read())
        print('Processed: {}'.format(yaml_file))
    return specs


def get_yaml():
    plots = []
    basic_config = read_yaml_file(os.path.join(YAML_DIR, "config.yaml"))
    files = [f for f in glob.glob(os.path.join(YAML_DIR, "*.yaml"))]
    if files:
        for yaml_file in files:
            if 'config' not in yaml_file:
                specs = read_yaml_file(yaml_file)  # read specific config
                final = basic_config.copy()  # merge it with general config
                final.update(specs)
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