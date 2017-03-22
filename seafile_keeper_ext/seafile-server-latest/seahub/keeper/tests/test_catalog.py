import pytest
import json
import time
# import cchardet


from keeper.catalog.catalog_manager import is_in_mpg_ip_range, get_catalog, \
        get_user_name, generate_catalog, clean_up_catalog

# @pytest.mark.skip
# def test_dummy():
    # pass

# @pytest.mark.skip
def test_is_in_mpg_ip_range():
    is_in_mpg = is_in_mpg_ip_range('192.129.78.1')
    assert is_in_mpg == False

# @pytest.mark.skip
def test_catalog():
    """Test catalog generation
    """
    start_time = time.time()
    catalog = get_catalog()
    print "--- %s seconds ---" % (time.time() - start_time)
    # for r in catalog:
        # if 'owner_name' in r and  'Vlad' in r['owner_name']:
            # print r
            # print json.dumps(r, indent=4, ensure_ascii = False, sort_keys=True, separators=(',', ': '))#.encode('utf8')
    # print json.dumps(catalog, ensure_ascii = False, indent=4, sort_keys=True, separators=(',', ': '))
    print "len:", len(catalog)


@pytest.mark.skip
def test_generate_catalog():
    """
        Test catalog generation
        Note: you prorbaly need to truncate keeper_catalog table
    """
    start_time = time.time()
    catalog = generate_catalog()
    print "--- %s seconds ---" % (time.time() - start_time)
    print json.dumps(catalog, ensure_ascii = False, indent=4, sort_keys=True, separators=(',', ': '))
    print "len:", len(catalog)

# @pytest.mark.skip
def test_clean_up_catalog():
    """
        Test catalog clean up
    """
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")

    import django
    django.setup()

    print "Deleted catalog entries: ", clean_up_catalog()






