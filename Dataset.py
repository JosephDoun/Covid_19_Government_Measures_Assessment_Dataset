import os
import pandas as pd


__author__ = 'Josef Doundoulakis'
__maintainer__ = 'Josef Doundoulakis'
__email__ = 'doundoulakis.iosif@outlook.com'


class Dataset:

    def __init__(self, filename):

        self.name = filename
        self.format = filename[filename.index('.', -7):]
        self.path = os.path.join(os.getcwd(), 'data', self.name)

        if self.format == '.csv':

            if 'GHCN_avg' in self.name:

                self.df = pd.read_csv(self.path, header=None)

            elif '.POP.' in self.name:

                self.df = pd.read_csv('data\API_SP.POP.TOTL_DS2_en_csv_v2_1217749.csv', header=2)

            else:

                self.df = pd.read_csv(self.path)

        elif self.format == '.xlsx':

            self.df = pd.read_excel(self.path, sheet_name='Database')

    def preprocess(self):

        """ Current method cleans source data and organizes them into dictionaries with countries as keys """

        if 'acaps' in self.name:

            self.df.LOG_TYPE = self.df.LOG_TYPE.map({'Introduction / extension of measures' : 1,
                                                    'Phase-out measure' : -1})
            self.df = self.df[['COUNTRY', 'DATE_IMPLEMENTED', 'MEASURE', 'NON_COMPLIANCE', 'LOG_TYPE', 'COMMENTS']]
            self.df.rename(columns={'COUNTRY' : 'country',
                                    'DATE_IMPLEMENTED' : 'date',
                                    'MEASURE' : 'measures',
                                    'NON_COMPLIANCE' : 'non_compliance',
                                    'LOG_TYPE' : 'log_type'}, inplace=True)
            self.df.country = self.df.country.apply(lambda x: x.capitalize())\
                                             .apply(lambda x: 'Us' if x == 'United states of america'
                                                    else 'Russia' if x == 'Russian federation' else 'Moldova'
                                                    if x == 'Moldova republic of' else 'China' if 'China' in x
                                                    else 'North macedonia' if 'macedonia' in x else 'Korea, south'
                                                    if 'Korea republic' in x else x)
            self.df.measures = self.df.measures.apply(lambda x: x.capitalize().strip())
            self.df['date'] = self.df['date'].apply(lambda x: x.strip() if type(x) == str else x)
            self.df['date'] = pd.to_datetime(self.df['date'], errors='raise')
            self.df.dropna(subset=['date'], inplace=True)
            self.df.set_index('country', inplace=True)
            self.df = self.df[['measures', 'date', 'log_type', ]].sort_values('date')
            unique_measures = self.df.measures.unique()

            measures = {country : self.df.loc[country].set_index('date') for country in self.df.index.unique()}

            for country in measures.keys():
                # measures[country] = measures[country].groupby('measures').log_type.sum()
                for measure in unique_measures:

                    measures[country][measure] = measures[country].measures.apply(lambda x: int(measure == x))
                    measures[country][measure] = measures[country][measure] * measures[country].log_type

                measures[country].drop(columns=['measures', 'log_type'], inplace=True)
                measures[country] = measures[country].groupby('date').sum()
                measures[country] = measures[country].resample('D').sum()
                measures[country] = measures[country].cumsum(axis=0, skipna=True)
                measures[country] = (measures[country] - measures[country].min(axis=0)) / \
                                    (measures[country].max(axis=0) - measures[country].min(axis=0))
                measures[country].fillna(0, inplace=True)

            return measures

        elif 'time_series' in self.name:

            self.df.rename(columns={'Country/Region' : 'country'}, inplace=True)
            self.df['country'] = self.df['country'].apply(lambda x: x.capitalize())\
                                                   .apply(lambda x: 'Czech republic' if
                                                          'Czech' in x else 'Congo' if
                                                          'brazzaville' in x else 'Congo dr'
                                                          if 'kinshasa' in x else "Côte d'ivoire"
                                                          if 'Cote' in x else x)
            self.df = self.df.drop(columns=['Province/State', 'Lat', 'Long'], inplace=False)
            self.df.set_index('country', inplace=True)
            self.df = self.df.groupby('country').sum()

            if 'confirmed' in self.name:

                confirmed_cases = {i : row for i, row in self.df.iterrows() if row[-1] > 500}

                for country, df in confirmed_cases.items():
                    df.index = pd.to_datetime(df.index, errors='raise')
                    confirmed_cases[country] = confirmed_cases[country][confirmed_cases[country] > 0]

                return confirmed_cases

            elif 'recovered' in self.name:

                recoveries = {i : row for i, row in self.df.iterrows()}

                for country, df in recoveries.items():
                    df.index = pd.to_datetime(df.index, errors='raise')
                    recoveries[country].sort_index(inplace=True)

                return recoveries

            elif 'deaths' in self.name:

                deaths = {i : row for i, row in self.df.iterrows()}

                for country, df in deaths.items():
                    df.index = pd.to_datetime(df.index, errors='raise')
                    deaths[country].sort_index(inplace=True)
                    # deaths[country] = deaths[country][deaths[country] > 0]

                return deaths

        elif 'GHCN_avg' in self.name:

            with open('data/GHCN_country_codes.txt', 'r') as f:
                lines = f.readlines()
                country_codes = {line[:2]: line[2:-1].strip() for line in lines}
                f.close()

            self.df[0] = self.df[0].apply(lambda x: x[:2]).map(country_codes).apply(lambda x: x.capitalize())
            self.df[0] = self.df[0].apply(lambda x: 'Us' if 'United states' in x else 'Czech republic' if
                                                    'Czech' in x else 'Congo' if
                                                    'brazzaville' in x else 'Congo dr'
                                                    if 'kinshasa' in x else "Côte d'ivoire"
                                                    if 'Cote' in x else 'North macedonia'
                                                    if 'Macedonia' in x else 'Bahamas'
                                                    if 'Bahamas' in x else x)
            self.df[1] = self.df[1].apply(str).apply(lambda x: "{}-{}-{}".format(x[:4], x[4:6], x[6:]))
            self.df[1] = pd.to_datetime(self.df[1], errors='raise')
            self.df = self.df[[0, 1, 3]].rename(columns={0 : 'country', 1 : 'date', 3 : 'avg_temp'})
            self.df.set_index('country', inplace=True)

            temperatures = {country : self.df.loc[country] for country in self.df.index.unique()}

            for country in temperatures.keys():

                temperatures[country] = temperatures[country].groupby('date').avg_temp.mean()
                temperatures[country] = temperatures[country].resample('D').mean().interpolate('linear')\
                                                             .apply(int)

            return temperatures

        elif 'BUILT_UP' in self.name:

            self.df = self.df[(self.df['MEAS'] == 'SQKM') & (self.df.Year == 2014)]
            self.df = self.df[['Country', 'Value']].rename(columns={'Value' : 'Built_up_sqkm'})
            self.df['Country'] = self.df['Country'].apply(lambda x: x.capitalize())\
                                                   .apply(lambda x: 'China' if 'China' in x or 'china' in x
                                                          else 'Korea, south' if 'Korea' in x else 'Congo dr'
                                                          if 'Democratic republic of the congo' in x else 'Us'
                                                          if x == 'United states' else 'Slovakia'
                                                          if 'Slovak' in x else x)
            self.df.set_index('Country', inplace=True)

            built_up = {i : row.values[0] for i, row in self.df.iterrows()}

            return built_up

        elif '.POP.' in self.name:

            self.df = self.df[['Country Name', '2019']]
            self.df['Country Name'] = self.df['Country Name'].apply(lambda x: x.capitalize())\
                                                             .apply(lambda x: 'Us' if x == 'United states'
                                                                    else 'Congo dr' if x == 'Congo, dem. rep.'
                                                                    else 'Congo' if x == 'Congo, rep.' else 'Russia'
                                                                    if 'Russian' in x else "Côte d'ivoire"
                                                                    if 'Cote' in x else 'Korea, south'
                                                                    if x == 'Korea, rep.' else 'China' if 'China' in x
                                                                    or 'china' in x else 'Iran' if 'Iran' in x else
                                                                    'Kyrgyzstan' if 'Kyrgyz' in x else 'Egypt'
                                                                    if 'Egypt' in x else 'Venezuela' if 'Venezuela'
                                                                    in x else 'Yemen' if 'Yemen' in x else
                                                                    'Dominican republic' if x == 'Dominica' else
                                                                    'Slovakia' if 'Slovak' in x else x)
            self.df.set_index('Country Name', inplace=True)

            population = {i : row.values[0] for i, row in self.df.iterrows()}

            return population


