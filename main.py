# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 13:46:49 2013

@author: Gauden Galea
"""
from __future__ import print_function
from pprint import pprint, pformat
import glob
import os
import yaml

from hfa.importer import DataImporter
from hfa.indices import HFAIndex


YAML_DIR = os.path.join('yaml')


def get_yaml():
    files = [f for f in glob.glob(os.path.join(YAML_DIR, "*.yaml"))]
    return files


class Plot(object):
    def __init__(self, specs, index, hfadb):
        self.specs = specs
        self.data = self.get_plot_dataset(index, hfadb)

    def get_plot_dataset(self, database):
        indicators = self.specs.get('indicators', [])
        countries = self.specs.get('countries', [])
        comparators = self.specs.get('comparators', [])
        countries.extend(comparators)
        end = self.specs.get('end', None)
        start = self.specs.get('start', None)
        return self._get_plot_data(countries, indicators, start, end, index, hfadb)

    def _get_plot_data(self, countries, indicators, start, end, index, hfadb):
        pass

    def __repr__(self):
        return pformat(self.specs)


def create_plot_from_yaml(yaml_file):
    with open(yaml_file, 'rb') as f:
        specs = yaml.load(f.read())
        plot = Plot(specs)
        pprint(plot)

def main():
    hfa_db = DataImporter().DF
    index = HFAIndex()
    files = get_yaml()
    if files:
        for yaml_file in files:
            create_plot_from_yaml(yaml_file, index, hfadb)
            print('Processed: {}'.format(yaml_file))
    print('Run completed.')


if __name__ == '__main__':
    main()