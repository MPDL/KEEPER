#!/usr/bin/env python

from seaserv import seafile_api

from keeper.cdc.cdc_manager import generate_certificate

MAX_INT = 2147483647

err_list = []

###### START
repos_all = seafile_api.get_repo_list(0, MAX_INT)

# total amount of generated CDCs by the run
cdc_gen_amount = 0

for repo in repos_all:

    try:
        if generate_certificate(repo):
            cdc_gen_amount += 1
    except Exception as err:
        print err
        err_list.append({'name:':repo.name, 'id':repo.id, 'err':str(err)})

print "Amount of generated certificates:", cdc_gen_amount    

print "Errors:", err_list

#print('\n'.join(sys.path))

exit(0)