def sync(temperatures, measures, confirmed_cases, deaths,
         built_up, population, recoveries):

    countries_intersection = set(measures.keys()).intersection(confirmed_cases.keys(), recoveries.keys(),
                                                               deaths.keys(), temperatures.keys(),
                                                               built_up.keys(), population.keys())

    countries_union = set(measures.keys()).union(confirmed_cases.keys(), recoveries.keys(),
                                                 deaths.keys(), temperatures.keys(),
                                                 built_up.keys(), population.keys())

    for country in countries_union - countries_intersection:

        deaths.pop(country) if country in deaths.keys() else ...
        measures.pop(country) if country in measures.keys() else ...
        recoveries.pop(country) if country in recoveries.keys() else ...
        temperatures.pop(country) if country in temperatures.keys() else ...
        confirmed_cases.pop(country) if country in confirmed_cases.keys() else ...
        population.pop(country) if country in population.keys() else ...
        built_up.pop(country) if country in built_up.keys() else ...

    for country in measures.keys():
        measures[country] = measures[country][(measures[country].index > confirmed_cases[country].index[0]) &
                                              (measures[country].index < confirmed_cases[country].index[-1])]
        assert country in confirmed_cases.keys(), country
        assert country in temperatures.keys(), country
        assert country in population.keys(), country
        assert country in built_up.keys(), country
