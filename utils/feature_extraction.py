import logging
import MySQLdb as mdb
import MySQLdb.cursors
from scipy.sparse import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import StandardScaler
import nltk
import re
import cPickle as pickle
from config import *
import datetime
import os

timenow = datetime.datetime.now()
outputdir = "%02d-%02d-%02d %02d%02d%02d" % (timenow.year, timenow.month, timenow.day, timenow.hour, timenow.minute,
                                             timenow.second)
os.path.mkdir(outputdir)
stemmer = nltk.stem.PorterStemmer()


def stemming_tokenizer(text):
    return [stemmer.stem(w).replace(".", "") for w in nltk.word_tokenize(text.lower())
            if re.match(r"\w", w)]

logging.basicConfig(format='%(asctime)s;%(levelname)s:%(message)s', level=logging.DEBUG)

con = mdb.connect(mysql_host, mysql_user, mysql_pass, mysql_db, cursorclass=MySQLdb.cursors.DictCursor)

lstFeatures = []  # A list of dictionaries that will be passed to the Dictionary Vectorizer. The other lists require
                  # additional work (NLP).
lstDescriptions = []
lstHeadlines = []
lstInstructions = []

# The values we are trying to predict
lstTargetPropertyDamages = []
lstTargetCropDamages = []
lstTargetDirectInjuries = []
lstTargetIndirectInjuries = []
lstTargetIndirectDeaths = []
lstTargetDirectDeaths = []

