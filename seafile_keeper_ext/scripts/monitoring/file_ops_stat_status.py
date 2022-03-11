# -*- coding: utf-8 -*-

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")

from django.db import connection

"""Get FileOpsStat status, and thus libevents correct propogation"""

"""
If there are no entries in the `FileOpsStat` since 1 HOUR then most probably libevents propagatio does not work
**NOTE:** timestamp in `FileOpsStat` saved in other timezone (from NOW() - 2 HOURS), thus add 2 HOURS. 1 HOUR is added to set time span to be in.
"""

RC = 0

cur = connection.cursor()

# should be increased by KEEPER growth, check `FileOpsStat` table
HOURS = 5

cur.execute(f"SELECT MAX(timestamp) + INTERVAL {HOURS} HOUR < NOW() FROM `FileOpsStat`")
rows = cur.fetchall()

# for row in rows:
    # print(row)

if rows[0] == 1:
    print("No new FileOpsStat entries since {HOURS} hours. WARNING: libevents propagation probably does not work anymore.")
    RC = 2

sys.exit(RC)

