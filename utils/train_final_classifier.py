from sklearn.linear_model import SGDClassifier
import numpy as np
import cPickle
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("model")
args = parser.parse_args()

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

target = args.model
avg_train_score = 0
avg_test_score = 0

target_data_file = "targets_%s.dat" % target
logger.info("Starting to train a model to predict %s..." % target.replace('_', ' '))
target_matrix = cPickle.load(open('2013-04-20 183207/' + target_data_file, 'r'))
target_matrix = [1 if i > 0 else 0 for i in target_matrix]
target_matrix = np.array(target_matrix)

sgdc = SGDClassifier(shuffle=True, n_jobs=-1, n_iter=300, loss='hinge', penalty='l2', verbose=3)
sgdc.fit(feature_matrix, target_matrix)

with open('final_classifier_' + target + '.dat', 'wb') as outfile:
    cPickle.dump(sgdc, outfile, cPickle.HIGHEST_PROTOCOL)
with open('final_classifier_' + target + '_coef.dat', 'wb') as outfile:
    cPickle.dump(sgdc, outfile, cPickle.HIGHEST_PROTOCOL)