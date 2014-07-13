#!/usr/bin/env python
# -*- coding: utf-8 -*-

# DEFAULT_IS_PRODUCTION == False => development environment by default
DEFAULT_IS_PRODUCTION = False

import os
import logging

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)


class Config(object):
  """General config with general config settings"""

  KNOWN_PT_TYPES = ('obfs3', 'scramblesuit', 'fte')
  CHARACTER_LIMIT = 139
  UNFOLLOW_AFTER_GIVING_BRIDGES = True

  LOG_FILE = dir_path + '/../logs/main.log'  # consider separate logs for
                                             # debug/info/error, etc.?
  LOG_TO_CONSOLE_TOO = True

  ASYNC_STREAMING_API = False   # get Streaming API events asynchronously
                                # (tweepy does this by running a separate
                                # thread with a loop)

  RESPOND_AFTER_FOLLOW = True   # send a message to user immediately after they
                                # start following us (do not wait for their
                                # msg.) after we start following someone, we

  WAIT_TIME_AFTER_FOLLOW = 1.0  # wait a # bit before performing actions that
                                # depend on us following them. (ideally, we
                                # check every WAIT_TIME_AFTER_FOLLOW seconds
                                # to make sure twitter reports us as following
                                # said user.

  DO_SINGLE_USER_CHURN_CONTROL = True
  NOTIFY_USERS_ABOUT_CHURN = True


class DevelopmentConfig(Config):
  """Development-specific configuration"""

  DEBUG = True

  LOG_LEVEL = logging.DEBUG
  SAFE_LOG = False

  API_KEY = ''  # <-- insert your test api key here
  API_SECRET = ''  # <-- insert your test api secret here
  # these two are for actual access to a particular twitter account:
  ACCESS_TOKEN = ''  # <-- insert your test access token here
  TOKEN_SECRET = ''  # <-- insert your test access token secret here

  MIN_REREQUEST_TIME = 60 # for a single user; seconds

  CHALLENGE_RESPONSE_EXPIRY_TIME = 60 # in seconds


class ProductionConfig(Config):
  """Production-specific configuration"""

  DEBUG = False

  LOG_LEVEL = logging.INFO
  SAFE_LOG = True

  API_KEY = ''
  API_SECRET = ''
  ACCESS_TOKEN = ''
  TOKEN_SECRET = ''

  MIN_REREQUEST_TIME = 600 # for a single user; seconds

  CHALLENGE_RESPONSE_EXPIRY_TIME = 60 # in seconds


