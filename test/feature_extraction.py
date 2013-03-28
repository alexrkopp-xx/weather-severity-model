import logging
import MySQLdb as mdb
import MySQLdb.cursors
from scipy.sparse import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import DictVectorizer
import nltk
import re

stemmer = nltk.stem.PorterStemmer()
def stemming_tokenizer(text):
    return [stemmer.stem(w).replace(".", "") for w in nltk.word_tokenize(text.lower())
            if re.match(r"\w", w)]

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
lstTargetDamage = []
lstTargetInjuries = []
lstTargetDeaths = []

with con:
    cur = con.cursor()
    query = "SELECT c.event, c.begin_time, c.category, c.urgency, c.severity, c.certainty, c.expires," \
            " c.headline, c.description, c.instruction, capfips.fips, se.injuries_direct, se.injuries_indirect," \
            " se.deaths_direct, se.deaths_indirect, se.property_damage, se.crop_damage FROM `weather-severity`.cap" \
            " c JOIN `weather-severity`.cap_fips capfips ON capfips.cap = c.id JOIN `weather-severity`.storm_events se" \
            " ON se.fips = capfips.fips WHERE ABS(TIMESTAMPDIFF(HOUR,c.begin_time,se.begin_time)) <= 3 AND" \
            " ABS(TIMESTAMPDIFF(HOUR,c.expires,se.end_time)) <= 3"

    cur.execute(query)
    field_names = [i[0] for i in cur.description]
    #print field_names
    for row in cur:
        lstTargetDamage.append(row['property_damage'] + row['crop_damage'])
        lstTargetInjuries.append(row['injuries_indirect'] + row['injuries_direct'])
        lstTargetDeaths.append(row['deaths_indirect'] + row['deaths_direct'])

        lstDescriptions.append(row['description'])
        lstHeadlines.append(row['headline'])
        lstInstructions.append(row['instruction'])

        row['duration'] = (row['expires']-row['begin_time']).seconds

        del row['expires']
        del row['begin_time']
        del row['instruction']
        del row['property_damage']
        del row['crop_damage']
        del row['injuries_indirect']
        del row['injuries_direct']
        del row['deaths_indirect']
        del row['deaths_direct']
        del row['description']
        del row['headline']

        row['fips'] = str(row['fips']) # Convert FIPS to string so we get dummy variables
        lstFeatures.append(row)
        # Targets
        #target_damage = property_damage + crop_damage
        #target_injuries = injuries_direct + injuries_indirect
        #target_deaths = deaths_direct + deaths_indirect

        # Extract Features
        # Categ

    # Part 1
    fvec = DictVectorizer()
    arrFeatures = fvec.fit_transform(lstFeatures) # Important to keep in sparse matrix
    print fvec.get_feature_names()

    # Going to be used for the next few parts
    freeTextVectorizer = TfidfVectorizer(charset_error='replace', tokenizer=stemming_tokenizer, analyzer='word', ngram_range=(2,2), stop_words='english', lowercase=True, max_features=None, norm='l2', use_idf=True, smooth_idf=True)

    # Part 2 (Headlines)
    headlineFeatures = freeTextVectorizer.fit_transform(lstHeadlines)
    print headlineFeatures.shape
    #print freeTextVectorizer.get_feature_names()

    # Part 3 (Descriptions)
    descriptionFeatures = freeTextVectorizer.fit_transform(lstDescriptions)
    print descriptionFeatures.shape
    #print freeTextVectorizer.get_feature_names()

    # Part 4 (Instructions)
    instructionFeatures = freeTextVectorizer.fit_transform(lstInstructions)
    print instructionFeatures.shape
    #print freeTextVectorizer.get_feature_names()

    # Combine the parts
    features = hstack([arrFeatures,headlineFeatures])
    features = hstack([features,descriptionFeatures])
    features = hstack([features,instructionFeatures])

    print features.shape
    #print features.todense()