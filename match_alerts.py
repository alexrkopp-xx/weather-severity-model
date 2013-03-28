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
    cur.execute('SELECT * FROM `weather-severity`.cap c JOIN `weather-severity`.cap_fips capfips ON capfips.cap = c.id \
                 JOIN `weather-severity`.storm_events se ON se.fips = capfips.fips \
                 WHERE ABS(TIMESTAMPDIFF(HOUR,c.begin_time,se.begin_time)) <= 3 \
                 AND ABS(TIMESTAMPDIFF(HOUR,c.expires,se.end_time)) <= 3')
    for row in cur:
        writer.writerow(row)

w.close()