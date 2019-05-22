#!/usr/bin/env python
# -*- coding: utf-8 -*-

import templayer
import json
import urllib2
from urlparse import parse_qs
import math
import cgi
import sys
import time
import os
import StringIO


import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")
os.environ.setdefault("CCNET_CONF_DIR", "__SEAFILE_DIR__/ccnet")
os.environ.setdefault("SEAFILE_CONF_DIR", "__SEAFILE_DIR__/seafile-data")
os.environ.setdefault("SEAFILE_CENTRAL_CONF_DIR", "__SEAFILE_DIR__/conf")
os.environ.setdefault("SEAFES_DIR", "__SEAFILE_DIR__/seafile-server-latest/pro/python/seafes")

from django.core.cache import cache

from seahub.settings import SERVICE_URL, LOGO_PATH, SEAFILE_DIR, DEBUG
from keeper.catalog.catalog_manager import is_in_mpg_ip_range, get_catalog

#########################
#                       #
#   start config vars   #
#                       #
#########################

# local install path of this script and files
install_path =  SEAFILE_DIR + '/seafile-server-latest/seahub/keeper/catalog/'

# all alloews ips or ip prefixes can be added here, empty string for all
allowed_ip_prefixes = []
# allowed_ip_prefixes = ['','172.16.1','10.10.','192.168.1.10','192.129.1.102']

# absolute url of json file with data of all projects
json_data_url = SERVICE_URL + '/api2/catalog/'

# path to cache json, make sure it is writable for script user
json_cache_file_path = install_path+'catalog.json'

# time to hold cache in minutes
json_cache_time = 0 # minutes

# items per page for pagination
pagination_items = 20 # per page

# max pages in paginator
max_pages_in_paginator = 5 # links


#########################
#                       #
#    end config vars    #
#                       #
#########################

def get_keeper_footer():
    """Get keeper_footer from cache
    """
    CACHE_KEY = 'KEEPER_FOOTER_HTML'
    keeper_footer = cache.get(CACHE_KEY)
    if DEBUG or keeper_footer is None:
        # read footer
        f = open(SEAFILE_DIR + '/seahub-data/custom/templates/keeper_footer.html', 'r')
        keeper_footer = unicode(f.read(), 'utf-8')
        f.close()
        cache.set(CACHE_KEY, keeper_footer, 0)
    return keeper_footer


