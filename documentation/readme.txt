severity_prediction.py - Not finished. The idea was to have this predict new severities once good models are found. There isn't much to do in this file until good models are trained.

test/test_cap_parser.py - Tests if NWSCAPParser library will work with the data provided to us by Google (it does)

utils/fips.py - Never actually used, but it converts states/counties to and from FIPS

utils/schema.sql - Base Schema for MySQL Database (NEED TO UPDATE)

1. utils/FixAndCombineStormReports.py - The NOAA Storm Events Database CSV files are malformed (Quotes are not escaped).It appears that the malformed text is only in the episode_narrative and event_narrative fields.Since we don't need these fields, the easiest solution is just to remove them. This script will 
also consolidate each of the CSVs into one large file

2. utils/GenerateCAPDatabase.py - Parses CAP and Storm Events and places into MySQL database

3. utils/feature_extraction.py - Runs matching algorithm and extracts features. Writes features, vectorizers, and target values to files. (They are pickled)

4. utils/train_classifiers.py - Runs a grid search of different parameters on each severity indicator (uses Stochastic Gradient Descent Classifier). The idea was to figure out which parameters work best

5. utils/train_final_classifier.py [model name] - Trains a classifier for the severity indicator passed in via command line. The idea was to rebuild the classifier using the ideal parameters for each severity indicator.

6. utils/train_regression.py - Same as utils/train_classifiers.py, but uses Stochastic Gradient Descent Regressor on the nonzero examples.

utils/analyze_classification_coefficients.py - Lists top 50 features found in each classification model
utils/category_counter.py - Was used to generate list of storm event types
utils/match_alerts.py - Was used to tweak matching algorithm.
utils/storm_event_types.py - Ignore, not used.
utils/train_models.py - Our first attempt at building the models (fitting a regression using all the data). We also tried a RidgeRegressor.
utils/train_grid_svr.py - Grid Search Support Vector Regressor.. Took too long
