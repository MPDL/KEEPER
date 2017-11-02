# -*- coding: utf-8 -*-
import pytest
import tempfile
import json
from uuid import uuid4

# from rest_framework.test import APIClient

import requests
import tempfile

from seahub.settings import TEST_SERVER, TEST_SERVER_ADMIN, TEST_SERVER_PASSWORD

BASE_URL=TEST_SERVER

def get_headers(username, password):
    response = requests.post(BASE_URL + '/api2/auth-token/',
                             data={'username':username,'password':password} )
    return {'Authorization':'Token ' + response.json()['token'],
            'Accept':'application/json; indent=4'}




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
            print("\nNew user:{}\n".format(users[i]))

            response = requests.post(BASE_URL + '/api2/repos/',
                                    data={'name':'test_snap_labels_repo_{}'.format(i)}, headers=headers)
            repo_id = response.json()['repo_id']
            users[i]['repo_id'] = repo_id
            # print(repo_id)

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
            # READ labels by snapshot
            response = requests.get(BASE_URL+'/api/v2.1/revision-tags/tag-names/',
                                    data={'repo_id':repo_id,'commit_id':commit_id},
                                    headers=headers)

            # TODO: NOT IMPLEMENTED. Should it be????
            #assert json.loads(response.text) == json.loads('["test_tag2_{}","test_tag3_{}"]'.format(i, i))
            print(response.text)

            # response = requests.get(BASE_URL+'/api/v2.1/repos/'+repo_id+'/history/',
                                    # headers=headers)
            # print(response.text)

        #####################################################################################
        # ADMIN
        # Get Snapshots by Label


        ADMIN_URL = BASE_URL + '/api/v2.1/admin/revision-tags/tagged-items/'

        ###################################################################
        print('''List of labels for all users with corresponding snapshots''')
        response = requests.get(ADMIN_URL,
                                headers=admin_headers)
        # TODO: NOT IMPLEMENTED
        # https://keeper.mpdl.mpg.de/lib/a0b4567a-8f72-4680-8a76-6100b6ebbc3e/file/Seafile/Development/Snapshot%20Labels/offer_snapshot_labels.pdf
        print(response.text)


        ###################################################################
        print('''List of tagged items for users''')
        for i in range(0, 2):
            response = requests.get(ADMIN_URL+
                                    '?user=' + users[i]['name'],
                                    headers=admin_headers)
            print('user:{}\nitems:{}\n'.format(users[i]['name'], response.text))
            assert json.loads('["test_tag1_{}","test_tag2_{}","test_tag3_{}"]'.format(i,i,i)) == \
                sorted([e['tag'] for e in response.json()])
        ###################################################################

        print('''Snapshots for the tag''')
        response = requests.get(ADMIN_URL+
                                '?tag_name=test_tag1_0',
                                headers=admin_headers)
        # TODO: NOT IMPLEMENTED
        print(response.text)

        ###################################################################


        for i in range(0, 2):

            repo_id = users[i]['repo_id']

            ###################################################################
            print('''Labeled items for repo''')
            response = requests.get(ADMIN_URL+
                                    '?repo_id='+repo_id,
                                    headers=admin_headers)

            print('repo:{}\nitems:{}'.format(repo_id, response.text))
            assert len(response.json()) == 3

            ###################################################################

            print('''Labeled items for repo by label''')

            for j in range(1, 3):
                tag_name = 'test_tag{}_{}'.format(j, i)
                response = requests.get(ADMIN_URL +
                                        '?repo_id={}&tag_name={}'.format(repo_id, tag_name),
                                        headers=admin_headers)
                print('repo:{}\ntag_name={}\nitems:{}'.format(repo_id, tag_name, response.text))
                assert len(response.json())==1 and response.json()[0]['tag'] == tag_name

            ###################################################################

            print('''Labeled items by label contains''')
            response = requests.get(ADMIN_URL +
                                    '?repo_id='+repo_id+'&tag_contains=test_',
                                    headers=admin_headers)
            print('repo:{}\ntag_contains=test_\nitems:{}'.format(repo_id, response.text))
            assert len(response.json()) == 3



        ###################################################################
        print('''List of labels, where label contains "test_"''')
        response = requests.get(ADMIN_URL+
                                '?tag_contains=test_',
                                headers=admin_headers)
        print('\n{}'.format(response.text))
        # TODO: NOT IMPLEMENTED
        # assert len(response.json()) == 6
        print(response)



        ### USER
        #####################################################################################
        headers = users[0]['headers']
        repo_id = users[0]['repo_id']

        #####################################################################################
        print('''Get the snapshot labels of the current user''')
        response = requests.get(BASE_URL+'/api/v2.1/revision-tags/tag-names/',
                                headers=headers)
        assert len(response.json()) == 3
        print(response.text)


        #####################################################################################
        print('''Get the snapshots for labels''')
        response = requests.get(BASE_URL+'/api/v2.1/revision-tags/tagged-items/',
                                data={'repo_id':repo_id,'tag_names':'test_tag1_0'},
                                headers=headers)
        print(response.text)



        #####################################################################################
        print('''Update Snapshot Label''')
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
        print(response.text)
        #####################################################################################



        # Delete Snapshot Label
        response = requests.delete(BASE_URL+'/api/v2.1/revision-tags/tagged-items/',
                                data={'repo_id':repo_id,'tag_names':'test_tag1_0_updated'},
                                headers=headers)
        # TODO: NOT IMPLEMENTED
        print(response.text)





        # response = requests.delete(BASE_URL + '/api2/repos/' + repo_id + '/', headers=headers)

        # TODO: !!!! BUG: tag will not be deleted if repo is deleted!
        # Thus, there is no way to delete tags

        # clean up users
    finally:
        for u in users:
            next(u['gen'])