def application(env, start_response):

    timer = time.time()

    # check static data (e.g. images)
    if ( 'static' in str(env['REQUEST_URI']) ):

        # send image header
        start_response('200 OK', [('Content-Type','image/png')])

        # image path
        tmp_static_path = install_path+str(env['REQUEST_URI'])[str(env['REQUEST_URI']).find('static'):]

        # send response to nginx
        return open(tmp_static_path,'r').read()

    else:
        # send html header
        start_response('200 OK', [('Content-Type','text/html')])

        # start response
        response = StringIO.StringIO()


        # default text if IP not allowed
        errmsg = unicode('Sie sind leider nicht berechtigt den Projektkatalog zu öffnen. Bitte wenden Sie sich an den Keeper Support.','utf-8')


        # get HTTP_X_FORWARDED_FOR (i.e. servier is clustered), otherwise remote address
        remote_addr = env['HTTP_X_FORWARDED_FOR'] if 'HTTP_X_FORWARDED_FOR' in env else env['REMOTE_ADDR']

        # test for valid IP
        is_valid_user = 0 # default 0 not valid
        for allowed_ip_prefix in allowed_ip_prefixes:
            if (remote_addr.startswith(allowed_ip_prefix)):
                errmsg = ''
                is_valid_user = 1
                break
        # change this or add code to support sigle-sign-on or session based authentification

        #if is_valid_user == 0 and is_in_mpg_ip_range(remote_addr):
        #    errmsg = ''
        #    is_valid_user = 1

        # allow all
        is_valid_user = 1
        errmsg = ''


        results = []
        if (is_valid_user == 1 and len(errmsg) <= 0):

            get_params = parse_qs(env['QUERY_STRING'])

			# pars request params
            try:
                request_body_size = int(env.get('CONTENT_LENGTH', 0))
            except (ValueError):
                request_body_size = 0

            logging.error(env)
            request_body = env['wsgi.input'].read()
            post_params = parse_qs(request_body)
            logging.error(post_params)
            scope = post_params['cat_scope'][0] if 'cat_scope' in post_params else get_params['scope'][0] if 'scope' in get_params else 'with_metadata'

            # jsondata = get_catalog(filter=scope[0])
            jsondata = get_catalog(scope)
            """
            # init var
            jsondata = ''
            # test if json from cache is too old (5min)
            if ( not(os.path.isfile(json_cache_file_path) ) or (time.time() - os.path.getmtime(json_cache_file_path) > (json_cache_time * 60)) ):

                # get json from server
                responseJson = urllib2.urlopen(json_data_url)
                jsondataraw = responseJson.read()

                # validate json
                try:
                    jsondata = json.loads(jsondataraw)
                except ValueError:
                    errmsg = 'the data ist not correct, please try again'
                    # load json from cache
                    with open(json_cache_file_path) as cachefile:
                        jsondata = json.load(cachefile)

                # cache json
                with open(json_cache_file_path, 'w') as cachefile:
                    json.dump(jsondata, cachefile)

            else:

                # load cached file
                with open(json_cache_file_path) as cachefile:
                    jsondata = json.load(cachefile)
            """

            # load pagination parameter
            totalitemscount = 0
            pagination_current = 0
            try:
                totalitemscount = len(jsondata)

                #form = cgi.FieldStorage()
                #pagination_current = int(form.getvalue('page'))
                try:
                    if 'cat_scope' in post_params:
                        pagination_current = 0 # ignore error
                    elif (env['QUERY_STRING'] and 'page' in parse_qs(env['QUERY_STRING'])):
                        pagination_current = int(parse_qs(env['QUERY_STRING'])['page'][0])
                except (RuntimeError, TypeError, NameError, ValueError):
                    pagination_current = 0 # ignore error

                if ( pagination_current >= 1 ):
                    pagination_current = pagination_current-1
                else:
                    pagination_current = 0
            except (RuntimeError, TypeError, NameError, ValueError):
                pass  # ignore error


            # TODO load institute parameter


            # parse json an format data
            for i in range( (pagination_current*pagination_items), (pagination_current*pagination_items+pagination_items) ):
                if ( i < len(jsondata) ):
                    results.append(jsondata[i])


            # debug parsed data output
            #print('<pre>')
            #print(jsondata)
            #print(results)
            #print('</pre>')


            # load template
            tmpl = templayer.HTMLTemplate(install_path + 'main.tpl')
            file_writer = tmpl.start_file(response)
            main_layer = file_writer.open(errmsg='', logo_path=LOGO_PATH, footer=templayer.RawHTML(get_keeper_footer()))


            slots = {}
            slots['checked_' + scope] = 'checked'
            main_layer.write_layer('data-nav', **slots)


            # load pagination into template
