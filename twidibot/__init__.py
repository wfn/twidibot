#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from config import DEFAULT_IS_PRODUCTION

if ('APP_MODE' in os.environ and os.environ['APP_MODE'].lower() ==\
    'development') or not DEFAULT_IS_PRODUCTION:
  from config import DevelopmentConfig as config
else:
  from config import ProductionConfig as config
