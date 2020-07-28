import numpy as np
import pandas as pd


__author__ = 'Josef Doundoulakis'
__maintainer__ = 'Josef Doundoulakis'
__email__ = 'doundoulakis.iosif@outlook.com'


def dataset_compiler(measures, confirmed, deaths,
                     temperatures, population,
                     built_up):

    country_parts = {}
    exponents = {country : np.log(confirmed[country]) for country in confirmed.keys()}
    dataset = np.array([['day_zero', 'avg_temp', 'population', 'built_area', 'pop_density',
                         *measures['Greece'].columns, '%exp_increase']])

    for i, country in enumerate(exponents.keys()):

        built = built_up[country]
        pop = population[country]
        pop_density = pop / built
        exponents[country] = exponents[country].pct_change()
        exponents[country][exponents[country] < 0] = 0
        exponents[country].replace({np.inf : np.nan}, inplace=True)
        exponents[country].fillna(0, inplace=True)
        exponents[country] = exponents[country].rolling(7, center=True).mean()

        country_parts[country] = pd.concat([measures[country], exponents[country], temperatures[country]],
                                           axis=1)
        country_parts[country].ffill(inplace=True)
        country_parts[country].rename(columns={country : '%exp_increase'}, inplace=True)
        country_parts[country].dropna(subset=['%exp_increase'], inplace=True)
        country_parts[country]['pop_density'] = pop_density
        country_parts[country]['population'] = pop
        country_parts[country]['built_area'] = built
        country_parts[country].fillna(0, inplace=True)
        country_parts[country]['day_zero'] = (country_parts[country].index - country_parts[country].index[0]).days

        i += 1
        print('\rCompiling final dataset: {} %'.format(round((i/len(exponents.keys()))*100, 1)),
              end='', flush=True)

        country_parts[country] = pd.concat([country_parts[country]['day_zero'],
                                            country_parts[country]['avg_temp'],
                                            country_parts[country]['population'],
                                            country_parts[country]['built_area'],
                                            country_parts[country]['pop_density'],               # Re-order
                                            country_parts[country][measures[country].columns],
                                            country_parts[country]['%exp_increase']], axis=1)

        dataset = np.concatenate([dataset, country_parts[country].values])

    dataset = pd.DataFrame(dataset[1:, ...], columns=dataset[0, ...])

    return country_parts, dataset