#           main_layer.write_layer('pagination-start',style='margin-bottom:20px')
#           if ( pagination_current > 0 ):
#               main_layer.write_layer('page-prev',page=str(pagination_current))
#           else:
#               main_layer.write_layer('page-prev-disabled')
#           for i in range( 0, int(math.ceil(1.0*totalitemscount/pagination_items)) ):
#               if (i == pagination_current):
#                   main_layer.write_layer('pagination',page=[str(i+1)], cssclass='active')
#               else:
#                   main_layer.write_layer('pagination',page=[str(i+1)], cssclass='')
#           if ( pagination_current+2 <= math.ceil(1.0*totalitemscount/pagination_items) ):
#               main_layer.write_layer('page-next',page=str(pagination_current+2))
#           else:
#               main_layer.write_layer('page-next-disabled')
#           main_layer.write_layer('pagination-end')


            # load datasets into template
            for tmpresult in results:

                slots = {}
                result_id = '#'
                if ( 'id' in tmpresult):
                    result_id = '/f/'+tmpresult['id']

                result_title = "Project archive no. %s" % tmpresult['catalog_id']
                if ( 'title' in tmpresult and len(tmpresult['title']) > 0 ):
                    if ( len(tmpresult['title']) > 200 ):
                        result_title = (tmpresult['title'][0:197]+'...')
                    else:
                        result_title = tmpresult['title']
                slots['title'] = result_title

                result_owner = ''
                if ( 'owner' in tmpresult):
                    result_owner = tmpresult['owner'].lower()
                slots['contact'] = result_owner

                result_author = []
                if ( 'authors' in tmpresult):
                    for j in xrange(len(tmpresult['authors'])):
                        tmpauthors = tmpresult['authors'][j]
                        tmpauthor = ""
                        tmpauthorlist = tmpauthors['name'].title().split(', ')
                        for i in xrange(len(tmpauthorlist)):
                            if ( i <= 0 and len(tmpauthorlist[i].strip()) > 1 ):
                                tmpauthor += tmpauthorlist[i]+", "
                            elif (len(tmpauthorlist[i].strip()) > 1):
                                tmpauthor += tmpauthorlist[i].strip()[:1]+"., "
                        tmpauthor = tmpauthor.strip()[:-1]

                        if (j >= 5):
                            tmpauthor = "et al."
                        result_author.append( tmpauthor )
                        if (j >= 5):
                            break

                        if ( 'affs' in tmpauthors):
                            #TODO check if correct format
                            result_author.append( ','.join(tmpauthors['affs']).title() )
                slots['author'] = ', '.join(result_author)

                result_description = ''
                if ( 'description' in tmpresult and len(tmpresult['description']) > 0 ):
                    if ( len(tmpresult['description']) > 200 ):
                        result_description = (tmpresult['description'][0:197]+'...')
                    else:
                        result_description = tmpresult['description']
                slots['smalltext'] = result_description


                slots['year']=''
                if ( 'year' in tmpresult and len(tmpresult['year']) > 0 ):
                    slots['year'] = tmpl.format('fyear', year=tmpresult['year'])



                if ( 'is_certified' in tmpresult and tmpresult['is_certified'] == True ):
                    main_layer.write_layer('dataset_certified', **slots)
                else:
                    main_layer.write_layer('dataset', **slots)



            # load pagination into template
            if totalitemscount > pagination_items:

                # max number of pages
                max_pages_count = (totalitemscount / pagination_items) + 1 if totalitemscount > pagination_items else 0

                # pagination_group = int(math.ceil( 1.0 * (pagination_current + 1) / (max_pages_in_paginator + 1) + 1) )
                pagination_group = pagination_current / max_pages_in_paginator
                start_page = pagination_group * max_pages_in_paginator + 1
                end_page = start_page + max_pages_in_paginator - 1
                end_page = min(end_page, max_pages_count)

                main_layer.write_layer('pagination-start',style='margin-top:20px',
                                       # debug="start_page=" + str(start_page) + ";end_page=" + str(end_page) + ";pagination_current=" + str(pagination_current) + ";totalitemscount=" + str(totalitemscount) +
                                       # ";max_pages_count=" + str(max_pages_count) + ";pagination_group=" +str(pagination_group)
                                       )
                if ( pagination_current > 0 ):
                    main_layer.write_layer('page-prev', page=str(pagination_current), scope=scope)
                if ( pagination_group > 1 ):
                    main_layer.write_layer('group-prev', page=str((pagination_group - 1) * max_pages_in_paginator + 1 ), scope=scope)
                for i in range( start_page, end_page + 1 ):
                    main_layer.write_layer('pagination', page=str(i),
                                           cssclass='active' if i - 1 == pagination_current else '',
                                           scope=scope)
                next_group_first_page = (pagination_group + 1) * max_pages_in_paginator + 1
                if ( next_group_first_page < max_pages_count ):
                    main_layer.write_layer('group-next', page=str(next_group_first_page), scope=scope)
                if ( pagination_current + 1 < max_pages_count):
                    main_layer.write_layer('page-next',page=str(pagination_current+2), scope=scope)
                main_layer.write_layer('pagination-end')

            main_layer.write_layer('data-nav-end')

            file_writer.close()


        else:

            # load template with error message
            tmpl = templayer.HTMLTemplate(install_path+'main.tpl')
            file_writer = tmpl.start_file(response)
            file_writer.open(errmsg=errmsg, logo_path=LOGO_PATH, footer=templayer.RawHTML(get_keeper_footer()))

            file_writer.close()


        # send response to nginx
        return(response.getvalue()+"\n<!-- render: "+str(time.time()-timer)+" -->\n")

# end of file while is halt so

