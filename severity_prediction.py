import argparse
from nwscapparser import NWSCAPParser
import cPickle

# Configuration
vectorizer_part_1 = 'utils/2013-04-20 183207/vectorizer_part_1.dat'
vectorizer_part_2 = 'utils/2013-04-20 183207/vectorizer_part_2.dat'
vectorizer_part_3 = 'utils/2013-04-20 183207/vectorizer_part_3.dat'
vectorizer_part_4 = 'utils/2013-04-20 183207/vectorizer_part_4.dat'
duration_scale = 'utils/2013-04-20 183207/duration_scale.dat'

parser = argparse.ArgumentParser()
parser.add_argument("cap_report", help="CAP report of storm", type=str)
parser.add_argument("-d", "--debug", help="Show debug information", action="store_true")
args = parser.parse_args()

f = None
try:
    f = open(args.cap_report, 'r')
except IOError:  # If file doesn't exist
    print 'Error opening', args.cap_report
    exit(1)

# Parse CAP
src = f.read()
alert = NWSCAPParser(src)
if alert.status != "Actual":
    print "Can't process CAP. Report status has to be 'Actual'"
    exit(1)

try:

    effective = alert.info.effective[:-6]
    effective_offset = alert.info.effective[-6:]
except:
    effective = 0
    effective_offset = 0

identifier = alert.identifier
sent = alert.sent[:-6]
sent_offset = alert.sent[-6:]
msgType = alert.msgType
category = alert.info.category
event = alert.info.event
responseType = alert.info.responseType
urgency = alert.info.urgency
severity = alert.info.severity
certainty = alert.info.certainty

try:
    onset = alert.info.onset[:-6]
    onset_offset = alert.info.onset[-6:]
except:
    onset = 0
    onset_offset = 0

try:
    expires = alert.info.expires[:-6]
    expires_offset = alert.info.expires[-6:]
except:
    expires = 0
    onset_offset = 0

begin_time = None
if onset != 0:
    begin_time = onset
elif effective != 0:
    begin_time = effective
else:
    begin_time = sent

headline = alert.info.headline
description = alert.info.description
instruction = alert.info.instruction
lstfips = []
for i in alert.info.area.geocode:
    if i['valueName'] == "FIPS6":
        try:
            lstfips = int(i['value'])
        except ValueError:
            pass

for fips in lstfips:  # For every county/state that the cap report covers
    # Extract Features
    pass
    # Run through models
    # Run predicted values through the classifer
    # Output severity