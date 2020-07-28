from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lightgbm import LGBMRegressor
pd.options.display.max_columns = 50
pd.options.display.width = 1000

training_data = pd.read_csv('../training_data/covid19_measure_assessment_dataset.csv')


X = training_data[training_data.columns[0:-1]]
y = training_data[training_data.columns[-1]]

X.drop(columns=['Obligatory medical tests not related to covid-19'], inplace=True)

print(y.describe(), X.day_zero.describe())

X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=True, random_state=0, test_size=0.2)


max_depth = -1
num_leaves = 150
learning_rate = 0.01
boosting_type, subsample, subsample_freq = 'rf', 0.8, 2
class_weight = None
objective = 'rmse'
colsample_bytree = 0.8
colsample_bynode = 0.8
min_child_samples = 180
max_bin = 256

Regressor = LGBMRegressor(n_estimators=100000, boosting_type=boosting_type, learning_rate=learning_rate, random_state=0,
                          subsample=subsample, subsample_freq=subsample_freq, colsample_bytree=colsample_bytree,
                          colsample_bynode=colsample_bynode, min_child_samples=min_child_samples,
                          max_depth=max_depth, num_leaves=num_leaves, class_weight=class_weight, max_bin=max_bin,
                          importance_type='split', objective=objective)
Regressor.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_test, y_test)],
              early_stopping_rounds=1000, )

best_iteration = Regressor.best_iteration_

print(Regressor.get_params())


Regressor = LGBMRegressor(n_estimators=best_iteration, boosting_type=boosting_type, learning_rate=learning_rate,
                          random_state=0, class_weight=class_weight, min_child_samples=min_child_samples,
                          colsample_bynode=colsample_bynode, colsample_bytree=colsample_bytree,
                          subsample=subsample, subsample_freq=subsample_freq, max_bin=max_bin,
                          max_depth=max_depth, num_leaves=num_leaves, top_k=1000, tree_learner='voting',
                          importance_type='split', objective=objective)


scores = cross_val_score(Regressor, X, y, cv=5,
                         scoring='neg_mean_squared_error')
print('Cross Validation Results: {} +- Std.Dev. {} '.format(scores.mean(), scores.std()))


Regressor.fit(X, y)

print("Iterations used: ", Regressor.n_estimators)

for c, i in zip(X.columns, Regressor.feature_importances_):
    print(c, i)


fig, ax = plt.subplots(1, 1, figsize=(10, 5), facecolor=(0.9, 0.9, 0.9))
ax.set_title('Model predictions per solely activated measure')
ax.set_facecolor((0.8, 0.8, 0.8))
ax.set_xlabel('Days since day zero')
ax.set_ylabel('Exponent % increase since day zero')


days = X.day_zero.max()
period = np.arange(X.day_zero.min(), days, 1)


def prediction(measure_intensity=0, days=days, temp=X.avg_temp.mean(), population=X.population.mean(),
               built=X.built_area.mean(), density=X.pop_density.mean(), measure_index=None, clf=Regressor, train_data=X):

    days = np.arange(X.day_zero.min(), days, 1)
    array = np.zeros((days.size, train_data.columns.size), 'float64')
    array[:, 0], array[:, 1], array[:, 2], array[:, 3], array[:, 4] = days, temp, population, built, density

    if measure_index:

        array[:, 4+measure_index] = 1

    else:

        array[:, 5:] = measure_intensity

    array = pd.DataFrame(array, columns=X.columns)
    predictions = clf.predict(array, num_iteration=best_iteration, pred_contrib=False)
    predictions = predictions.cumsum()

    return predictions


intensity_0, intensity_0_1, intensity_1 = prediction(0), prediction(0.1), prediction(1)

measure_assessment = [prediction(days, measure_index=i) for i in range(1, 35)]


ax.plot(period, intensity_0, c=(0.1, 0.1, 0.1), lw=6, alpha=0.9, label='All measures: Intensity 0')
ax.plot(period, intensity_0_1, c=(0.3, 0.3, 0.3), lw=6, alpha=0.9, label='All measures: Intensity 0.1')
ax.plot(period, intensity_1, c=(0.5, 0.5, 0.5), lw=6, alpha=0.9, label='All measures: Intensity 1')

for name, measure in zip(X.columns[5:], measure_assessment):
    rc = np.random.random(3,)
    ax.plot(period, measure, c=rc, ls='--', lw=2, label=name)
    ax.fill_between(period, measure-scores.mean()*(period-period[0]+1), measure+scores.mean()*(period-period[0]+1),
                    color=(*rc, 0.2))


ax.set_xlim(left=0, right=days)
ax.set_ylim(bottom=0, top=intensity_0.max())
ax.yaxis.set_ticklabels(['{}%'.format(int(x*100)) for x in ax.get_yticks()], rotation=90)
ax.grid(axis='both', linestyle=':', color=(1, 1, 1, 0.3))

ax.legend(bbox_to_anchor=(1, 1.01), fontsize=7.5, labelspacing=0.6, fancybox=True, title='Legend')
plt.subplots_adjust(wspace=0, hspace=0, right=0.7, left=0.05)


Regressor.booster_.save_model('Model/covid19_measure_assessment_model.txt', num_iteration=best_iteration)


results = pd.DataFrame(((round(((measure[-1] - intensity_0[-1]) / intensity_0[-1])*100, 1))
                       for measure in measure_assessment),
                       index=X.columns[5:],
                       columns=['Spread % decrease in {} days'.format(int(days))])

results['RMSE'] = '+- {}%'.format(abs(round((days*scores.mean()/intensity_0[-1])*100, 1)))

results.sort_values('Spread % decrease in {} days'.format(int(days)), inplace=True)
results[results.columns[0]] = results[results.columns[0]].apply(lambda x: '{}%'.format(x))

print(results)

plt.show()
