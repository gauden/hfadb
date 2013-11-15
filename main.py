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


def get_yaml():
    plots = []
    files = [f for f in glob.glob(os.path.join(YAML_DIR, "*.yaml"))]
    if files:
        for yaml_file in files:
            with open(yaml_file, 'rb') as f:
                specs = yaml.load(f.read())
                plots.append(specs)
                print('Processed: {}'.format(yaml_file))
    return plots

def main():
    hfa_db = DataImporter().DF
    index = HFAIndex()
    plot_specs = get_yaml()
    if plot_specs:
        for specs in plot_specs:
            plot = Plot(specs, index, hfa_db)
            print(plot)
            plot.render()  # TODO
    print('Run completed.')


if __name__ == '__main__':
    main()