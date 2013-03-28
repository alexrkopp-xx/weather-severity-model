import csv
from collections import defaultdict
import operator
cap_to_se = defaultdict(lambda: defaultdict(lambda:0))
se_to_cap = defaultdict(lambda: defaultdict(lambda:0))

with open('matched.csv','r') as csvreader:
    reader = csv.reader(csvreader)
    for r in reader:
        cap_category = r[5]
        se_category = r[21]
        cap_to_se[cap_category][se_category] += 1
        se_to_cap[se_category][cap_category] += 1

print "CAP -> Storm Events"
for key,setValues in cap_to_se.iteritems():
    print "\t",key
    sortedv = sorted(setValues.iteritems(), key=operator.itemgetter(1), reverse=True)
    for key,value in sortedv:
        print "\t\t",key,"-",value

print "Storm Events -> CAP"
for key,setValues in se_to_cap.iteritems():
    print "\t",key
    sortedv = sorted(setValues.iteritems(), key=operator.itemgetter(1), reverse=True)
    for key,value in sortedv:
        print "\t\t",key,"-",value