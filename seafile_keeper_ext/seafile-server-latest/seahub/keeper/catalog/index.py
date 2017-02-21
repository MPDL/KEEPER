#!/usr/bin/env python
# -*- coding: utf-8 -*-

import templayer
import json
import urllib2
import urlparse
import math
import cgi
import sys
import time
import os
import StringIO
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")
os.environ.setdefault("CCNET_CONF_DIR", "/opt/seafile/ccnet")
os.environ.setdefault("SEAFILE_CONF_DIR", "/opt/seafile/seafile-data")
os.environ.setdefault("SEAFILE_CENTRAL_CONF_DIR", "/opt/seafile/conf")
os.environ.setdefault("SEAFES_DIR", "/opt/seafile/seafile-server-latest/pro/python/seafes")

from seahub.settings import SERVICE_URL, LOGO_PATH
from keeper.catalog.catalog_manager import is_in_mpg_ip_range, get_catalog

#########################
#                       #
#   start config vars   #
#                       #
#########################

# local install path of this script and files
install_path = '/opt/seafile/seafile-server-latest/seahub/keeper/catalog/'

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
pagination_items = 25 # per page

#########################
#                       #
#    end config vars    #
#                       #
#########################


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


        # test for valid IP
        is_valid_user = 0 # default 0 not valid
        for allowed_ip_prefix in allowed_ip_prefixes:
            if (env['REMOTE_ADDR'].startswith(allowed_ip_prefix)):
                errmsg = ''
                is_valid_user = 1
                break
        # change this or add code to support sigle-sign-on or session based authentification

        if is_valid_user == 0 and is_in_mpg_ip_range(env['REMOTE_ADDR']):
            errmsg = ''
            is_valid_user = 1

        # allow all
        #is_valid_user = 1
        #errmsg = ''


        results = []
        if (is_valid_user == 1 and len(errmsg) <= 0):
            jsondata = get_catalog()
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
                    if (env['QUERY_STRING'] and 'page' in urlparse.parse_qs(env['QUERY_STRING'])):
                        pagination_current = int(urlparse.parse_qs(env['QUERY_STRING'])['page'][0])
                except (RuntimeError, TypeError, NameError, ValueError):
                    pagination_current = 0 # ignore error

                if ( pagination_current >= 1 ):
                    pagination_current = pagination_current-1
                else:
                    pagination_current = 0
            except (RuntimeError, TypeError, NameError, ValueError):
                '' # ignore error


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
            tmpl = templayer.HTMLTemplate(install_path+'main.tpl')
            file_writer = tmpl.start_file(response)
            main_layer = file_writer.open(errmsg='', logo_path=LOGO_PATH)


            main_layer.write_layer('data-nav')


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
                result_id = '#'
                if ( 'id' in tmpresult):
                    result_id = '/f/'+tmpresult['id']

                result_title = 'Project in progress;'
                if ( 'title' in tmpresult and len(tmpresult['title']) > 0 ):
                    if ( len(tmpresult['title']) > 200 ):
                        result_title = (tmpresult['title'][0:197]+'...')
                    else:
                        result_title = tmpresult['title']

                result_owner = ''
                if ( 'owner' in tmpresult):
                    result_owner = tmpresult['owner'].lower()

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

                result_description = ''
                if ( 'description' in tmpresult and len(tmpresult['description']) > 0 ):
                    if ( len(tmpresult['description']) > 200 ):
                        result_description = (tmpresult['description'][0:197]+'...')
                    else:
                        result_description = tmpresult['description']

                if ( 'is_certified' in tmpresult and tmpresult['is_certified'] == True ):
                    main_layer.write_layer('dataset_certified', title=result_title, author=', '.join(result_author), contact=result_owner, smalltext=result_description )
                else:
                    main_layer.write_layer('dataset', title=result_title, author=', '.join(result_author), contact=result_owner, smalltext=result_description )


            # load pagination into template
            main_layer.write_layer('pagination-start',style='margin-top:20px')
            if ( pagination_current > 0 ):
                main_layer.write_layer('page-prev',page=str(pagination_current))
            else:
                main_layer.write_layer('page-prev-disabled')
            for i in range( 0, int(math.ceil(1.0*totalitemscount/pagination_items)) ):
                if (i == pagination_current):
                    main_layer.write_layer('pagination',page=[str(i+1)], cssclass='active')
                else:
                    main_layer.write_layer('pagination',page=[str(i+1)], cssclass='')
            if ( pagination_current+2 <= math.ceil(1.0*totalitemscount/pagination_items) ):
                main_layer.write_layer('page-next',page=str(pagination_current+2))
            else:
                main_layer.write_layer('page-next-disabled')
            main_layer.write_layer('pagination-end')

            main_layer.write_layer('data-nav-end')

            file_writer.close()


        else:

            # load template with error message
            tmpl = templayer.HTMLTemplate(install_path+'main.tpl')
            file_writer = tmpl.start_file(response)
            file_writer.open(errmsg=errmsg, logo_path=LOGO_PATH)
            file_writer.close()


        # send response to nginx
        return(response.getvalue()+"\n<!-- render: "+str(time.time()-timer)+" -->\n")

# end of file while is halt so

