# -*- coding: utf-8 -*-
"""
When run as a main module, import country names and indicators
in English and Russian, prepare relevant dictionaries,
and pickle them.
    
Created on Sat Nov  9 13:29:42 2013

@author: gauden
"""

import codecs
import os
import re
import HTMLParser
import pandas as pd


class HFAIndex(object):
    '''
    A Pandas DataFrame that containscountry names and indicators
    in English and Russian languages.
    '''

    def __init__(self, data_dir=os.path.join('.', 'hfa', 'index_data')):
        self.data = Extractor(data_dir).data

    def get_subset(self,
                   names=[],
                   ids=[],
                   lang=None,
                   index_type='countries'):
        '''
        Return a list of country/indicator names and indices.

        Parameters
        ----------
        names: list of unicode elements (optional)
           Names of relevant countries/indicators to return.
           If empty, return all.
        ids: list of unicode elements (optional)
           Index of relevant countries/indicators to return.
           If empty, return all.
        lang: string (optional)
           'en' or 'ru' return the English or Russian names respectively.
           If None, return both languages
        '''
        result = self.data[self.data['index_type'] == index_type]
        result = result.drop('index_type', 1)

        # collect subsets by name and id
        if names:
            result_by_name = result.loc[(result['en'].isin(names)) | (result['ru'].isin(names))]
        if ids:
            result_by_id = result.ix[ids]

        # Combine the subsets if these are desired and not empty
        names_requested = names and result_by_name
        ids_requested = ids and result_by_id
        if names_requested and not ids_requested:
            result = result_by_name
        elif ids_requested and not names_requested:
            result = result_by_id
        elif ids_requested and names_requested:
            result = pd.merge(result_by_name, result_by_id, how='outer')

        # return the desired language column alone if this is specified
        if lang:
            result = result[lang]
        return result

    def get_countries(self, names=[], ids=[], lang=None):
        return self.get_subset(names, ids, lang, index_type='countries')

    def get_indicators(self, names=[], ids=[], lang=None):
        return self.get_subset(names, ids, lang, index_type='indicators')

    def find_indicators(self, needle):
        '''
        Return the record of a particular indicator, or set of indicators
        that match a given string.

        Parameters
        ----------
        needle: unicode object
           Names of relevant countries to return.
           If empty, return all.

        Returns
        ----------
        indics: pandas DataFrame
           All records that contain the needle in en or ru cols.
           
        '''

        result = self.data[self.data['index_type'] == 'indicators']
        result = result.drop('index_type', 1)

        # df[df['A'].str.contains("hello")]
        result = result.loc[(result['en'].str.contains(needle))
                            | (result['ru'].str.contains(needle))]
        return result


class Extractor(object):
    '''
    Expect to find raw country and indicator files 
    in the index_data directory at same level.
    
    These files should be called:
    - raw_indicators_[en/ru].txt and
    - raw_countries_[en/ru].txt
    Parse and extract data, and create Pandas DataFrame.
    '''

    PATTERN = re.compile(r"'\d{4}\s[^']+'")
    H = HTMLParser.HTMLParser()

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.data = self.extract_data()

    def _dissect_file(self, fn, index_type):
        records = []
        with codecs.open(fn, 'rb', 'cp1251') as f:
            # read as Cyrillic encoding and remove some gibberish
            holder = f.read()
            holder = holder.replace('@mavr@', '')
        m = re.findall(self.PATTERN, holder)
        for item in m:
            item = item[1:-1]
            idx, indicator = item.split(' ', 1)
            idx = unicode(idx)
            indicator = self.H.unescape(indicator)
            records.append((idx, index_type, indicator))
        return records

    def extract_data(self):
        results = []
        for index_type in ['countries', 'indicators']:
            data = None
            for lang in ['ru', 'en']:
                fn = 'raw_{prefix}_{lang}.txt'.format(prefix=index_type,
                                                      lang=lang)
                fn = os.path.join(self.data_dir, fn)
                records = self._dissect_file(fn, index_type)
                records = pd.DataFrame.from_records(records[:],
                                                    columns=['idx', 'index_type', lang])
                if data:
                    data = pd.merge(data, records)
                else:
                    data = records
            results.append(data)
        df = pd.concat(results)
        df = df.set_index('idx')
        return df


def main():
    data_dir = os.path.join('.', 'index_data')
    IDX = HFAIndex(data_dir)
    print '''\n\nIDX.get_countries(ids=['0006', '0001'])'''
    print IDX.get_countries(ids=['0006', '0001'])
    print '''\n\nIDX.get_countries(names=['Albania', 'Azerbaijan', 'France'])'''
    print IDX.get_countries(names=['Albania', 'Azerbaijan', 'France'])
    print '''\n\nIDX.get_countries(names=['Albania', 'Azerbaijan', 'France'], ids=['0006', '0001'])'''
    print IDX.get_countries(names=['Albania', 'Azerbaijan', 'France'], ids=['0006', '0001'])
    print '''\n\nIDX.get_countries(ids=['0006', '0001'], names=['Albania', 'Azerbaijan', 'France'])'''
    print IDX.get_countries(ids=['0006', '0001'], names=['Albania', 'Azerbaijan', 'France'])
    print '''\n\nIDX.get_indicators(ids=['1320'])'''
    print IDX.get_indicators(ids=['1320'])


if __name__ == '__main__':
    main()