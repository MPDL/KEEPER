#!/usr/bin/python3

import os
import re
import sys
import datetime
from operator import length_hint
from seafevents.db import init_db_session_class
import configparser

'''
Variables:
'''
RC = 0
conf = configparser.ConfigParser()
conf.read(os.path.join(os.environ['SEAFILE_CENTRAL_CONF_DIR'], 'seafile.conf'))
session = init_db_session_class(conf, db = 'seafile')()
today = datetime.date.today()
last_month = today.replace(day=1) - datetime.timedelta(days=1)
check_list = ['Failed to connect to MySQL',
              'Failed to stat block',
              'Failed to open file',
              'Failed to execute sql',
              'Head branch update',
              'Failed to update origin repo',
              'Fast forward merge for repo',
              'Failed to decompress',
              'Empty input', 'STOP']
'''
Log analysis:
'''
with open("/opt/seafile/logs/seafile.log", "r") as seafile_log:
    lines = seafile_log.readlines()
    errors = 0
    current = ''
    list_of_errors = []
    special_characters = ['(', ')', ',']

    for i in check_list:
        if errors > 0 and i != current:
            print('WARNING:', errors, current, 'last:', date_of_error)
            print('List of errors:')
            for j in list_of_errors:
                if current == check_list[1]:
                    repo_id = re.search(
                        '[0-9a-f]{8}[:-][0-9a-f]{4}[:-][0-9a-f]{4}[:-][0-9a-f]{4}[:-][0-9a-f]{12}', j).group()
                    # execute owner
                    result = session.execute("SELECT owner_id FROM RepoOwner WHERE repo_id LIKE '%s'" % repo_id)
                    for row in result:
                        repo_owner = "".join(filter(lambda char: char not in special_characters, str(row)))
                        print("repository:", repo_id, ", owner:", repo_owner)
                else:
                    print(j)
            list_of_errors.clear()
            errors = 0
        for line in lines:
            if line.startswith(last_month.strftime("%Y-%m")) or line.startswith(today.strftime("%Y-%m")):
                if i in line:
                    date_of_error = line[:19]
                    text_of_error = line[20:]
                    if length_hint(list_of_errors) == 0:
                        current = i
                    if text_of_error not in list_of_errors:
                        list_of_errors.append(text_of_error)
                        errors += 1
                        RC = 1
not list_of_errors and print("OK")
sys.exit(RC)
