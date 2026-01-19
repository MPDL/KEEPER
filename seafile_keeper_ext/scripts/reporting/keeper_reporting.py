#!/usr/bin/env python3

import os
import sys
import json
import requests
import argparse
import pprint
from pathlib import Path
from datetime import datetime

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")
django.setup()
from seahub.profile.models import Profile
from seaserv import ccnet_threaded_rpc

DOMAINS_URL = 'https://rena.mpdl.mpg.de/iplists/keeperx.json'


pp = pprint.PrettyPrinter(indent=2)
parser = argparse.ArgumentParser()

def p_header(txt):
    t = "##### " + txt + " #####"
    c = "".ljust(len(t), '#')
    print(c)
    print(t)
    print(c)


def load_json_from_url(url):
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print(f"Cannot load {url}: status_code {r.status_code}")
        return None
    return json.loads(r.content)


def load_rena_domains():
    # return load_json_from_file('keeperx.json')
    return load_json_from_url(DOMAINS_URL)

def get_rena_domains_dict_set(domains_json):
    domains_dict = {}
    domains_set = set()
    if domains_json:
        dts = domains_json.get('details')
        for dt in dts:
            for v in dt.values():
                dmns = v.get('domains')
                if dmns:
                    domains_dict[v.get('inst_name_de')] = dmns
                    for d in dmns:
                        domains_set.add(d)
    return domains_dict, domains_set


def do(args):
    """
    Main doer method
    """

    if not [a for a in args.__dict__.keys() if getattr(args, a) and a != 'func']:
        print("At least one parameter should be defined:")
        parser.print_help()
        return -1

    all = args.all

    # generate domains_dict and domains_set
    domains = load_rena_domains()
    if domains is None:
        return -1

    domains_dict, domains_set = get_rena_domains_dict_set(domains)

    p_header(f"Reporting timestamp: {datetime.now()}")

    # get consolidated email list from KEEPER 
    status = 'active'
    users = ccnet_threaded_rpc.get_emailusers('DB', -1, -1, status)
    print(f"Number of {status} users: {len(users)}")
   
    emails = []
    for u in users:
        email = str(u.email)
        if email.endswith("@auth.local"):
            p = Profile.objects.get_profile_by_user(email)
            if hasattr(p, 'contact_email'):
                emails.append(p.contact_email)
        else:
            emails.append(u.email)
        
    # generate domains_dict
    domains_count = {}
    if domains:
        for k in domains_dict.keys():
            d_list = domains_dict.get(k)
            for e in emails:
                if e[e.index('@')+1:] in d_list:
                    if k not in domains_count:
                        domains_count[k] = 1
                    else:
                        domains_count[k] += 1

    # for key, value in sorted(domains_count.items(), key=lambda item: item[1], reverse=True):
        # print(f"{key}: {value}")

    more_than_50 = [domains_count[key] for key in domains_count.keys() if  domains_count[key] > 50]
    print(f"Number of Institutes with more than 50 {status} users: {len(more_than_50)}")

    more_than_100 = [domains_count[key] for key in domains_count.keys() if  domains_count[key] > 100]
    print(f"Number of Institutes with more than 100 {status} users: {len(more_than_100)}")



parser.add_argument('--users-per-mpg-aff', action='store_true', help='Members per MPG Affiliation')
parser.add_argument('--mpg-affs', action='store_true', help='Number of MPG Affiliations on board')

parser.add_argument('-a', '--all', action='store_true', help='Show all')
parser.set_defaults(func=do)
args = parser.parse_args()

exit(args.func(args))
