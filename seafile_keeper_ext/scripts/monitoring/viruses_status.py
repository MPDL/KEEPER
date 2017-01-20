# -*- coding: utf-8 -*-

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")

from seahub.settings import DATABASES

import MySQLdb


def get_db(db_name):
    """Get DB connection"""
    return MySQLdb.connect(host=DATABASES['default']['HOST'],
         user=DATABASES['default']['USER'],
         passwd=DATABASES['default']['PASSWORD'],
         db=db_name,
         charset='utf8')



"""Get non handled viruses"""

RC = 0

db = get_db('seahub-db')
cur = db.cursor(MySQLdb.cursors.DictCursor)

cur.execute("SELECT * FROM `VirusFile` WHERE `has_handle`=1")
rows = cur.fetchall()


if len(rows)>0:
    # found not hadlen viruses
    print "WARNING: There are non handled viruses:"
    for row in rows:
        print row
    RC = 1

sys.exit(RC)

