# coding: utf-8

import os
import logging
from configparser import ConfigParser
from seafevents.db import init_db_session_class
from seafevents.app.config import appconfig
from seafevents.utils.config import get_opt_from_conf_or_env, parse_bool

logger = logging.getLogger('virus_scan')
logger.setLevel(logging.INFO)


class Settings(object):
    def __init__(self, config_file):
        self.enable_scan = False
        self.scan_cmd = None
        self.vir_codes = None
        self.nonvir_codes = None
        self.scan_interval = 60
        # default 20M
        self.scan_size_limit = 20
        self.scan_skip_ext = ['.bmp', '.gif', '.ico', '.png', '.jpg',
                              '.mp3', '.mp4', '.wav', '.avi', '.rmvb',
                              '.mkv']
        self.threads = 4

        self.seahub_dir = None
        self.enable_send_mail = False

        self.session_cls = None
        self.seaf_session_cls = None

        self.parse_config(config_file)

    def parse_config(self, config_file):
        try:
            cfg = ConfigParser()
            seaf_conf = appconfig.seaf_conf_path
            cfg.read(seaf_conf)
        except Exception as e:
            logger.error('Failed to read seafile config, disable virus scan: %s', e)
            return

        if not self.parse_scan_config(cfg, seaf_conf):
            return

        try:
            self.session_cls = appconfig.session_cls
            self.seaf_session_cls = appconfig.seaf_session_cls
        except Exception as e:
            logger.warning('Failed to init db session class: %s', e)
            return

        self.enable_scan = True

        self.parse_send_mail_config(config_file)

    def parse_scan_config(self, cfg, seaf_conf):
        if cfg.has_option('virus_scan', 'scan_command'):
            self.scan_cmd = cfg.get('virus_scan', 'scan_command')
        if not self.scan_cmd:
            logger.info('[virus_scan] scan_command option is not found in %s, disable virus scan.' %
                        seaf_conf)
            return False

        vcode = None
        if cfg.has_option('virus_scan', 'virus_code'):
            vcode = cfg.get('virus_scan', 'virus_code')
        if not vcode:
            logger.info('virus_code is not set, disable virus scan.')
            return False

        nvcode = None
        if cfg.has_option('virus_scan', 'nonvirus_code'):
            nvcode = cfg.get('virus_scan', 'nonvirus_code')
        if not nvcode:
            logger.info('nonvirus_code is not set, disable virus scan.')
            return False

        vcodes = vcode.split(',')
        self.vir_codes = [code.strip() for code in vcodes if code]
        if len(self.vir_codes) == 0:
            logger.info('invalid virus_code format, disable virus scan.')
            return False

        nvcodes = nvcode.split(',')
        self.nonvir_codes = [code.strip() for code in nvcodes if code]
        if len(self.nonvir_codes) == 0:
            logger.info('invalid nonvirus_code format, disable virus scan.')
            return False

        if cfg.has_option('virus_scan', 'scan_interval'):
            try:
                self.scan_interval = cfg.getint('virus_scan', 'scan_interval')
            except ValueError:
                pass

        if cfg.has_option('virus_scan', 'scan_size_limit'):
            try:
                # in M unit
                self.scan_size_limit = cfg.getint('virus_scan', 'scan_size_limit')
            except ValueError:
                pass

        if cfg.has_option('virus_scan', 'scan_skip_ext'):
            exts = cfg.get('virus_scan', 'scan_skip_ext').split(',')
            # .jpg, .mp3, .mp4 format
            exts = [ext.strip() for ext in exts if ext]
            self.scan_skip_ext = [ext.lower() for ext in exts
                                  if len(ext) > 1 and ext[0] == '.']

        if cfg.has_option('virus_scan', 'threads'):
            try:
                self.threads = cfg.getint('virus_scan', 'threads')
            except ValueError:
                pass

        return True

    def parse_send_mail_config(self, config_file):
        cfg = ConfigParser()
        cfg.read(config_file)

        section_name = 'SEAHUB EMAIL'
        key_enabled = 'enabled'
        key_seahubdir = 'seahubdir'

        if not cfg.has_section(section_name):
            return

        enabled = get_opt_from_conf_or_env(cfg, section_name, key_enabled, default=False)
        enabled = parse_bool(enabled)
        if not enabled:
            return

        self.seahub_dir = get_opt_from_conf_or_env(cfg, section_name, key_seahubdir, 'SEAHUB_DIR')
        if not self.seahub_dir or not os.path.exists(self.seahub_dir):
            logger.info("SEAHUB_DIR is not set or doesn't exist, disable send email when find virus.")
        else:
            self.enable_send_mail = True

    def is_enabled(self):
        return self.enable_scan
