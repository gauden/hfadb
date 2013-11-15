from pprint import pformat

class Plot(object):
    def __init__(self, specs, index, hfa_db):
        self.specs = specs
        self.data = self.get_plot_dataset(hfa_db)
        self.index = index

    def get_plot_dataset(self, hfa_db):
        indicators = self.specs.get('indicators', [])
        countries = self.specs.get('countries', [])
        comparators = self.specs.get('comparators', [])
        countries.extend(comparators)
        end = self.specs.get('end', None)
        start = self.specs.get('start', None)
        dataset = self._get_plot_data(countries, indicators, start, end, hfa_db)
        return dataset

    def _get_plot_data(self, countries, indicators, start, end, hfa_db):
        if not start:
            start = hfa_db.year.min()
        if not end:
            end = hfa_db.year.min()

        data = hfa_db[hfa_db.country.isin(countries)]
        data = data[data.indicator.isin(indicators)]
        data = data[data.year >= start]
        data = data[data.year <= end]
        data.sort('year', inplace=True)

        return data

    def __repr__(self):
        return pformat(self.specs)
