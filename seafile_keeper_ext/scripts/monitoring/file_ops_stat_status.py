# -*- coding: utf-8 -*-

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")

from django.db import connection

"""Get FileOpsStat last update status, and thus try to indicate libevents correct propagation"""

"""
If there are no entries in the `FileOpsStat` since x `HOURS` then most probably libevents propagation does not work.
**NOTE:** `HOURS`>1 because aggragation task takes some time and one HOUR is added to set time span to be in.
"""

RC = 0

cur = connection.cursor()

# should be increased by KEEPER growth, check `FileOpsStat` table
HOURS = 4

cur.execute(f"SELECT MAX(timestamp) + INTERVAL {HOURS} HOUR < NOW() FROM `FileOpsStat`")
rows = cur.fetchall()

# for row in rows:
    # print(row)

# print(rows[0][0])

if rows[0][0] != 0:
    print(f"No new FileOpsStat entries since {HOURS} hour(s). WARNING: libevents propagation probably does not work anymore.")
    RC = 2

sys.exit(RC)

