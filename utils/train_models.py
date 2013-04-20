from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import explained_variance_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import SGDRegressor, Ridge
from sklearn.cross_validation import KFold
from scipy.sparse import *
import numpy as np
import cPickle

# Load Feature Matrix
feature_matrix = cPickle.load(open('2013-04-20 183207/features.dat', 'r'))
# Load Target Data
print "Converting to CSR Matrix to make life easier..."
feature_matrix = feature_matrix.tocsr()

for target in ['crop_damages', 'property_damages', 'direct_deaths', 'indirect_deaths', 'direct_injuries',
               'indirect_injuries']:
    avg_train_score = 0
    avg_test_score = 0

    target_data_file = "targets_%s.dat" % target
    print "Starting to train a model to predict %s..." % target.replace('_', ' ')
    target_matrix = cPickle.load(open('2013-04-20 183207/' + target_data_file, 'r'))
    print "Converting targets to CSR Matrix to make life easier..."
    target_matrix = np.array(target_matrix)

    kf = KFold(len(target_matrix), n_folds=3, indices=True, shuffle=True)
    for train_index, test_index in kf:
        print "Beginning Fold"
        kfold_train = feature_matrix[train_index]
        kfold_test = feature_matrix[test_index]
        kfold_train_target = target_matrix[train_index]
        kfold_test_target = target_matrix[test_index]
        #clf = SGDRegressor(n_iter=1000, shuffle=True)
        clf = Ridge()
        clf.fit(kfold_train, kfold_train_target)

        score_train = clf.score(kfold_train, kfold_train_target)
        score_test = clf.score(kfold_test, kfold_test_target)

        print "R^2 Score On Training Data:", score_train
        avg_train_score += score_train
        print "R^2 Score On Validation Data:", score_test
        avg_test_score += score_test
    avg_train_score = avg_train_score/3.0
    avg_test_score = avg_test_score/3.0
    print "Average Score on Training Data:", avg_train_score
    print "Average Score on Testing Data:", avg_test_score