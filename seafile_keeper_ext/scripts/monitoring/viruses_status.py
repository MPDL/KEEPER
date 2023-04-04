# -*- coding: utf-8 -*-

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")

from django.db import connection

"""Get non handled viruses"""

RC = 0

cur = connection.cursor()

cur.execute("SELECT * FROM `VirusFile` WHERE has_deleted=0 AND has_ignored=0")
rows = cur.fetchall()


if len(rows)>0:
    # found not hadlen viruses
    print("There are non handled viruses:")
    for row in rows:
        print(row)
    RC = 2

sys.exit(RC)

