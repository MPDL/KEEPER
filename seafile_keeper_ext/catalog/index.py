#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import templayer
import json
import urllib2
import math
import cgi
import sys
import time
import os

import pprint

import cgi, cgitb 

import web

from StringIO import StringIO

cgitb.enable()

#########################
#                       #
#   start config vars   #
#                       #
#########################

# all alloews ips or ip prefixes can be added here, empty string for all
allowed_ip_prefixes = ['','172.16.1','10.10.','192.168.1.10','192.129.1.102']

# absolute url of json file with data of all projects
json_data_url = 'https://qa-keeper.mpdl.mpg.de/api2/catalog/'

# path to cache json, make sure it is writable for script user
json_cache_file_path = './catalog.json'

# time to hold cache in minutes
json_cache_time = 5 # minutes

# items per page for pagination
pagination_items = 25 # per page

#########################
#                       #
#    end config vars    #
#                       #
#########################


# WEB server stuff
urls = (
    '/.*', 'catalog'
)

app = web.application(urls, globals())

class catalog:
    def GET(self):
        temp = sys.stdout                 # store original stdout object for later
        result = StringIO()
        sys.stdout = result 
        generate_catalog()
        sys.stdout = temp
        return result.getvalue()


if __name__ == "__main__":
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()



def generate_catalog():
    # send html header
    #print('Content-type: text/html; charset=utf-8\r\n\r\n')
    timer = time.time()


    # default text if IP not allowed
    errmsg = u'Sie sind leider nicht berechtigt den Projektkatalog zu öffnen. Bitte wenden Sie sich an den Keeper Support.'
    # pprint.pprint(os.environ)

    # test for valid IP
    is_valid_user = 0
    # for allowed_ip_prefix in allowed_ip_prefixes:
    # if (os.environ.get('REMOTE_ADDR') and os.environ['REMOTE_ADDR'].startswith(allowed_ip_prefix)):
    errmsg = ''
    is_valid_user = 1
    #    break
    # change this or add code to support sigle-sign-on or session based authentification
    

    results = []
    if (is_valid_user == 1 and len(errmsg) <= 0):

            # init var
            jsondata = ''
            
            # test if json from cache is too old (5min)
            if ( not(os.path.isfile(json_cache_file_path) ) or (time.time() - os.path.getmtime(json_cache_file_path) > (json_cache_time * 60)) ):
                    
                    # get json from server
                    response = urllib2.urlopen(json_data_url)
                    jsondataraw = response.read()
                    
                    # validate json
                    try:
                            jsondata = json.loads(jsondataraw)
                    except ValueError:
                            errmsg = 'the data ist not correct, please try again'
                            # load json from cache
                    
                    # cache json
                    with open(json_cache_file_path, 'w') as cachefile:
                        json.dump(jsondata, cachefile)
                    
            else:
                    
                    # load cached file
                    with open(json_cache_file_path) as cachefile:
                        jsondata = json.load(cachefile)
                    
            
            # load pagination parameter
            totalitemscount = 0
            pagination_current = 0
            try:
                    form = cgi.FieldStorage()
                    totalitemscount = len(jsondata)
                    pagination_current = int(form.getvalue('page'))
                    if ( pagination_current >= 1 ):
                            pagination_current = pagination_current-1
                    else:
                            pagination_current = 0
            except (RuntimeError, TypeError, NameError, ValueError):
                    print '' # ignore error
            
            
            # TODO load project parameter
            
            
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
            tmpl = templayer.HTMLTemplate('main.tpl')
            file_writer = tmpl.start_file()
            main_layer = file_writer.open(errmsg='')
            
            main_layer.write_layer('data-nav')
            
            
            # load pagination into template
            #	main_layer.write_layer('pagination-start',style='margin-bottom:20px')
            #	if ( pagination_current > 0 ):
            #		main_layer.write_layer('page-prev',page=str(pagination_current))
            #	else:
            #		main_layer.write_layer('page-prev-disabled')
            #	for i in range( 0, int(math.ceil(1.0*totalitemscount/pagination_items)) ):
            #		if (i == pagination_current):
            #			main_layer.write_layer('pagination',page=[str(i+1)], cssclass='active')
            #		else:
            #			main_layer.write_layer('pagination',page=[str(i+1)], cssclass='')
            #	if ( pagination_current+2 <= math.ceil(1.0*totalitemscount/pagination_items) ):
            #		main_layer.write_layer('page-next',page=str(pagination_current+2))
            #	else:
            #		main_layer.write_layer('page-next-disabled')
            #	main_layer.write_layer('pagination-end')
                    
            
            # load datasets into template
            for tmpresult in results:
                    result_id = '#'
                    if ( 'id' in tmpresult):
                            result_id = '/f/'+tmpresult['id']
                    
                    result_cert = ''
                    if ( 'is_certified' in tmpresult):
                            result_cert = 'is_certified'
                    
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
                    
                    if ( result_cert == 'is_certified' ):
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
            tmpl = templayer.HTMLTemplate('main.tpl')
            file_writer = tmpl.start_file()
            main_layer = file_writer.open(errmsg=errmsg)
            file_writer.close()

    print("<!-- render: "+str(time.time()-timer)+" -->")

    # end of file while is halt so



