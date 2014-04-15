#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from config import DEFAULT_IS_PRODUCTION

if (os.environ.has_key('APP_MODE') and os.environ['APP_MODE'].lower() ==\
    'development') or not DEFAULT_IS_PRODUCTION:
  from config import DevelopmentConfig as config
else:
  from config import ProductionConfig as config
