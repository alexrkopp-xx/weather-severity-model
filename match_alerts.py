import logging
import MySQLdb as mdb
import csv

logging.basicConfig(format='%(asctime)s;%(levelname)s:%(message)s', level=logging.DEBUG)
mysql_host = 'localhost'
mysql_user = 'root'
mysql_pass = ''
mysql_db = 'weather-severity'

w = open('matched.csv','w')
writer = csv.writer(w, delimiter=',')

con = mdb.connect(mysql_host, mysql_user, mysql_pass, mysql_db)
with con:
    cur = con.cursor()
    #cur.execute('SELECT * FROM `weather-severity`.cap c JOIN `weather-severity`.cap_fips capfips ON capfips.cap = c.id \
    #             JOIN `weather-severity`.storm_events se ON se.fips = capfips.fips \
    #             WHERE (c.begin_time >= se.begin_time AND c.expires <= se.end_time) \
    #             OR ( ABS(TIMESTAMPDIFF(MINUTE,c.begin_time,se.begin_time)) <= 0.25 * TIMESTAMPDIFF(MINUTE,se.end_time,se.begin_time) \
    #             AND ABS(TIMESTAMPDIFF(MINUTE,c.expires,se.end_time)) <= 0.25 * TIMESTAMPDIFF(MINUTE,se.end_time,se.begin_time))')
    cur.execute('SELECT * FROM `weather-severity`.cap c JOIN `weather-severity`.cap_fips capfips ON capfips.cap = c.id '
                 'JOIN `weather-severity`.storm_events se ON se.fips = capfips.fips '
                 'WHERE (c.begin_time >= se.begin_time AND c.expires <= se.end_time) '
                 'OR ( ABS(TIMESTAMPDIFF(MINUTE,c.begin_time,se.begin_time)) <= 0.25 * TIMESTAMPDIFF(MINUTE,se.end_time,se.begin_time) '
                 'AND ABS(TIMESTAMPDIFF(MINUTE,c.expires,se.end_time)) <= 0.25 * TIMESTAMPDIFF(MINUTE,se.end_time,se.begin_time)) '
                 'OR (se.begin_time >= c.begin_time AND se.end_time <= c.expires) '
                 'OR ( ABS(TIMESTAMPDIFF(MINUTE,c.begin_time,se.begin_time)) <= 0.25 * TIMESTAMPDIFF(MINUTE,c.expires,c.begin_time) '
                 'AND ABS(TIMESTAMPDIFF(MINUTE,c.expires,se.end_time)) <= 0.25 * TIMESTAMPDIFF(MINUTE,c.expires,c.begin_time)) '
    )
    # CAP Fully Contained in Storm Event OR CAP start date is within a margin of 20% of the duration of the storm event

    for row in cur:
        writer.writerow(row)

w.close()