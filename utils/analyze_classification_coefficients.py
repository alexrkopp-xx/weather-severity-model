from sklearn.linear_model import SGDClassifier
import numpy as np
import cPickle

# Load feature names
feature_names = []
for i in range(1, 5):
    fn = cPickle.load(open('2013-04-20 183207/feature_names_' + str(i) + '.dat', 'r'))
    feature_names.extend(fn)


for model in ['property_damages', 'direct_deaths', 'indirect_deaths', 'direct_injuries', 'indirect_injuries',
              'crop_damages']:
    print "Model:", model
    classifier = cPickle.load(open('../final_classifier_' + model + '.dat', 'r'))
    top_positions = np.argsort(abs(classifier.coef_), axis=1)[0, -50:]
    vals = classifier.coef_[0, top_positions]


    #print top_positions
    for idx,i in enumerate(top_positions):
        print 50 - idx, ",", feature_names[i], ",", vals[idx]
    #print vals
    #break
    print ""
