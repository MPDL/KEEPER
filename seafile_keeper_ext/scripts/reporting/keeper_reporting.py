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

domains = None
domains_dict = None

pp = pprint.PrettyPrinter(indent=2)
parser = argparse.ArgumentParser()

def p_header(txt):
    t = "##### " + txt + " #####"
    c = "".ljust(len(t), '#')
    print(c)
    print(t)
    print(c)

def get_help(parser, arg):
    help = parser.__dict__.get('_option_string_actions').get(arg).__dict__.get('help')
    return help


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

def get_users_and_domains_stats(status='active'):

    global domains_dict
    
    users = ccnet_threaded_rpc.get_emailusers('DB', -1, -1, status)
    # print(f"Number of {status} users: {len(users)}")
   
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
    for k in domains_dict.keys():
        d_list = domains_dict.get(k)
        for e in emails:
            if e[e.index('@')+1:] in d_list:
                if k not in domains_count:
                    domains_count[k] = 1
                else:
                    domains_count[k] += 1

    return users, emails, domains_count

def get_usernick_domain_list(users):

    result = []

    for u in users:
        nn = None
        email = str(u.email)
        p = Profile.objects.get_profile_by_user(email)
        if hasattr(p, 'nickname'):
            nn = p.nickname
        if email.endswith("@auth.local"):
            if hasattr(p, 'contact_email'):
                m = p.contact_email
            else:
                m = email
        else:
            m = email
        m_prt = m.rpartition("@")
        result.append(f"{nn if nn else m_prt[0]}: {m_prt[2]}")
        
    return sorted(result) 

  
def do(args):
    """
    Main doer method
    """

    global domains_dict
    
    if not [a for a in args.__dict__.keys() if getattr(args, a) and a != 'func']:
        print("At least one parameter should be defined:")
        parser.print_help()
        return -1

    all = args.all

    # generate domains_dict and domains_set
    domains_json = load_rena_domains()
    if domains_json is None:
        return -1

    domains_dict, domains_set = get_rena_domains_dict_set(domains_json)

    p_header(f"Reporting timestamp: {datetime.now()}")


    status = 'active'
   
    users, emails, domains_count = get_users_and_domains_stats(status)
   

    if all or args.users_per_mpg_aff:
        p_header(get_help(parser, '--users-per-mpg-aff'))
        for key, value in sorted(domains_count.items(), key=lambda item: item[1], reverse=True):
            print(f"{key}: {value}")
             
        more_than_50 = [domains_count[key] for key in domains_count.keys() if  domains_count[key] > 50]
        print(f"Number of Institutes with more than 50 {status} users: {len(more_than_50)}")

        more_than_100 = [domains_count[key] for key in domains_count.keys() if  domains_count[key] > 100]
        print(f"Number of Institutes with more than 100 {status} users: {len(more_than_100)}")
        
    if all or args.activated_users:
        p_header(get_help(parser, '--activated-users'))
        # print(users[0])
        # for name, value in vars(users[0]).items():  # то же, что obj.__dict__
        #     print(name, "=", value)

        for s in get_usernick_domain_list(users):
            print(s)
 
    if all or args.deactivated_users:
        p_header(get_help(parser, '--deactivated-users'))
        deactivated_users, _, _ = get_users_and_domains_stats('inactive')
        for s in get_usernick_domain_list(deactivated_users):
            print(s)
 
parser.add_argument('--users-per-mpg-aff', action='store_true', help='Members per MPG Affiliation')
# parser.add_argument('--mpg-affs', action='store_true', help='Number of MPG Affiliations on board')
parser.add_argument('--activated-users', action='store_true', help='List of activated user')
parser.add_argument('--deactivated-users', action='store_true', help='List of deactivated user')
parser.add_argument('-a', '--all', action='store_true', help='Show all')
parser.set_defaults(func=do)
args = parser.parse_args()

exit(args.func(args))
