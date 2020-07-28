import numpy as np
import pandas as pd
from Plotter import plotter
import os
import csv
from Dataset import Dataset, sync
from Compiler import dataset_compiler
import Data_retrieval
pd.options.display.max_columns = 100
pd.options.display.max_rows = 500


__author__ = 'Josef Doundoulakis'
__maintainer__ = 'Josef Doundoulakis'
__email__ = 'doundoulakis.iosif@outlook.com'


data_dir = os.path.join(os.getcwd(), 'data')
files = [Dataset(x) for x in os.listdir(data_dir) if x.endswith('.csv') or x.endswith('.xlsx')]


temperatures = [x.preprocess() for x in files if 'GHCN_avg' in x.name][0]
measures = [x.preprocess() for x in files if 'acaps' in x.name][0]
confirmed_cases = [x.preprocess() for x in files if 'confirmed' in x.name][0]
deaths = [x.preprocess() for x in files if 'deaths' in x.name][0]
recoveries = [x.preprocess() for x in files if 'recovered' in x.name][0]
built_up = [x.preprocess() for x in files if 'BUILT_UP' in x.name][0]
population = [x.preprocess() for x in files if '.POP.' in x.name][0]


sync(temperatures=temperatures, measures=measures,
     confirmed_cases=confirmed_cases, deaths=deaths,                                    # Pop non mutual countries
     built_up=built_up, population=population, recoveries=recoveries)


country_parts, dataset = dataset_compiler(measures=measures, temperatures=temperatures,
                                          confirmed=confirmed_cases, deaths=deaths,          # Execute segmentation and
                                          population=population, built_up=built_up)          # data compilation


# random_country = tuple(measures.keys())[np.random.randint(0, len(measures.keys()))]
# plotter(random_country, confirmed_cases=confirmed_cases,                            # Plot random choice
#         deaths=deaths, segments=segments, measures=measures)


with open('training_data/covid19_measure_assessment_dataset.csv', 'w', newline='') as f:

    writer = csv.writer(f)
    writer.writerow(dataset.columns)                                                # Write on disk
    writer.writerows(dataset.values)
