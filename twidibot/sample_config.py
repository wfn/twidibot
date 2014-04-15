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
  CHARACTER_LIMIT = 140
  UNFOLLOW_AFTER_GIVING_BRIDGES = True

  LOG_FILE = dir_path + '/../logs/main.log' # consider separate logs for
                                            # debug/info/error, etc.?
  LOG_TO_CONSOLE_TOO = True

  ASYNC_STREAMING_API = False # get Streaming API events asynchronously
                              # (tweepy does this by running a separate thread
                              # with a loop)
  RESPOND_AFTER_FOLLOW = True # send a message to user immediately after they
                              # start following us (do not wait for their msg)

class DevelopmentConfig(Config):
  """Development-specific configuration"""

  DEBUG = True

  LOG_LEVEL = logging.DEBUG
  SAFE_LOG = False

  API_KEY = '' # <-- insert your test api key here
  API_SECRET = '' # <-- insert your test api secret here
  # these two are for actual access to a particular twitter account:
  ACCESS_TOKEN = '' # <-- insert your test access token here
  TOKEN_SECRET = '' # <-- insert your test access token secret here

class ProductionConfig(Config):
  """Production-specific configuration"""

  DEBUG = False

  LOG_LEVEL = logging.INFO
  SAFE_LOG = True

  API_KEY = ''
  API_SECRET = ''
  ACCESS_TOKEN = ''
  TOKEN_SECRET = ''
