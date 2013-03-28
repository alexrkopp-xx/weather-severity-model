# Testing if NWS-CAP-parser will work with Google's data

from pprint import pprint
import os
from dateutil.parser import *
from datetime import *
import pytz

from nwscapparser import NWSCAPParser


def test_basic_fields(alert):
    print '---- basic fields ----'
    print alert.identifier
    print alert.info.effective
    print '%d FIPS6 codes:'%len(alert.FIPS6), alert.FIPS6
    print '%d UGC codes:'%len(alert.UGC), alert.UGC
    print '%d INFO_PARAMS:'%len(alert.INFO_PARAMS), alert.INFO_PARAMS


def test_dict_dump(alert):
    print '---- dict dump ----'
    pprint(alert.as_dict())


def test_json_dump(alert):
    print '---- json dump ----'
    pprint(alert.as_json())


path = '../noaa-cap-xml/'
listing = os.listdir(path)
earliest_date = datetime.now(pytz.utc)
for i in listing:
    #print idx
    with open(path + i,'r') as f:
        src = f.read()
    alert = NWSCAPParser(src)
    #test_basic_fields(alert)
    #test_dict_dump(alert)
    date = parse(alert.info.effective)
    #if date.year < 2012 or (date.year == 2012 and date.month < 6):
    #    test_json_dump(alert)
    #    break
    if date < earliest_date:
        print "New Earliest Date:", date
        earliest_date = date

#        with open(fn,'r') as f:
#            src = f.read()
#    alert = NWSCAPParser(src)
#    print alert
#    test_basic_fields(alert)
#    test_dict_dump(alert)
#    test_json_dump(alert)

