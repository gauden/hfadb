# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 20:10:29 2013

@author: gauden
"""

import os
import glob
import pandas as pd
from bs4 import BeautifulSoup
from StringIO import StringIO


class DataImporter(object):
    '''Load the default dataframe stroed as a pickled Pandas DatFrame.
    Also augment it with any new data found as HTML table files in 
    the raw data directory. The HTML should be in the HFA Table A format.

    Parameters
    ----------
    raw_data_dir: string (optional)
       Path to a raw data directory, defaults to ./data/raw otherwise.
       Looks for any new HTML files in this directory for new data to import.
    
    Data
    -------
    DF: Pandas DataFrame
       A property containing all the HFA data currently 
       stored in the package
       
    '''
    
    def __init__(self, raw_data_dir=None):
        self.DATA_DIR = os.path.join('.', 'data')
        self.DATA_PKL = os.path.join(self.DATA_DIR, 'master_frame.pkl')

        # Load in the default pickled DataFrame or create a new one
        try:
            self.DF = pd.read_pickle(self.DATA_PKL)
        except IOError:
            self.DF = pd.DataFrame()
        
        # Seek out any new files from the raw data directory
        if raw_data_dir:
            self.RAW_DATA_DIR = raw_data_dir
        else:
            self.RAW_DATA_DIR = os.path.join(self.DATA_DIR, 'raw')

        files = self.get_file_list()
        if files:
            for f in files:
                new_df = self.get_dataframe(f)
                self.DF = pd.concat([self.DF, new_df])
            self.DF.to_pickle(self.DATA_PKL) # save the new master dataframe
            for f in files:
                os.remove(f)

    def get_file_list(self):
        '''Glob a list of html files given the path to a data directory.
        
        Default directory is ./data in the idiom of the current OS.'''
        
        raw_data_pattern = os.path.join(self.RAW_DATA_DIR, '*.html')
        files = glob.glob(raw_data_pattern)
        return files
   

    def get_text_from_html(self, filename):
        '''Scrape an HFA DB HTML table in 'Table A' format 
        and return tab-delimited version.'''
        
        with open(filename, 'r') as f:
            soup = BeautifulSoup(f.read())
            table = soup.find('table')
            rows = table.findAll('tr')
            indicator = rows[0].text
            
            # prepare the headers and initialise the result
            headers = ['country_id', 'country', 'indicator']
            headers += [td.text for td in rows[1].findAll('td')][1:]
            result = '\t'.join(headers) + '\n'
            
            # read in row by row of data and add to results
            for row in rows[2:]:
                cells = [td.text for td in row.findAll('td')]
                record = cells[0].split(' ',1)
                record.append(indicator)
                record.extend([cell for cell in cells[1:]])
                result += '\t'.join(record) +'\n'
            return result

    def get_df_from_text(self, txt):
        '''Given a tab-delimited text table, parse out a Pandas DataFrame.'''
        
        df = pd.read_table(StringIO(txt), sep='\t', na_values=['...'])
        df = pd.melt(df, id_vars=['country_id', 'country', 'indicator'])
        df.columns = ['country_id', 'country', 'indicator', 'year', 'value']
        df = df.dropna()
        df[['year']] = df[['year']].astype(int)
        df[['value']] = df[['value']].astype(float)
        return df
    
    def get_dataframe(self, filename):
        '''Given a pathname to an HTML table file, return a Pandas DataFrame.'''
        
        text_table = self.get_text_from_html(filename)
        df = self.get_df_from_text(text_table)
        return df