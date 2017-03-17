#!/usr/bin/env python

import traceback

from seaserv import get_commits, get_commit, get_repo_owner, seafile_api
from seafobj import fs_mgr
from seahub.settings import ARCHIVE_METADATA_TARGET

from keeper.cdc.cdc_manager import is_certified_by_repo_id
from keeper.common import parse_markdown, get_user_name

from keeper.models import Catalog

import logging
import json
from netaddr import IPAddress, IPSet

import urllib2

from django.core.cache import cache
from django.db import connections

#time to live of the mpg IP set: day
IP_SET_TTL = 60 * 60 * 24

MAX_INT = 2147483647

JSON_DATA_URL = 'https://rena.mpdl.mpg.de/iplists/keeper.json'

def trim_by_len(str, max_len, suffix="..."):
    if str:
        str = str.strip()
        if str and len(str) > max_len:
            str = str[0:max_len] + suffix
        str = unicode(str, 'utf-8', errors='replace')
    return str

def strip_uni(str):
    if str:
        str = unicode(str.strip(), 'utf-8', errors='replace')
    return str

def get_mpg_ip_set():
    """
    Get MPG IP ranges from cache or from rena service if cache is expired
    """
    if cache.get('KEEPER_CATALOG_LAST_FETCHED') is None:
        logging.info("Put ips to cache...")
        try:
            # get json from server
            response = urllib2.urlopen(JSON_DATA_URL)
            json_str = response.read()
            # parse json
            json_dict = json.loads(json_str)
            # get only ip ranges
            ip_ranges = [(ipr.items())[0][0] for ipr in json_dict['details']]
            ip_set = IPSet(ip_ranges)
            cache.set('KEEPER_CATALOG_MPG_IP_SET', ip_set, None)
            cache.set('KEEPER_CATALOG_LAST_FETCHED', json_dict['timestamp'], IP_SET_TTL)
        except Exception as e:
            logging.info("Cannot get/parse MPG IPs DB: " + ": ".join(str(i) for i in e))
            logging.info("Get IPS from old cache")
            ip_set = cache.get('KEEPER_CATALOG_MPG_IP_SET')
    else:
        logging.info("Get ips from cache...")
        ip_set = cache.get('KEEPER_CATALOG_MPG_IP_SET')
    return ip_set

def is_in_mpg_ip_range(ip):
    return IPAddress(ip) in get_mpg_ip_set()

def generate_catalog_entry(repo):
    """
    Generate catalog entry in for the repo DB
    """

    proj = {}

    try:
        proj["id"] = repo.id
        proj["name"] = repo.name
        email = get_repo_owner(repo.id)
        proj["owner"] = email
        user_name = get_user_name(email)
        if user_name != email:
            proj["owner_name"] = user_name
        proj["in_progress"] = True
        proj["modified"] = repo.last_modify

        commits = get_commits(repo.id, 0, 1)
        commit = get_commit(repo.id, repo.version, commits[0].id)
        dir = fs_mgr.load_seafdir(repo.id, repo.version, commit.root_id)
        file = dir.lookup(ARCHIVE_METADATA_TARGET)
        if file:
            md = parse_markdown(file.get_content())
            if md:
                # Author
                a = md.get("Author")
                if a:
                    a_list = strip_uni(a).split('\n')
                    authors = []
                    for _ in a_list:
                        author = {}
                        aa = _.split(';')
                        author['name'] = aa[0]
                        if len(aa) > 1 and aa[1].strip():
                            author['affs'] = [x.strip() for x in aa[1].split('|')]
                            author['affs'] = [x for x in author['affs'] if x ]
                        authors.append(author)
                    if a:
                        proj["authors"] = authors

                # Description
                d = strip_uni(md.get("Description"))
                if d:
                    proj["description"] = d

                # Comments
                c = strip_uni(md.get("Comments"))
                if c:
                    proj["comments"] = c

                #Title
                t = strip_uni(md.get("Title"))
                if t:
                    proj["title"] = t
                    del proj["in_progress"]

                #Year
                y = strip_uni(md.get("Year"))
                if y:
                    proj["year"] = y

                proj["is_certified"] = is_certified_by_repo_id(repo.id)

        # add or update project metadata in DB
        c = Catalog.objects.add_or_update_by_repo_id(repo.id, email, proj)
        #Catalog_id
        proj["catalog_id"] = str(c.catalog_id)


    except Exception:
        msg = "repo_name: %s, id: %s" % ( repo.name, repo.id )
        logging.error (msg)
        logging.error(traceback.format_exc())

    return proj


def generate_catalog_entry_by_repo_id(repo_id):
    """
    Generate catalog entry by repo_id
    """
    return generate_catalog_entry(seafile_api.get_repo(repo_id))

def get_catalog():
    """
    Get catalog metadata from pre-generated DB cache
    """
    # force db reconnect
    # see https://code.djangoproject.com/ticket/21597#comment:29
    connections['default'].close()
    connections['keeper'].close()

    return Catalog.objects.get_all_mds_ordered()


def delete_catalog_entry_by_repo_id(repo_id):
    """
    Delete catalog entry by repo_id
    """
    Catalog.objects.delete_by_repo_id(repo_id)



def generate_catalog():
    """
    Generate entire catalog and put it into DB cache
    """
    repos_all = [r for r in seafile_api.get_repo_list(0, MAX_INT)
                 if get_repo_owner(r.id) != 'system']

    return [ generate_catalog_entry(repo) for repo in
            sorted(repos_all, key=lambda x: x.last_modify, reverse=True) ]
