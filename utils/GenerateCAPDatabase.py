from datetime import timedelta
from dateutil.parser import parse
import logging
import os
from nwscapparser import NWSCAPParser
import sys
import csv
import MySQLdb as mdb
import warnings
from subprocess import Popen, PIPE
from config import *
import re

"""
    Goal: Read CAP Reports and store in MySQL database
"""

logging.basicConfig(format='%(asctime)s;%(levelname)s:%(message)s', level=logging.DEBUG)

schema_file = 'schema.sql'
tz = re.compile(r'[^\d-]+')

def monetary_damage_convert(m):
    multipliers = { 'K': 1000, 'M': 1000000, 'B': 1000000000, 'T': 1000000000000}
    try:
        return float(m[:-1]) * multipliers[m[-1]]
    except (TypeError, ValueError, KeyError):
        return 0.0


def storm_event_parser(d):
    try:
        offset = int(d.split('-')[1])
    except IndexError:
        if d.split()[-1] == "GST10":
            offset = 10
        else:
            raise IndexError
    utc_date = (parse(" ".join(d.split()[:-1])) + timedelta(hours=offset)).replace(tzinfo=None)
    return utc_date


warnings.filterwarnings('error', category=mdb.Warning)

logging.info("Importing Database Structure...")
if mysql_pass == '':
    process = Popen('mysql -u%s -h%s' % (mysql_user, mysql_host),
                    stdout=PIPE, stdin=PIPE, shell=True)
else:
    process = Popen('mysql -u%s -p%s -h%s' % (mysql_user, mysql_pass, mysql_host),
                    stdout=PIPE, stdin=PIPE, shell=True)

process.communicate('source ' + schema_file)[0]

con = mdb.connect(mysql_host, mysql_user, mysql_pass, mysql_db)
with con:
    cur = con.cursor()
    logging.info("Reading and Generating Database of Storm Events...")
    with open(storm_events_path) as csvfile:
        count = 0
        insert_query = """INSERT INTO `storm_events` (event_type, fips, begin_time, end_time, injuries_direct,
                                injuries_indirect, deaths_direct, deaths_indirect, property_damage, crop_damage) VALUES (%s, %s,
                                CONVERT_TZ(STR_TO_DATE(%s,'%%m/%%d/%%Y %%H:%%i:%%s'),%s,'+00:00'),
                                CONVERT_TZ(STR_TO_DATE(%s,'%%m/%%d/%%Y %%H:%%i:%%s'),%s,'+00:00'),%s, %s, %s, %s, %s, %s)"""
        sereader = csv.reader(csvfile, delimiter=',', )
        sereader.next(); # Skip Column Headers
        records = []
        print "Processed Storm Events:"
        for row in sereader:
            fips = int(row[5] + row[10].zfill(3))
            event_type = row[8]
            offset = tz.sub('', row[14]) + ":00"
            if offset[0] != '-':
                offset = "+" + offset
            begin_time = row[13]
            end_time = row[15]
            injuries_direct = row[16]
            injuries_indirect = row[17]
            deaths_direct = row[18]
            deaths_indirect = row[19]
            property_damage = monetary_damage_convert(row[20])
            crop_damage = monetary_damage_convert(row[21])
            records.append((event_type, fips, begin_time, offset, end_time, offset, injuries_direct, injuries_indirect, deaths_direct, deaths_indirect, property_damage, crop_damage))
            if len(records) >= 10000:
                try:
                    cur.executemany(insert_query,records)
                    con.commit()
                    records = []
                    count += 10000
                    sys.stdout.write(str(count) + "...");
                except mdb.Error:
                    print "Error in Query:"
                    print cur._last_executed
                    exit(0)
        try: # Commit the last set of records
            cur.executemany(insert_query,records)
            con.commit()
            count += len(records)
            print str(count) + "... Finished!"
            records = []
        except mdb.Error:
            print "Error in Query:"
            print cur._last_executed
            exit(0)

    logging.info("Reading and Generating Database of CAP Reports...")
    records = []
    fips_records = []
    listing = [file for file in os.listdir(cap_path) if file.lower().endswith(".xml")]
    insert_query = """INSERT INTO `cap` (`identifier`, `sent`, `msgType`, `category`, `event`, `responseType`,
            `urgency`,`severity`,`certainty`,`effective`,`onset`,`expires`,`headline`,`description`,`instruction`)
            VALUES (%s,CONVERT_TZ(STR_TO_DATE(%s,'%%Y-%%m-%%dT%%H:%%i:%%s'),%s,'+00:00'),%s,%s,%s,%s,%s,%s,%s,
            CONVERT_TZ(STR_TO_DATE(%s,'%%Y-%%m-%%dT%%H:%%i:%%s'),%s,'+00:00'),
            CONVERT_TZ(STR_TO_DATE(%s,'%%Y-%%m-%%dT%%H:%%i:%%s'),%s,'+00:00'),
            CONVERT_TZ(STR_TO_DATE(%s,'%%Y-%%m-%%dT%%H:%%i:%%s'),%s,'+00:00'), %s,%s,%s)"""
    insert_fips_query = """INSERT INTO `cap_fips` (`fips`,`cap`) VALUES (%s, %s)"""
    count = 0
    for idx, i in enumerate(listing):
        with open(cap_path + i,'r') as f:
            src = f.read()
            alert = NWSCAPParser(src)
            if alert.status != "Actual":
                continue

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

            headline = alert.info.headline
            description = alert.info.description
            instruction = alert.info.instruction
            #lstfips = [int(i['value']) for i in alert.info.area.geocode if i['valueName'] == "FIPS6"]
            records.append((identifier, sent, sent_offset, msgType, category, event, responseType, urgency, severity, certainty, effective, effective_offset, onset, onset_offset, expires, expires_offset, headline, description, instruction))
            for i in alert.info.area.geocode:
                if i['valueName'] == "FIPS6":
                    try:
                        tmpfips = int(i['value'])
                        fips_records.append((tmpfips,idx+1))
                    except ValueError:
                        pass

        if len(records) >= 1000:
            try:
                cur.executemany(insert_query,records)
                con.commit()
                cur.executemany(insert_fips_query,fips_records)
                records = []
                con.commit()
                fips_records = []
                count += 1000
                sys.stdout.write(str(count) + "...");
            except mdb.Error:
                print "Error in Query:"
                print cur._last_executed
                exit(0)
    try: # Commit the last set of records
        cur.executemany(insert_query,records)
        con.commit()
        cur.executemany(insert_fips_query,fips_records)
        con.commit()
        count += len(records)
        print str(count) + "... Finished!"
        records = []
        fips_records = []
    except mdb.Error:
        print "Error in Query:"
        print cur._last_executed
        exit(0)
