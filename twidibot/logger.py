#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from twidibot import config

log = logging.getLogger('twidibot')

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s ')
log_file_handler = logging.FileHandler(config.LOG_FILE)
log_file_handler.setFormatter(log_formatter)
log.addHandler(log_file_handler)

if config.LOG_TO_CONSOLE_TOO:
  log_console_handler = logging.StreamHandler()
  log_console_handler.setFormatter(log_formatter)
  log.addHandler(log_console_handler)

log.setLevel(config.LOG_LEVEL)
