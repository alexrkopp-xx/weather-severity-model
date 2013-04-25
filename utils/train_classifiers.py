from sklearn.grid_search import GridSearchCV
from sklearn.linear_model import SGDClassifier
from sklearn.cross_validation import KFold
import numpy as np
import cPickle
import logging

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

for target in ['property_damages', 'direct_deaths', 'indirect_deaths', 'direct_injuries',
               'indirect_injuries', 'crop_damages']:
    avg_train_score = 0
    avg_test_score = 0

    target_data_file = "targets_%s.dat" % target
    logger.info("Starting to train a model to predict %s..." % target.replace('_', ' '))
    target_matrix = cPickle.load(open('2013-04-20 183207/' + target_data_file, 'r'))
    target_matrix = [1 if i > 0 else 0 for i in target_matrix]
    target_matrix = np.array(target_matrix)

    kf = KFold(len(target_matrix), n_folds=3, indices=True, shuffle=True)
    sgdc = SGDClassifier(shuffle=True, n_jobs=-1, n_iter=300, verbose=3)
    gs = GridSearchCV(sgdc, parameters, n_jobs=-1, cv=kf, verbose=1, refit=False)
    gs.fit(feature_matrix, target_matrix)

    logger.info(gs.grid_scores_)
    logger.info(gs.best_score_)
    logger.info(gs.best_params_)