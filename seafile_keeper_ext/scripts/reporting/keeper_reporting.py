#!/usr/bin/env python3

import os
import sys
import json
import requests
import argparse
import pprint
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict, Counter

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
    """
    Parse keeperx.json structure:
    details → [ { "123": { "domains": [...], "inst_name_de": "...", ... } }, ... ]
    Returns: dict[inst_name_de → list of domains], set of all domains
    """
    domains_dict = {}
    domains_set = set()

    if not domains_json:
        return domains_dict, domains_set

    details = domains_json.get('details', [])
    for entry in details:
        # entry is dict with ONE key (the number "100", "200", etc.)
        for inst_key, inst_data in entry.items():
            if not isinstance(inst_data, dict):
                continue

            inst_name = inst_data.get('inst_name_de')
            domains = inst_data.get('domains', [])

            if inst_name and domains:
                # Optional: normalize name (strip whitespace, etc.)
                inst_name = inst_name.strip()
                domains_dict[inst_name] = [d.strip().lower() for d in domains]
                domains_set.update(domains_dict[inst_name])

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

def ctime_to_datetime(ctime):
    """
    Convert Seafile's microsecond timestamp to datetime (UTC).
    Returns None if invalid.
    """
    if ctime is None or ctime <= 0:
        return None
    try:
        return datetime.fromtimestamp(ctime / 1_000_000, tz=timezone.utc)
    except (OSError, ValueError):
        return None

def ctime_to_year(ctime):
    """Quick helper: get year or None"""
    dt = ctime_to_datetime(ctime)
    return dt.year if dt else None


def get_institutes_per_creation_year(users, status_filter='all'):
    """
    Returns: dict[year → set of institute names]
             and dict[year → count of distinct institutes]
    """
    year_to_institutes = defaultdict(set)
    
    for u in users:
        # Skip if we want only active and user is inactive
        if status_filter == 'active' and not u.is_active:
            continue
            
        if not hasattr(u, 'ctime') or u.ctime is None or u.ctime <= 0:
            continue  # rare case - skip invalid ctime
            
        year = ctime_to_year(getattr(u, 'ctime', None))
        if year is None:
            continue
        
        # Get resolved email (same logic as in your script)
        email = str(u.email)
        if email.endswith("@auth.local"):
            p = Profile.objects.get_profile_by_user(email)
            if hasattr(p, 'contact_email') and p.contact_email:
                email = p.contact_email
            else:
                continue  # no usable email
        
        # Extract domain
        try:
            domain = email.split('@', 1)[1].lower()
        except IndexError:
            continue
        
        # Find matching institute
        found_inst = None
        for inst_name, domains_list in domains_dict.items():
            if domain in [d.lower() for d in domains_list]:
                found_inst = inst_name
                break
        
        if found_inst:
            year_to_institutes[year].add(found_inst)
    
    # Convert sets → counts
    year_to_count = {y: len(insts) for y, insts in sorted(year_to_institutes.items())}
    
    return year_to_institutes, year_to_count
  
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
            
    if all or args.institutes_per_creation_year:
        p_header(get_help(parser, '--institutes-per-creation-year'))
        
        status = 'active'
        all_users = ccnet_threaded_rpc.get_emailusers('DB', -1, -1, status)  # 'all' = active + inactive

        year_to_institutes, _ = get_institutes_per_creation_year(all_users, status_filter=status)
        
        if not year_to_institutes:
            print("No users with mappable MPG domains and valid creation timestamp found.")
        else:
            print("Distinct MPG institutes first appearing per creation year:")
            print("-------------------------------------------------------")
            inst_set_cum = set()
            for year, inst_set in sorted(year_to_institutes.items()):
                # NOTE: only institutes with "Max-Planck" in the name!
                mpi_only = {x for x in inst_set if "max-planck" in x.lower()}
                inst_set_cum |= mpi_only
                print(f"{year:4d}: new users from {len(mpi_only):3d} institutes (cumulative: {len(inst_set_cum):3d})")
            
            print(f"\nTotal distinct MPG institutes ever observed: {len(inst_set_cum)}")
            print(f"Based on {len(all_users)} total user accounts (status: {status}) in ccnet.EmailUser")
             
parser.add_argument('--users-per-mpg-aff', action='store_true', help='Members per MPG Affiliation')
# parser.add_argument('--mpg-affs', action='store_true', help='Number of MPG Affiliations on board')
parser.add_argument('--activated-users', action='store_true', help='List of activated user')
parser.add_argument('--deactivated-users', action='store_true', help='List of deactivated user')
parser.add_argument(
    '--institutes-per-creation-year',
    action='store_true',
    help='Number of distinct MPG institutions per user creation year (based on email domain)'
)
parser.add_argument('-a', '--all', action='store_true', help='Show all')
parser.set_defaults(func=do)
args = parser.parse_args()

exit(args.func(args))
