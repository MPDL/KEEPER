# -*- coding: utf-8 -*-
import pytest
import tempfile
import json
from uuid import uuid4

# from rest_framework.test import APIClient

import requests
import tempfile

import sys
import logging
from logging import INFO, DEBUG
logging.basicConfig(stream=sys.stdout, level=INFO)

from seahub.settings import TEST_SERVER, TEST_SERVER_ADMIN, TEST_SERVER_PASSWORD

BASE_URL=TEST_SERVER
HEADERS = {}

def log(url, headers, response, level=DEBUG):
    logging.log(level, 'URL:{}\nheaders:{},\nresponse:\n{}'.format(url, headers, response))

def _l(msg, level=DEBUG):
    logging.log(level, '{}'.format(msg))


def get_headers(username, password):
    # key = username[:username.index('@')]
    key = username
    if key not in HEADERS:
        response = requests.post(BASE_URL + '/api2/auth-token/',
                             data={'username':username,'password':password} )
        assert response.status_code == 200
        HEADERS[key] = {'Authorization':'Token ' + response.json()['token'],
                                'Accept':'application/json; indent=4'}
    return HEADERS[key]



# REMOTE with REST
#https://manual.seafile.com/develop/web_api_v2.1html#admin-only-create-account
# PUT https://cloud.seafile.com/api2/accounts/{email}/
def create_remote_tmp_user(headers):
    """Create new random user"""
    email = uuid4().hex + '@test.com'
    password = 'secret'
    response = requests.put(BASE_URL + '/api2/accounts/' + email + '/',
                                data={'password':password},
                                headers=headers)
    assert response.status_code == 201
    yield (email, password)
    # teardown code
    response = requests.delete(BASE_URL + '/api2/accounts/' + email + '/',
                             headers=headers)
    assert response.status_code == 200
    yield


@pytest.fixture(scope='function')
def get_admin_headers():
    return get_headers(TEST_SERVER_ADMIN, TEST_SERVER_PASSWORD)
    # teardown code

def update_file(repo_id, headers, content):
    response = requests.get(BASE_URL+'/api2/repos/'+repo_id+'/update-link/',
                             headers=headers)
    upd_link = response.json()

    response = requests.post(upd_link,
                             files={'file':('test.txt', content)},
                             data={'target_file':'/test.txt'},
                             headers=headers)


