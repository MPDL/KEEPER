from django import template
from django.utils.html import escape
from django.utils.encoding import force_unicode
import json

register = template.Library()

@register.filter(name='get_value_from_json')
def get_value_from_json(value, key):
    """
    get value by key from json string
    """
    json_dict = json.loads(value)
    result = ''
    if key in json_dict:
        result = force_unicode(escape(json_dict[key]))
    return result

@register.simple_tag
def json_to_var(json_str):
    """
    convert json string to variable
    """
    json_var = {}
    try:
        json_var = json.loads(json_str)
    except:
        pass
    return json_var
