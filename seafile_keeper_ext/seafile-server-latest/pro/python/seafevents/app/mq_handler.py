import time
import logging
from threading import Thread, excepthook
import threading
import traceback
import sys

from seaserv import seafile_api

import seafevents.events.handlers as events_handlers
import seafevents.events_publisher.handlers as publisher_handlers
import seafevents.statistics.handlers as stats_handlers
from seafevents.db import init_db_session_class
from seafevents.app.event_redis import RedisClient

logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
k_log = logging.getLogger('keeper_debug')

__all__ = [
    'EventsHandler',
    'init_message_handlers'
]

# KEEPER: add exception hook on any Thread
def handle_thread_exception(args):
    exc_msg = traceback.format_exc()
    k_log.debug("Exception in thread %s: %s, %s, error: %s", args.thread.name, args.exc_type, args.exc_value, exc_msg)

threading.excepthook = handle_thread_exception


class MessageHandler(object):
    def __init__(self):
        # A (channel, List<handler>) map. For a given channel, there may be
        # multiple handlers
        self._handlers = {}

    def add_handler(self, msg_type, func):
        if msg_type in self._handlers:
            funcs = self._handlers[msg_type]
        else:
            funcs = []
            self._handlers[msg_type] = funcs

        if func not in funcs:
            funcs.append(func)

    def handle_message(self, config, session, redis_connection, channel, msg):
        pos = msg['content'].find('\t')
        if pos == -1:
            logger.warning("invalid message format: %s", msg)
            return

        msg_type = channel + ':' + msg['content'][:pos]
        if msg_type not in self._handlers:
            return

        funcs = self._handlers.get(msg_type)
        for func in funcs:
            try:
                if func.__name__ == 'RepoUpdatePublishHandler':
                    func(config, redis_connection, msg)
                else:
                    func(config, session, msg)
            except Exception as e:
                logger.exception("error when handle msg: %s", e)

    def get_channels(self):
        channels = set()
        for msg_type in self._handlers:
            pos = msg_type.find(':')
            channels.add(msg_type[:pos])

        return channels


message_handler = MessageHandler()


def init_message_handlers(config):
    if config.has_option('Audit', 'enabled'):
        try:
            enable_audit = config.getboolean('Audit', 'enabled')
        except ValueError:
            enable_audit = False
    elif config.has_option('AUDIT', 'enabled'):
        try:
            enable_audit = config.getboolean('AUDIT', 'enabled')
        except ValueError:
            enable_audit = False
    else:
        enable_audit = False

    events_handlers.register_handlers(message_handler, enable_audit)
    stats_handlers.register_handlers(message_handler)
    publisher_handlers.register_handlers(message_handler)


class EventsHandler(object):

    def __init__(self, config):
        self._config = config
        self._db_session_class = init_db_session_class(config)
        self._redis_connection = RedisClient(config).connection
        self._past_ts_dict =  {}
        self._counter = 0

    def handle_event(self, channel):
        config = self._config
        session = self._db_session_class()
        redis_connection = self._redis_connection
        try:
            k_log.debug('Starting handle_event thread for %s channel...', channel)
            while 1:
                try:
                    curr_ts = datetime.now()
                    if curr_ts - self._past_ts_dict[channel] >= timedelta(minutes=1):
                        k_log.debug('Channel %s thread is alive', channel)
                        self._past_ts_dict[channel] = curr_ts
                    msg = seafile_api.pop_event(channel)
                except Exception as e:
                    logger.error('Failed to get event: %s' % e)
                    k_log.debug('Failed to get event in channel %s: %s', channel, e)
                    time.sleep(3)
                    continue
                if channel == 'seaf_server.event':
                    k_log.debug('Counter: %s', self._counter)
                    # if self._counter == 3:
                    #     sys.exit(1)
                    # self._counter += 1
                if msg:
                    if channel == 'seaf_server.event':
                        k_log.debug(msg)
                    try:
                        message_handler.handle_message(config, session, redis_connection, channel, msg)
                    except Exception as e:
                        logger.error(e)
                        k_log.debug('Failed to handle_message in channel %s: %s', channel, e)
                    finally:
                        session.close()
                        if redis_connection:
                            redis_connection.close()
                else:
                    time.sleep(0.5)
                    
        except SystemExit as sa:
            raise Exception("Catched SystemExit exception", sa)
        finally:
            k_log.debug('Leaving channel %s thread...', channel)

    def start(self):
        channels = message_handler.get_channels()
        logger.info('Subscribe to channels: %s', channels)
        for channel in channels:
            self._past_ts_dict[channel] = datetime.now()
            event_handler = Thread(target=self.handle_event, name=channel, args=(channel, ))
            event_handler.start()
