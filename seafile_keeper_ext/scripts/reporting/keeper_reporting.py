#!/usr/bin/env python3

import os
import json
import requests
import argparse
from datetime import datetime, timezone
from collections import defaultdict

import humanize
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")
django.setup()

from seahub.profile.models import Profile
from seaserv import ccnet_threaded_rpc, seafserv_threaded_rpc

from django.db import connection

DOMAINS_URL = 'https://rena.mpdl.mpg.de/iplists/keeperx.json'

domains_dict = None

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
                inst_name = inst_name.strip()
                domains_dict[inst_name] = [d.strip().lower() for d in domains]
                domains_set.update(domains_dict[inst_name])

    return domains_dict, domains_set


def get_users_and_domains_stats(status='active', last_interval=None, year=None, all_activity=False):

    global domains_dict

    if status in (None, 'all'):
        all_users = ccnet_threaded_rpc.get_emailusers('DB', -1, -1, '')
    else:
        all_users = ccnet_threaded_rpc.get_emailusers('DB', -1, -1, status)

    if last_interval or year or all_activity:
        if all_activity:
            where_login = ""
            where_api = ""
        elif year:
            where_login = f"WHERE YEAR(last_login) = {year}"
            where_api = f"WHERE YEAR(last_accessed) = {year}"
        else:
            where_login = f"WHERE last_login >= NOW() - INTERVAL {last_interval}"
            where_api = f"WHERE last_accessed >= NOW() - INTERVAL {last_interval}"

        SQL = f"""
            SELECT
                username,
                (
                    SELECT contact_email
                    FROM `seahub-db`.profile_profile
                    WHERE username = profile_profile.user
                ) AS contact_mail
            FROM base_userlastlogin
            {where_login}

            UNION

            SELECT
                user,
                (
                    SELECT contact_email
                    FROM `seahub-db`.profile_profile
                    WHERE api2_tokenv2.user = profile_profile.user
                ) AS contact_mail
            FROM api2_tokenv2
            {where_api}

            ORDER BY 2
            """

        with connection.cursor() as cursor:
            cursor.execute(SQL)
            rows = cursor.fetchall()

        sql_usernames = {username for username, _ in rows}
        users = [u for u in all_users if u.email in sql_usernames]
        emails = [contact_mail if username.endswith("@auth.local") else username for username, contact_mail in rows]
    else:
        users = all_users
        emails = []
        for u in users:
            email = str(u.email)
            if email.endswith("@auth.local"):
                p = Profile.objects.get_profile_by_user(email)
                if hasattr(p, 'contact_email'):
                    emails.append(p.contact_email)
            else:
                emails.append(email)

    domains_count = defaultdict(int)
    for inst, d_list in domains_dict.items():
        for e in emails:
            if e and e[e.index('@')+1:] in d_list:
                domains_count[inst] += 1

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


def get_non_mpg_list(users, domains_set):
    result = []
    for u in users:
        nn = None
        email = str(u.email)
        p = Profile.objects.get_profile_by_user(email)
        if hasattr(p, 'nickname'):
            nn = p.nickname
        if email.endswith("@auth.local"):
            m = p.contact_email if hasattr(p, 'contact_email') and p.contact_email else None
        else:
            m = email
        if not m:
            continue
        try:
            domain = m.split('@', 1)[1].lower()
        except IndexError:
            continue
        if domain not in domains_set:
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
        
        # Find matching institute (domains already lowercased in get_rena_domains_dict_set)
        found_inst = None
        for inst_name, domains_list in domains_dict.items():
            if domain in domains_list:
                found_inst = inst_name
                break
        
        if found_inst:
            year_to_institutes[year].add(found_inst)
    
    # Convert sets → counts
    year_to_count = {y: len(insts) for y, insts in sorted(year_to_institutes.items())}
    
    return year_to_institutes, year_to_count
  
def get_storage_per_institution(users):
    global domains_dict

    inst_storage = defaultdict(int)

    for u in users:
        email = str(u.email)
        if email.endswith("@auth.local"):
            p = Profile.objects.get_profile_by_user(email)
            if hasattr(p, 'contact_email') and p.contact_email:
                email = p.contact_email
            else:
                continue

        try:
            domain = email.split('@', 1)[1].lower()
        except IndexError:
            continue

        usage = seafserv_threaded_rpc.get_user_quota_usage(str(u.email))
        if not usage or usage <= 0:
            continue

        for inst_name, domains_list in domains_dict.items():
            if domain in domains_list:
                inst_storage[inst_name] += usage
                break

    return inst_storage


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

    status = 'active'
    last_interval = None
    # last_interval = '6 month'


    p_header(f"Reporting timestamp: {datetime.now()}" + (f", last_interval: {last_interval}" if last_interval else ""))

    users, emails, domains_count = get_users_and_domains_stats(status=status, last_interval=last_interval)
   

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
        for s in get_usernick_domain_list(users):
            print(s)
 
    if all or args.deactivated_users:
        p_header(get_help(parser, '--deactivated-users'))
        deactivated_users, _, _ = get_users_and_domains_stats(status='inactive', last_interval=None)
        for s in get_usernick_domain_list(deactivated_users):
            print(s)
            
    if all or args.used_last_n_months is not None:
        months = args.used_last_n_months or 12
        p_header(get_help(parser, '--used-last-n-months') + f" ({months} months)")
        users_nm, _, _ = get_users_and_domains_stats(status=None, last_interval=f'{months} MONTH')
        print(f"Total: {len(users_nm)}")
        for s in get_usernick_domain_list(users_nm):
            print(s)

    if all or args.non_mpg_used_in_year is not None:
        year_val = args.non_mpg_used_in_year or 2025
        p_header(get_help(parser, '--non-mpg-used-in-year') + f" ({year_val})")
        users_y, _, _ = get_users_and_domains_stats(status=None, year=year_val)
        result = get_non_mpg_list(users_y, domains_set)
        print(f"Total: {len(result)}")
        for s in result:
            print(s)

    if all or args.non_mpg_used:
        p_header(get_help(parser, '--non-mpg-used'))
        users_all, _, _ = get_users_and_domains_stats(status=None, all_activity=True)
        result = get_non_mpg_list(users_all, domains_set)
        print(f"Total: {len(result)}")
        for s in result:
            print(s)

    if all or args.storage_per_institution:
        p_header(get_help(parser, '--storage-per-institution'))
        inst_storage = get_storage_per_institution(users)
        total = sum(inst_storage.values())
        for inst, size in sorted(inst_storage.items(), key=lambda x: x[1], reverse=True):
            print(f"{inst}: {humanize.naturalsize(size)}")
        print(f"Total (mapped to MPG institutions): {humanize.naturalsize(total)}")

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
parser.add_argument('--used-last-n-months', type=int, default=None, metavar='N',
    help='Users who used Keeper in the last N months (incl. deactivated); default: 12')
parser.add_argument('--non-mpg-used-in-year', type=int, default=None, metavar='YEAR',
    help='Non-MPG users who used Keeper in the given year (incl. deactivated); default: 2025')
parser.add_argument('--non-mpg-used', action='store_true',
    help='Non-MPG users who ever used Keeper (all years, incl. deactivated)')
parser.add_argument(
    '--institutes-per-creation-year',
    action='store_true',
    help='Number of distinct MPG institutions per user creation year (based on email domain)'
)
parser.add_argument('--storage-per-institution', action='store_true',
    help='Storage usage per MPG institution (in GB)')
parser.add_argument('-a', '--all', action='store_true', help='Show all')
parser.set_defaults(func=do)
args = parser.parse_args()

exit(args.func(args))
