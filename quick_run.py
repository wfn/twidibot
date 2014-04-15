#!/usr/bin/env python
# -*- coding: utf-8 -*-

def quick_run():
  """Quick way of running the thing.

  Note that default right now is 'no async', which means, function won't
  return; on the other hand everything "will just work."

  If async is off, then we can:
  >>> from quick_run import quick_run
  >>> bot = quick_run() # authenticate, subscribe to streaming api, get handle
  """

  from twidibot.twitter_bot import TwitterBot

  bot = TwitterBot()
  bot.authenticate()
  #bot.api.update_status('yup!')
  bot.subscribeToStreams()

  return bot

if __name__ == '__main__':
  quick_run()
