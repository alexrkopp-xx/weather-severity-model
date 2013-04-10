import logging
import MySQLdb as mdb
import MySQLdb.cursors
from scipy.sparse import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import DictVectorizer
import nltk
import re
import cPickle as pickle
import numpy as np

stemmer = nltk.stem.PorterStemmer()
def stemming_tokenizer(text):
    return [stemmer.stem(w).replace(".", "") for w in nltk.word_tokenize(text.lower())
            if re.match(r"\w", w)]

# Modified from default english list in scikit-learn
stopword_list = frozenset(
    ['all', 'less', 'being', 'indeed', 'over', 'anyway', 'not', 'own', 'through', 'yourselves', 'fify', 'where', 'mill',
     'only', 'find', 'before', 'whose', 'system', 'how', 'somewhere', 'with', 'show', 'had', 'enough', 'should', 'to',
     'whom', 'seeming', 'ours', 'has', 'might', 'thereafter',
     'latterly', 'do', 'them', 'his', 'around', 'than', 'get', 'very', 'de', 'none', 'cannot', 'every', 'whether',
     'they', 'front', 'during', 'thus', 'now', 'him', 'nor', 'name', 'several', 'hereafter', 'always', 'who', 'cry',
     'whither', 'this', 'someone', 'either', 'each', 'become', 'thereupon', 'sometime', 'side', 'therein',
     'because', 'often', 'our', 'eg', 'some', 'back', 'up', 'go', 'namely', 'towards', 'are',
     'further', 'beyond', 'ourselves', 'yet', 'out', 'even', 'will', 'what', 'still', 'for', 'bottom', 'mine', 'since',
     'please', 'per', 'its', 'everything', 'behind', 'un', 'above', 'between', 'it', 'neither', 'seemed',
     'ever', 'across', 'she', 'somehow', 'be', 'we', 'full', 'never', 'however', 'here', 'otherwise', 'were',
     'whereupon', 'nowhere', 'although', 'found', 'alone', 're', 'along', 'by', 'both', 'about', 'last',
     'would', 'anything', 'via', 'many', 'could', 'thence', 'put', 'against', 'keep', 'etc', 'amount', 'became', 'ltd',
     'hence', 'onto', 'or', 'con', 'among', 'already', 'co', 'afterwards', 'formerly', 'within', 'seems', 'into',
     'others', 'while', 'whatever', 'except', 'down', 'hers', 'everyone', 'done', 'least', 'another', 'whoever',
     'moreover', 'couldnt', 'throughout', 'anyhow', 'yourself', 'from', 'her', 'few', 'together', 'top',
     'there', 'due', 'been', 'next', 'anyone', 'much', 'call', 'therefore', 'interest', 'then', 'thru',
     'themselves', 'was', 'sincere', 'empty', 'more', 'himself', 'elsewhere', 'mostly', 'on', 'am',
     'becoming', 'hereby', 'amongst', 'else', 'part', 'everywhere', 'too', 'herself', 'former', 'those', 'he', 'me',
     'myself', 'made', 'these', 'bill', 'cant', 'us', 'until', 'besides', 'nevertheless', 'below', 'anywhere',
     'can', 'of', 'your', 'toward', 'my', 'something', 'and', 'whereafter', 'whenever', 'give', 'almost',
     'wherever', 'is', 'describe', 'beforehand', 'herein', 'an', 'as', 'itself', 'at', 'have', 'in', 'seem', 'whence',
     'ie', 'any', 'fill', 'again', 'hasnt', 'inc', 'thereby', 'thin', 'no', 'perhaps', 'latter', 'meanwhile', 'when',
     'detail', 'same', 'wherein', 'beside', 'also', 'that', 'other', 'take', 'which', 'becomes', 'you', 'if', 'nobody',
     'see', 'though', 'may', 'after', 'upon', 'most', 'hereupon', 'but', 'nothing', 'such', 'why',
     'a', 'off', 'whereby', 'i', 'whole', 'noone', 'sometimes', 'well', 'amoungst', 'yours', 'their', 'rather',
     'without', 'so', 'the', 'whereas', 'once'])



logging.basicConfig(format='%(asctime)s;%(levelname)s:%(message)s', level=logging.DEBUG)
mysql_host = 'localhost'
mysql_user = 'root'
mysql_pass = ''
mysql_db = 'weather-severity'

con = mdb.connect(mysql_host, mysql_user, mysql_pass, mysql_db, cursorclass=MySQLdb.cursors.DictCursor)

