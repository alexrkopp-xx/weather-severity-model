"""
    The NOAA Storm Events Database CSV files are malformed (Quotes are not escaped)

    It appears that the malformed text is only in the episode_narrative and event_narrative fields.
    Since we don't need these fields, the easiest solution is just to remove them.

    This script will also consolidate each of the CSVs into one large file

    Author: Alex Kopp
"""

import csv
import glob
import os

# I think the "update" event details files are included in the main event details files
# as such, only the event_details_YYYYMM.csv should be used
file_format = "event_details_??????.csv"
file_location = "../StormEvents/original"
output_file = "../StormEvents/StormEventData.csv" # Output for new CSV

expected_headers = [
    'last_date_modified',
    'last_date_certified',
    'episode_id',
    'event_id',
    'state',
    'state_fips',
    'year',
    'month_name',
    'event_type',
    'cz_type',
    'cz_fips',
    'cz_name',
    'wfo',
    'begin_date_time',
    'cz_timezone',
    'end_date_time',
    'injuries_direct',
    'injuries_indirect',
    'deaths_direct',
    'deaths_indirect',
    'damage_property',
    'damage_crops',
    'source',
    'magnitude',
    'magnitude_type',
    'flood_cause',
    'category',
    'tor_f_scale',
    'tor_length',
    'tor_width',
    'tor_other_wfo',
    'tor_other_cz_state',
    'tor_other_cz_fips',
    'tor_other_cz_name',
    'episode_title',
    'episode_narrative',
    'event_narrative'
]

remove_column = 34 # Removing 'episode_title' and everything afterwards

with open(output_file,'wb') as out:
    storm_writer = csv.writer(out)
    storm_writer.writerow(expected_headers[:remove_column])

    os.chdir(file_location)
    files = sorted(glob.glob(file_format)) # Sort them so we can read in chronological order

    for f in files:
        with open(f, 'rb') as csvfile:
            print "Reading",f
            storm_reader = csv.reader(csvfile)
            headers = storm_reader.next()
            for i,eh in enumerate(expected_headers):
                if eh != headers[i]:
                    print "Error in headers: (Expected:",eh,") (Found:",headers[i],")"
                    print "Exiting..."
                    exit(1)
            for row in storm_reader:
                storm_writer.writerow(row[:remove_column])

print "Finished!"
