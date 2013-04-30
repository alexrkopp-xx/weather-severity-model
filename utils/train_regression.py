from sklearn.grid_search import GridSearchCV
from sklearn.linear_model import SGDRegressor
from sklearn.cross_validation import KFold
import numpy as np
import cPickle
import logging
import scipy

logger = logging.getLogger('train')

handler = logging.FileHandler('train.log')
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Load Feature Matrix
feature_matrix = cPickle.load(open('2013-04-20 183207/features.dat', 'r'))
# Load Target Data
logger.info("Converting to CSR Matrix to make life easier...")
feature_matrix = feature_matrix.tocsr()
print feature_matrix.shape

parameters = {'loss': ('hinge', 'huber'), 'penalty': ('l2', 'l1', 'elasticnet')}

for target in ['property_damages', 'crop_damages']:

    target_data_file = "targets_%s.dat" % target
    logger.info("Starting to train a model to predict %s..." % target.replace('_', ' '))
    target_matrix = cPickle.load(open('2013-04-20 183207/' + target_data_file, 'r'))

    nonzero_index = []
    for i, v in enumerate(target_matrix):
        if v != 0:
            nonzero_index.append(i)
    #nonzero_index.reverse()
    target_matrix = np.array(target_matrix)

    pruned_feature_matrix = feature_matrix[nonzero_index]
    pruned_target_matrix = target_matrix[nonzero_index]

    kf = KFold(pruned_target_matrix.shape[0], n_folds=3, indices=True, shuffle=True)
    sgdc = SGDRegressor(shuffle=True, n_iter=300, verbose=3)
    gs = GridSearchCV(sgdc, parameters, n_jobs=4, cv=kf, verbose=1, refit=False)
    gs.fit(feature_matrix, target_matrix)

    logger.info(gs.grid_scores_)
    logger.info(gs.best_score_)
    logger.info(gs.best_params_)