lstFeatures = [] # A list of dictionaries that will be passed to the Dictionary Vectorizer. The other lists require
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
                'WHERE (ve.cap_type = c.event) AND (ve.se_type = se.event_type) AND (ve.valid = 1) AND ((c.begin_time >= se.begin_time AND c.expires <= se.end_time) '
                'OR ( ABS(TIMESTAMPDIFF(MINUTE,c.begin_time,se.begin_time)) <= 0.25 * TIMESTAMPDIFF(MINUTE,se.end_time,se.begin_time) '
                'AND ABS(TIMESTAMPDIFF(MINUTE,c.expires,se.end_time)) <= 0.25 * TIMESTAMPDIFF(MINUTE,se.end_time,se.begin_time)) '
                'OR (se.begin_time >= c.begin_time AND se.end_time <= c.expires) '
                'OR ( ABS(TIMESTAMPDIFF(MINUTE,c.begin_time,se.begin_time)) <= 0.25 * TIMESTAMPDIFF(MINUTE,c.expires,c.begin_time) '
                'AND ABS(TIMESTAMPDIFF(MINUTE,c.expires,se.end_time)) <= 0.25 * TIMESTAMPDIFF(MINUTE,c.expires,c.begin_time))) LIMIT 10'
    )

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
        features_1['responseType'] = row['responseType']
        features_1['urgency'] = row['urgency']
        features_1['severity'] = row['severity']
        features_1['certainty'] = row['certainty']

        features_1['fips'] = str(row['fips']) # Convert FIPS to string so we get dummy variables
        lstFeatures.append(features_1)

    # Part 1
    print lstFeatures
    fvec = DictVectorizer()
    arrFeatures = fvec.fit_transform(lstFeatures) # Important to keep in sparse matrix
    print "(Part 1) Writing Feature Names to feature_names_1.dat"

    with open('feature_names_1.dat', 'wb') as outfile:
        pickle.dump(fvec.get_feature_names(), outfile, pickle.HIGHEST_PROTOCOL)

    # Going to be used for the next few parts
    freeTextVectorizer = TfidfVectorizer(charset_error='replace', tokenizer=stemming_tokenizer, analyzer='word', ngram_range=(1,2), stop_words=stopword_list, lowercase=True, max_features=None, norm='l2', use_idf=True, smooth_idf=True)

    # Part 2 (Headlines)
    headlineFeatures = freeTextVectorizer.fit_transform(lstHeadlines)
    print headlineFeatures.shape
    print "(Part 2) Writing Feature Names to feature_names_2.dat"

    with open('feature_names_2.dat', 'wb') as outfile:
        pickle.dump(freeTextVectorizer.get_feature_names(), outfile, pickle.HIGHEST_PROTOCOL)

    # Part 3 (Descriptions)
    descriptionFeatures = freeTextVectorizer.fit_transform(lstDescriptions)
    print descriptionFeatures.shape
    print "(Part 3) Writing Feature Names to feature_names_3.dat"

    with open('feature_names_3.dat', 'wb') as outfile:
        pickle.dump(freeTextVectorizer.get_feature_names(), outfile, pickle.HIGHEST_PROTOCOL)

    # Part 4 (Instructions)
    instructionFeatures = freeTextVectorizer.fit_transform(lstInstructions)
    print instructionFeatures.shape
    print "(Part 4) Writing Feature Names to feature_names_4.dat"

    with open('feature_names_4.dat', 'wb') as outfile:
        pickle.dump(freeTextVectorizer.get_feature_names(), outfile, pickle.HIGHEST_PROTOCOL)

    # Combine the parts
    features = hstack([arrFeatures,headlineFeatures])
    features = hstack([features,descriptionFeatures])
    features = hstack([features,instructionFeatures])

    print features.shape

    print "Writing Feature Matrix to features.dat"
    with open('features.dat', 'wb') as outfile:
        pickle.dump(features, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Target Direct Deaths"
    with open('targets_direct_deaths.dat', 'wb') as outfile:
        pickle.dump(lstTargetDirectDeaths, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Target Direct Injuries"
    with open('targets_direct_injuries.dat', 'wb') as outfile:
        pickle.dump(lstTargetDirectInjuries, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Target Property Damages"
    with open('targets_property_damages.dat', 'wb') as outfile:
        pickle.dump(lstTargetPropertyDamages, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Target Indirect Deaths"
    with open('targets_indirect_deaths.dat', 'wb') as outfile:
        pickle.dump(lstTargetIndirectDeaths, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Target Indirect Injuries"
    with open('targets_indirect_injuries.dat', 'wb') as outfile:
        pickle.dump(lstTargetIndirectInjuries, outfile, pickle.HIGHEST_PROTOCOL)

    print "Writing Target Crop Damages"
    with open('targets_crop_damages.dat', 'wb') as outfile:
        pickle.dump(lstTargetCropDamages, outfile, pickle.HIGHEST_PROTOCOL)

    #print features.todense()