# -*- coding: utf-8 -*-

import logging
import re

from seahub.settings import ACCOUNT_ACTIVATION_PATTERN

def account_can_be_auto_activated(email):
    activate = False
    try:
        activation_pattern = re.compile(ACCOUNT_ACTIVATION_PATTERN)
        activate = re.match(activation_pattern, email)
    except Exception as e:
        logging.error("Cannot match pattern: %s" % e)

    return activate
