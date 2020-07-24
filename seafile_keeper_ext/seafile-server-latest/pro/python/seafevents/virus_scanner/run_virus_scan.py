#!/usr/bin/env python
#coding: utf-8

import os
import sys
import logging
import argparse
from seafevents.virus_scanner.scan_settings import Settings
from seafevents.virus_scanner.virus_scan import VirusScan

from seafevents.app.config import load_config

if __name__ == "__main__":
    kw = {
        'format': '[%(asctime)s] [%(levelname)s] %(message)s',
        'datefmt': '%m/%d/%Y %H:%M:%S',
        'level': logging.DEBUG,
        'stream': sys.stdout
    }
    logging.basicConfig(**kw)

    from seafevents.virus_scanner.scan_settings import logger
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file',
                        default=os.path.join(os.path.abspath('..'), 'events.conf'),
                        help='seafevents config file')
    args = parser.parse_args()

    load_config(args.config_file)

    setting = Settings(args.config_file)
    if setting.is_enabled():
        VirusScan(setting).start()
    else:
        logger.info('Virus scan is disabled.')
