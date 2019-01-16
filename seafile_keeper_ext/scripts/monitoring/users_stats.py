# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")
import django
django.setup()

from seaserv import ccnet_api
from keeper.utils import email_in_mpg_domain_list


def get_user_stats():
    """get KEEPER user stats
    """
    try:
        users = ccnet_api.get_emailusers('DB', -1, -1) + \
        ccnet_api.get_emailusers('LDAPImport', -1, -1)
    except Exception as e:
        print ('Error: {}'.format(e))
        return

    users_activated = [u for u in users if u.is_active]
    mpg_users_activated = [u for u in users_activated if email_in_mpg_domain_list(u.email)]
    external_users_activated = [u for u in users_activated if not email_in_mpg_domain_list(u.email)]


    print("KEEPER users \n --total: {}\n --activated: {}\n   --MPG activated: {}\n   --external activated: {}".
          format(len(users), len(users_activated), len(mpg_users_activated), len(external_users_activated)))


if __name__ == "__main__":
    get_user_stats()