# @pytest.mark.skip
def test_snapshot_labels_api(get_admin_headers):

    users = []

    try:
        admin_headers = get_admin_headers

        #create repo

        for i in range(0, 2):

            users.append({'gen' : create_remote_tmp_user(admin_headers) })
            (n, p) = next(users[i]['gen'])
            users[i].update(name=n, password=p)

            headers=get_headers(n, p)
            users[i].update(headers=headers)
            logging.debug("\nNew user:{}\n".format(users[i]))

            response = requests.post(BASE_URL + '/api2/repos/',
                                    data={'name':'test_snap_labels_repo_{}'.format(i)}, headers=headers)
            repo_id = response.json()['repo_id']
            users[i]['repo_id'] = repo_id
            logging.debug(repo_id)

            # create file
            response = requests.post(BASE_URL+'/api/v2.1/repos/'+repo_id+'/file/?p=/test.txt',
                                    data={'operation':'create'}, headers=headers)

            #create first label
            response = requests.post(BASE_URL+'/api/v2.1/revision-tags/tagged-items/',
                                    data={'repo_id':repo_id,'tag_names':'test_tag1_{}'.format(i)},
                                    headers=headers)

            # update file and create new commits
            update_file(repo_id, headers, 'content for first commit')

            # response = requests.get(BASE_URL+'/api/v2.1/repos/'+repo_id+'/history/',
                                    # headers=headers)

            #+1 commit
            update_file(repo_id, headers, 'content for second commit')

            #####################################################################################
            # CRUD
            # CREATE New Snapshot Labels
            response = requests.post(BASE_URL+'/api/v2.1/revision-tags/tagged-items/',
                                    data={'repo_id':repo_id,'tag_names':'test_tag2_{},test_tag3_{}'.format(i, i)},
                                    headers=headers)

            commit_id = response.json()['revisionTags'][0]['revision']['commit_id']

            #####################################################################################
            # Get snapshot labes of a library
            _l('''Get labels by commit''')
            URL = BASE_URL + '/api/v2.1/revision-tags/tag-names/'
            response = requests.get(URL,
                                    data={'repo_id':repo_id},
                                    headers=headers)
            log(URL, headers, response.text)
            assert json.loads(response.text) == json.loads('["test_tag1_{}","test_tag2_{}","test_tag3_{}"]'.format(i, i, i))


            #####################################################################################
            # READ labels by commit
            _l('''Get labels by commit''')
            URL = BASE_URL + '/api/v2.1/revision-tags/tag-names/'
            response = requests.get(URL,
                                    data={'repo_id':repo_id,'commit_id':commit_id},
                                    headers=headers)

            # TODO: NOT IMPLEMENTED. Should it be????
            log(URL, headers, response.text)
            # assert json.loads(response.text) == json.loads('["test_tag2_{}","test_tag3_{}"]'.format(i, i))

            # response = requests.get(BASE_URL+'/api/v2.1/repos/'+repo_id+'/history/',
                                    # headers=headers)
            # logging.debug(response.text)

        #####################################################################################
        # ADMIN
        # Get Snapshots by Label


        ADMIN_URL = BASE_URL + '/api/v2.1/admin/revision-tags/tagged-items/'

        ###################################################################
        _l('''List of labels for all users with corresponding snapshots''')
        URL = ADMIN_URL
        response = requests.get(URL,
                                headers=admin_headers)
        log(URL, admin_headers, response.text)
        assert len(response.json()) > 0

        ###################################################################
        _l('''List of tagged items for users''')
        for i in range(0, 2):
            response = requests.get(ADMIN_URL+
                                    '?user=' + users[i]['name'],
                                    headers=admin_headers)
            logging.debug('user:{}\nitems:{}\n'.format(users[i]['name'], response.text))
            assert json.loads('["test_tag1_{}","test_tag2_{}","test_tag3_{}"]'.format(i,i,i)) == \
                sorted([e['tag'] for e in response.json()])

        ###################################################################
        _l('''Snapshots for the tag''')
        URL =  ADMIN_URL + '?tag_name=test_tag1_0'
        response = requests.get(URL,
                                headers=admin_headers)
        log(URL, admin_headers, response.text)
        assert len(response.json()) == 1 and response.json()[0]['tag'] == 'test_tag1_0'

        ###################################################################
        _l('''Get the snapshot of a label''')
        URL = ADMIN_URL + '?tag_contains=test_tag'
        response = requests.get(URL,
                                headers=admin_headers)
        log(URL, admin_headers, response.text)
        assert len(response.json()) == 6

        ###################################################################


        for i in range(0, 2):

            repo_id = users[i]['repo_id']

            ###################################################################
            logging.debug('''Labeled items for repo''')
            URL = ADMIN_URL+'?repo_id='+repo_id
            response = requests.get(URL,
                                    headers=admin_headers)

            log(URL, admin_headers, response.text, )
            assert len(response.json()) == 3

            ###################################################################
            logging.debug('''Labeled items for repo by label''')
            for j in range(1, 3):
                tag_name = 'test_tag{}_{}'.format(j, i)
                response = requests.get(ADMIN_URL +
                                        '?repo_id={}&tag_name={}'.format(repo_id, tag_name),
                                        headers=admin_headers)
                logging.debug('repo:{}\ntag_name={}\nitems:{}'.format(repo_id, tag_name, response.text))
                assert len(response.json())==1 and response.json()[0]['tag'] == tag_name

            ###################################################################
            logging.debug('''Labeled items by label contains''')
            response = requests.get(ADMIN_URL +
                                    '?repo_id='+repo_id+'&tag_contains=test_',
                                    headers=admin_headers)
            logging.debug('repo:{}\ntag_contains=test_\nitems:{}'.format(repo_id, response.text))
            assert len(response.json()) == 3


        ###################################################################
        logging.debug('''List of labels, where label contains "test_"''')
        response = requests.get(ADMIN_URL+
                                '?tag_contains=test_',
                                headers=admin_headers)
        logging.debug('\n{}'.format(response.text))
        # TODO: NOT IMPLEMENTED
        # assert len(response.json()) == 6
        logging.debug(response)



        ### USER
        #####################################################################################
        headers = users[0]['headers']
        repo_id = users[0]['repo_id']

        #####################################################################################
        _l('''Get the snapshot labels of the current user {} '''.format(users[0]['name']))
        URL = BASE_URL+'/api/v2.1/revision-tags/tag-names/'
        response = requests.get(URL,
                                headers=headers)
        assert len(response.json()) == 3
        log(URL, headers, response.text)


        #####################################################################################
        logging.debug('''Get the snapshots for labels''')
        response = requests.get(BASE_URL+'/api/v2.1/revision-tags/tagged-items/',
                                data={'repo_id':repo_id,'tag_names':'test_tag1_0'},
                                headers=headers)
        logging.debug(response.text)


        #####################################################################################
        _l('''Update Snapshot Label''')
        #get commit
        response = requests.get(ADMIN_URL +
                                '?repo_id={}&tag_name=test_tag1_0'.format(repo_id),
                                 headers=admin_headers)
        commit_id = response.json()[0]['revision']['commit_id']

        #update
        response = requests.put(BASE_URL+'/api/v2.1/revision-tags/tagged-items/',
                                data={'repo_id':repo_id,'commit_id':commit_id,'tag_names':'test_tag1_0_updated'},
                                headers=headers)

        assert response.json()['revisionTags'][0]['tag'] == 'test_tag1_0_updated'
        _l(response.text, INFO)

        #####################################################################################
        _l('''Delete Snapshot Label''', INFO)
        URL = BASE_URL+'/api/v2.1/revision-tags/tagged-items/?repo_id={}&tag_name={}'.format(repo_id, 'test_tag1_0_updated')
        response = requests.delete(URL,
                                headers=headers)
        log(URL, headers, response.text, level=INFO)


        # response = requests.delete(BASE_URL + '/api2/repos/' + repo_id + '/', headers=headers)

        # TODO: !!!! BUG: tag will not be deleted if repo is deleted!
        # Thus, there is no way to delete tags

    # clean up users
    finally:
        for u in users:
            next(u['gen'])




