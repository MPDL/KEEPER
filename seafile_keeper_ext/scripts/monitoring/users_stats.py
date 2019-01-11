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

    active_users = [u for u in users if u.is_active]
    mpg_active_users = [u for u in active_users if email_in_mpg_domain_list(u.email)]
    external_active_users = [u for u in active_users if not email_in_mpg_domain_list(u.email)]


    print("KEEPER users \n --total: {}\n --active: {}\n --MPG active: {}\n --external active: {}".
          format(len(users), len(active_users), len(mpg_active_users), len(external_active_users)))


if __name__ == "__main__":
    get_user_stats()