with con:
    cur = con.cursor()
    cur.execute('SELECT * FROM `weather-severity`.cap c JOIN `weather-severity`.cap_fips capfips ON capfips.cap = c.id '
                'JOIN `weather-severity`.storm_events se ON se.fips = capfips.fips '
                'JOIN `weather-severity`.valid_events ve '
                'WHERE (ve.cap_type = c.event) AND (ve.se_type = se.event_type) AND (ve.valid = 1) AND '
                '((c.begin_time >= se.begin_time AND c.expires <= se.end_time) '
                'OR ( ABS(TIMESTAMPDIFF(MINUTE,c.begin_time,se.begin_time)) <= 0.25 * '
                'TIMESTAMPDIFF(MINUTE,se.end_time,se.begin_time) AND '
                'ABS(TIMESTAMPDIFF(MINUTE,c.expires,se.end_time)) <= 0.25 * '
                'TIMESTAMPDIFF(MINUTE,se.end_time,se.begin_time)) OR '
                '(se.begin_time >= c.begin_time AND se.end_time <= c.expires) OR '
                '( ABS(TIMESTAMPDIFF(MINUTE,c.begin_time,se.begin_time)) <= 0.25 * '
                'TIMESTAMPDIFF(MINUTE,c.expires,c.begin_time) AND '
                'ABS(TIMESTAMPDIFF(MINUTE,c.expires,se.end_time)) <= 0.25 * '
                'TIMESTAMPDIFF(MINUTE,c.expires,c.begin_time)))')

    field_names = [i[0] for i in cur.description]
    #print field_names
    for row in cur:
        print row.keys()
        lstTargetPropertyDamages.append(row['property_damage'])
        lstTargetCropDamages.append(row['crop_damage'])
        lstTargetDirectInjuries.append(row['injuries_direct'])
        lstTargetIndirectInjuries.append(row['injuries_indirect'])
        lstTargetDirectDeaths.append(row['deaths_direct'])
        lstTargetIndirectDeaths.append(row['deaths_indirect'])

        lstDescriptions.append(row['description'])
        lstHeadlines.append(row['headline'])
        lstInstructions.append(row['instruction'])

        features_1 = dict()
        features_1['duration'] = (row['expires']-row['begin_time']).seconds
        features_1['event'] = row['event']
        #features_1['responseType'] = row['responseType'] None of the CAP reports have a response type.. Removing
        features_1['urgency'] = row['urgency']
        features_1['severity'] = row['severity']
        features_1['certainty'] = row['certainty']

        features_1['fips'] = str(row['fips'])  # Convert FIPS to string so we get dummy variables
        lstFeatures.append(features_1)

    # Part 1
    #print lstFeatures
    fvec = DictVectorizer()

    arrFeatures = fvec.fit_transform(lstFeatures)  # Important to keep in sparse matrix
    print "(Part 1) Writing Feature Names to feature_names_1.dat"

    with open(outputdir + '/feature_names_1.dat', 'wb') as outfile:
        pickle.dump(fvec.get_feature_names(), outfile, pickle.HIGHEST_PROTOCOL)

    print "Scaling Duration..."
    print "Converting COO Sparse Matrix (arrFeatures) to LIL Sparse Matrix"
    # Note: This may not be the most efficient way to scale
    lil_feature_matrix = arrFeatures.tolil()
    durationScaler = StandardScaler(with_mean=False)
    tmpArr = durationScaler.fit_transform(lil_feature_matrix[:, 4])
    lil_feature_matrix[:, 4] = tmpArr
    arrFeatures = lil_feature_matrix.tocsr()
    print "Finished Scaling Duration... Writing scale parameters to file"
    with open(outputdir + '/duration_scale.dat', 'wb') as outfile:
        pickle.dump(durationScaler, outfile, pickle.HIGHEST_PROTOCOL)

    # Going to be used for the next few parts
    headlineTextVectorizer = TfidfVectorizer(charset_error='replace', tokenizer=stemming_tokenizer, analyzer='word',
                                             ngram_range=(1, 2), stop_words=stopword_list, lowercase=True,
                                             max_features=None, norm='l2', use_idf=True, smooth_idf=True)
    descriptionTextVectorizer = TfidfVectorizer(charset_error='replace', tokenizer=stemming_tokenizer, analyzer='word',
                                                ngram_range=(1, 2), stop_words=stopword_list, lowercase=True,
                                                max_features=None, norm='l2', use_idf=True, smooth_idf=True)
    instructionTextVectorizer = TfidfVectorizer(charset_error='replace', tokenizer=stemming_tokenizer, analyzer='word',
                                                ngram_range=(1, 2), stop_words=stopword_list, lowercase=True,
                                                max_features=None, norm='l2', use_idf=True, smooth_idf=True)

    # Part 2 (Headlines)
    headlineFeatures = headlineTextVectorizer.fit_transform(lstHeadlines)
    print headlineFeatures.shape
    print "(Part 2) Writing Feature Names to feature_names_2.dat"

    with open(outputdir + '/feature_names_2.dat', 'wb') as outfile:
        pickle.dump(headlineTextVectorizer.get_feature_names(), outfile, pickle.HIGHEST_PROTOCOL)

    # Part 3 (Descriptions)
    descriptionFeatures = descriptionTextVectorizer.fit_transform(lstDescriptions)
    print descriptionFeatures.shape
    print "(Part 3) Writing Feature Names to feature_names_3.dat"

    with open(outputdir + '/feature_names_3.dat', 'wb') as outfile:
        pickle.dump(descriptionTextVectorizer.get_feature_names(), outfile, pickle.HIGHEST_PROTOCOL)

    # Part 4 (Instructions)
    instructionFeatures = instructionTextVectorizer.fit_transform(lstInstructions)
    print instructionFeatures.shape
    print "(Part 4) Writing Feature Names to feature_names_4.dat"

    with open(outputdir + '/feature_names_4.dat', 'wb') as outfile:
        pickle.dump(instructionTextVectorizer.get_feature_names(), outfile, pickle.HIGHEST_PROTOCOL)

    # Combine the parts
    features = hstack([arrFeatures, headlineFeatures])
    features = hstack([features, descriptionFeatures])
    features = hstack([features, instructionFeatures])

    print features.shape

    print "Writing Part 1 Vectorizer to vectorizer_part_1.dat"
    with open(outputdir + '/vectorizer_part_1.dat', 'wb') as outfile:
        pickle.dump(fvec, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Part 2 Vectorizer to vectorizer_part_2.dat"
    with open(outputdir + '/vectorizer_part_2.dat', 'wb') as outfile:
        pickle.dump(headlineTextVectorizer, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Part 3 Vectorizer to vectorizer_part_3.dat"
    with open(outputdir + '/vectorizer_part_3.dat', 'wb') as outfile:
        pickle.dump(descriptionTextVectorizer, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Part 4 Vectorizer to vectorizer_part_4.dat"
    with open(outputdir + '/vectorizer_part_4.dat', 'wb') as outfile:
        pickle.dump(instructionTextVectorizer, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Feature Matrix to features.dat"
    with open(outputdir + '/features.dat', 'wb') as outfile:
        pickle.dump(features, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Target Direct Deaths"
    with open(outputdir + '/targets_direct_deaths.dat', 'wb') as outfile:
        pickle.dump(lstTargetDirectDeaths, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Target Direct Injuries"
    with open(outputdir + '/targets_direct_injuries.dat', 'wb') as outfile:
        pickle.dump(lstTargetDirectInjuries, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Target Property Damages"
    with open(outputdir + '/targets_property_damages.dat', 'wb') as outfile:
        pickle.dump(lstTargetPropertyDamages, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Target Indirect Deaths"
    with open(outputdir + '/targets_indirect_deaths.dat', 'wb') as outfile:
        pickle.dump(lstTargetIndirectDeaths, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Target Indirect Injuries"
    with open(outputdir + '/targets_indirect_injuries.dat', 'wb') as outfile:
        pickle.dump(lstTargetIndirectInjuries, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Target Crop Damages"
    with open(outputdir + '/targets_crop_damages.dat', 'wb') as outfile:
        pickle.dump(lstTargetCropDamages, outfile, pickle.HIGHEST_PROTOCOL)
