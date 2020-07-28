import urllib.request
import os, time, gzip
import numpy as np
from progress_bar import progress_bar

__author__ = 'Josef Doundoulakis'
__maintainer__ = 'Josef Doundoulakis'
__email__ = 'doundoulakis.iosif@outlook.com'


#  Organizing the necessary data for analysis
#  and their respective urls

data = (('time_series_covid19_confirmed_global.csv', 'https://raw.githubusercontent.com/'
                                                     'CSSEGISandData/COVID-19/master/'
                                                     'csse_covid_19_data/'        # Infection cases time-series JHS
                                                     'csse_covid_19_time_series/'
                                                     'time_series_covid19_confirmed_global.csv'),
             ('time_series_covid19_recovered_global.csv', 'https://raw.githubusercontent.com/'
                                                          'CSSEGISandData/COVID-19/master/'
                                                          'csse_covid_19_data/'        # Recovery cases time-series JHS
                                                          'csse_covid_19_time_series/'
                                                          'time_series_covid19_recovered_global.csv'),
             ('time_series_covid19_deaths_global.csv', 'https://raw.githubusercontent.com/'
                                                       'CSSEGISandData/COVID-19/master/'
                                                       'csse_covid_19_data/'           # Death cases time-series JHS
                                                       'csse_covid_19_time_series/'
                                                       'time_series_covid19_deaths_global.csv'),
             ('acaps_covid19_government_measures_dataset.xlsx',
              'https://www.acaps.org/sites/acaps/files/resources'  # Government measures dataset from ACAPS
              '/files/acaps_covid19_government_measures_dataset.xlsx'),
             ('2020.csv.gz',                                       # Climate data from GHCN for the year 2020
              'ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/2020.csv.gz'),
             ('GHCN_country_codes.txt',
              'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-countries.txt'))  # GHCN data country codes

data_dir = os.listdir(os.path.join(os.getcwd(), 'data'))
# _____________________________________________________________________________________


class File:

    def __init__(self, filename, url, rel_dir):

        self.filename = filename
        self.url = url
        self.rel_dir = rel_dir
        try:
            self.age = (time.time()-os.path.getmtime(self.rel_dir+'/'+self.filename))/(24*3600)
        except WindowsError as e:
            self.age = 0
        if not filename == 'GHCN_country_codes.txt':
            self.tobeupdated = True if self.age > 1 else False
        elif filename == 'GHCN_country_codes.txt':
            self.tobeupdated = False

    def download(self):

        print('\nDownloading file "{}"...'.format(self.filename))
        urllib.request.urlretrieve(url=self.url, filename=self.rel_dir+'/'+self.filename, reporthook=progress_bar)

        if self.filename.endswith('.gz'):

            print('\nExtracting average temperature data from file "{}"...'.format(self.filename))

            with gzip.open(self.rel_dir+'/'+self.filename, 'rt') as g:

                start = time.time()
                m = np.array([a.split(',') for a in list(g) if 'TAVG' in a.split(',')])
                np.savetxt(self.rel_dir+'/'+'GHCN_avg_temperature_data.csv', m,
                           delimiter=',', fmt='%s')
                g.close()
                end = time.time()

            print('Done in {} seconds.'.format(round(end-start,1)))


# ________________________________________________________________________________________


files = (File(x, y, 'data') for x, y in data)

for file in files:

    if (file.filename not in data_dir) or (file.filename in data_dir and file.tobeupdated):

        if 'acaps' in file.filename:

            try:

                file.download()

            except Exception as e:

                print(e.args[0], 'Acaps dataset url varies. Attempting different link.')

                file.url = 'https://www.acaps.org/sites/acaps/files/resources' \
                           '/files/acaps_covid19_government_measures_dataset_0.xlsx'

                file.download()

        else:

            file.download()

    else:

        print('\n"{}" file has been recently '
              'updated.'.format(file.filename)) if not file.filename == 'GHCN_country_codes.txt'\
                                                else print('\n"{}" file exists.'.format(file.filename))

