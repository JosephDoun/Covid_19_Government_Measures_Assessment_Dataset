# Covid-19_Measure_Assessment_Dataset
### Compiling a dataset suitable for modeling the impact of government policies on the spread of covid-19


**_This is a work in progress and it is expected to be updated, including possible complete approach reconsiderations._** 

**_<ins>Contributions, suggestions and reviews are strongly encouraged</ins>._**


#### __<ins>Data sources:</ins>__

  * [1. Acaps measure implementation dataset](https://www.acaps.org/covid19-government-measures-dataset)

  * [2. CSSE-JHU Time-series](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series)

  * [3. GHCN daily climate data](https://www.climate.gov/maps-data/dataset/daily-temperature-and-precipitation-reports-data-tables)
    - Menne, M.J., I. Durre, R.S. Vose, B.E. Gleason, and T.G. Houston, 2012:  An overview 
of the Global Historical Climatology Network-Daily Database.  Journal of Atmospheric 
and Oceanic Technology, 29, 897-910, doi:10.1175/JTECH-D-11-00103.1.

  * [4. World Bank population data](https://data.worldbank.org/indicator/sp.pop.totl)

  * [5. OECD Built-up area cover data](https://stats.oecd.org/Index.aspx?DataSetCode=BUILT_UP)


#### __<ins>Pre-processing & Methodology:</ins>__

  1. Each dataset is preprocessed and cleaned with regards to country names, such as to be able to efficiently use the column "Country" as a join base.
  2. CSSE JHU Timeseries are filtered to only include countries with a minimum of 500 confirmed cases. Organized in series per country.
     - The confirmed cases dataset are transformed to logarithmic scale, which is then transformed to daily percent change. The daily percent changes are then used for the compilation of the final dataset. The particular unit of measure was chosen as a representative of disease spread and because of its non relation to the number of confirmed cases, which would render measurements comparable between different countries.
     - The recorded values are corrected for noise, via a centered 7-day moving average.
     - Example for Afghanistan:
     ![Y Smoothing](https://github.com/JosefDoun/Covid_19_Government_Measures_Assessment_Dataset/blob/master/images/Noise_removal.png?raw=true)
     
  3. GHCN climate data are used to extract and organize per country average temperature, per day. Organized in series per country.
  4. ACAPS Measures are filtered to exclude implemented measures prior to the appearance of cases (depending on country). Organized in series per country.
     - Each measure is one hot coded throughout 35 columns, with a positive or negative sign depending whether it is an introduction or a fade-out measure.
     - In order to establish the strength of implementation for each measure in place at a moment in time, the values are cumulatively summed into a continuous timeseries, which is then normalized into a [0,1] interval. Meaning, 1 corresponds to the measure being fully active, while any related fadeout measures are substracted gradually. This point system implies that if any number of fadeout measures were implemented after its final introduction, the measure would end up being inactive. Which does not represent reality in many of the cases. However, this approach manages to quantify withdrawl stages on some degree. The final product would describe what measures are active at a moment in time and at what 'degree' in relation to the maximum (1).
     - A more ideal approach would be to manually evaluate each measure implementation of the ACAPS dataset based on the 'Comments' field.
  5. Population and Built-up area datasets are integrated as they are and as an index (population density).
  6. Individual derived sets are combined together in a unified dataset which can be found under /training_data.


#### __<ins>Results Analysis:</ins>__

  1. An LGBMRegressor was fitted to the dataset, with a 5-fold cross validated mean RMSE of approximately 0.09% (0.00093). Between separate parameter tryouts, the ones that produced a more conservative model were chosen.
  2. Predictions were produced using different scenarios for a time period not longer than what is documented.
     - All measures deactivated.
     - All measures activated: Intensity 0.1
     - All measures activated: Intensity 1.0
     - One prediction for each measure being solely activated.
     - The rest of the variables with the exception of 'day_zero' were kept constant at mean values.
     
     ![Results](https://github.com/JosefDoun/Covid_19_Government_Measures_Assessment_Dataset/blob/master/images/Results_1.png?raw=true)
     
|      Measures                                           | Spread % decrease in 182 days   |  RMSE | Feature importance (splits)  |No. of non-zero values (dataset)|
|  :---                                                   | :---:                           | :---: |              :---:           |   :--: |
|Economic measures                                                        | -48.0% | +- 2.6%      |                   4280         |                    14783|
|Strengthening the public health system                                 |   -28.5% | +- 2.6%              |           5103         |                    14236|
|Partial lockdown                                                         | -28.5% | +- 2.6%                 |        4728             |                11061|
|Schools closure                                                          | -15.7% | +- 2.6%                |         2910             |                14119|
|International flights suspension                                         |  -7.5% | +- 2.6%               |          2140             |                14006|
|Limit public gatherings                                                  |  -7.2% | +- 2.6%               |          4610             |                15681|
|Other public health measures enforced                                    |  -6.5%  |+- 2.6%              |           2678              |                9195|
|Isolation and quarantine policies                                        |  -5.7% | +- 2.6%              |           2488              |               15128|
|Emergency administrative structures activated or established                       |  -5.4% | +- 2.6%              |           3088             |                11469|
|Closure of businesses and public services                                |  -4.7% | +- 2.6%              |           3992            |                 13085|
|Visa restrictions                                                        |  -3.3% | +- 2.6%              |           2257            |                 11587|
|Requirement to wear protective gear in public                           |   -3.1% | +- 2.6%              |           2929            |                  9058|
|Curfews                                                                 |   -2.5% | +- 2.6%               |          2255            |                  7824|
|Awareness campaigns                                                     |   -2.0% | +- 2.6%             |            1903            |                 10406|
|General recommendations                                                  |  -1.9% | +- 2.6%             |            1437            |                 10973|
|Health screenings in airports and border crossings                       |  -1.3% | +- 2.6%             |            1784           |                  10267|
|State of emergency declared                                              |  -1.3% | +- 2.6%             |            2369           |                   9976|
|Testing policy                                                          |   -0.8% | +- 2.6%             |            1771             |                 8326|
|Border checks                                                           |  -0.6%  |+- 2.6%            |              861           |                   5020|
|Changes in prison-related policies                                       |  -0.5% | +- 2.6%            |              799            |                  5423|
|Domestic travel restrictions                                            |   -0.5% | +- 2.6%            |             2891            |                 12185|
|Border closure                                                          |   -0.4% | +- 2.6%            |             2743              |               14063|
|Additional health/documents requirements upon arrival                      |   -0.2% | +- 2.6%            |              521             |                 4072|
|Surveillance and monitoring                                             |   -0.2% | +- 2.6%            |             2955             |                 9418|
|Psychological assistance and medical social work                        |   -0.1% | +- 2.6%            |             2085           |                   5013|
|Military deployment                                                     |   -0.1% | +- 2.6%            |              270             |                 5099|
|Amendments to funeral and burial regulations                            |    0.0% | +- 2.6%             |             391            |                  2860|
|Mass population testing                                                |    0.0% | +- 2.6%            |              279             |                 2753|
|Checkpoints within the country                                          |    0.0% | +- 2.6%            |              367             |                 2735|
|Lockdown of refugee/idp camps or other minorities                       |   -0.0% | +- 2.6%             |              10            |                  1083|
|Complete border closure                                                 |    0.0% | +- 2.6%             |               0             |                  132|
|Humanitarian exemptions                                                 |    0.0% | +- 2.6%             |               0             |                  494|
|Full lockdown                                                           |    0.1% | +- 2.6%             |             347              |                2624|
|Limit product imports/exports                                           |    0.2% | +- 2.6%              |            251               |               2813|

Author: Iosif Doundoulakis

E-mail: doundoulakis.iosif@outlook.com


Dependencies:

- Pandas / Numpy / Scipy / Matplotlib / xlrd
- LightGBM
- Python version 3.7.1


