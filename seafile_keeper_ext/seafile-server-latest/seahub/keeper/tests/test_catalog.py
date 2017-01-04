import pytest
import json
# import cchardet


from keeper.catalog.catalog_manager import is_in_mpg_ip_range, get_catalog, get_user_name

# @pytest.mark.skip
# def test_dummy():
    # pass

def test_is_in_mpg_ip_range():
    is_in_mpg = is_in_mpg_ip_range('192.129.78.1')
    assert is_in_mpg == False

# @pytest.mark.skip
def test_catalog():
    """Test catalog generation
    """
    catalog = get_catalog()
    # for r in catalog:
        # if 'owner_name' in r and  'Vlad' in r['owner_name']:
            # print r
            # print json.dumps(r, indent=4, ensure_ascii = False, sort_keys=True, separators=(',', ': '))#.encode('utf8')
    print json.dumps(catalog, ensure_ascii = False, indent=4, sort_keys=True, separators=(',', ': '))




