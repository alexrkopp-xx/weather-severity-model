import csv
import re
import MySQLdb as mdb

mysql_host = 'localhost'
mysql_user = 'root'
mysql_pass = ''
mysql_db = 'weather-severity'

con = mdb.connect(mysql_host, mysql_user, mysql_pass, mysql_db)
cur = con.cursor()

with open('/home/koppa/Downloads/tmp.csv','r') as csvreader:
    reader = csv.reader(csvreader)
    for r in reader:
        if r[0] == "" or r[1] == "":
            continue
        x = re.match("(.*)\s-\d*",r[1])

        valid = 0
        if r[2] != "-1":
            valid = 1

        insert_query = """INSERT INTO `valid_events` (`cap_type`,`se_type`,`valid`) VALUES (%s, %s, %s)"""
        cur.execute(insert_query, (x.groups()[0],r[0],valid))