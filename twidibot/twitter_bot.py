#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Proof of concept twitter bot for a new BridgeDB distributor.

This is supposed to be a working PoC bot, but that is all.
Not yet clear on file organization, etc.
Eventually all this should become a part of a subclassed
bridgedb.Distributor. Or a client of a generic distributor-service
(RESTful BridgeDB api?) Or not. Many things may change.

Current plan is to use bridge-getter, and to subclass bridge-getter in a way
that makes the most amount of sense (e.g. bridge-getter as RESTful api's
client, or bridge-getter as subclassed bridgedb.Distributor (the latter is
the easiest way to fulfil main deliverable, but we should also think ahead.))
"""

import sys
import json
import time
from pprint import pprint

import tweepy
from tweepy.models import Status

from twidibot import config, bridge_getter
from twidibot.logger import log

def stub_log(level, fmt, *args):
  """TODO: use python logger to actually log things.

  Will probably log to stdout/stderr and file by default.

  Lazy placeholder.
  Remove later.
  """

  print '[log placeholder]: [%s]' % level, fmt % args

class TwitterBotStreamListener(tweepy.StreamListener):
  """Listener for twitter's Streaming API."""

  def __init__(self, bot, api=None):
    self.bot = bot

    # do we need to do anything else here?

    super(TwitterBotStreamListener, self).__init__(api)

  def on_data(self, raw_data):
    """Called when raw data is received from connection.

    This is where all the data comes first. Normally we could use (inherit)
    the on_data() in tweepy.StreamListener, but it unnecessarily and naively
    reports unknown event types as errors (to simple log); also, we might want
    to tweak it further later on.

    But for now, this is basically taken from tweepy's on_data().

    Return False to stop stream and close connection.
    """

    data = json.loads(raw_data)

    if 'in_reply_to_status_id' in data:
      status = Status.parse(self.api, data)
      if self.on_status(status) is False:
        return False
    elif 'delete' in data:
      delete = data['delete']['status']
      if self.on_delete(delete['id'], delete['user_id']) is False:
        return False
    elif 'event' in data:
      status = Status.parse(self.api, data)
      if self.on_event(status) is False:
        return False
    elif 'direct_message' in data:
      status = Status.parse(self.api, data)
      if self.on_direct_message(status) is False:
        return False
    elif 'limit' in data:
      if self.on_limit(data['limit']['track']) is False:
        return False
    elif 'disconnect' in data:
      if self.on_disconnect(data['disconnect']) is False:
        return False
    else:
      # we really are ok to receive unknown stream/event types.
      # log to debug?
      log.debug('TwitterBotStreamListener::on_data(): got event/stream data of'
          ' unknown type. Raw data follows:\n%s', data)

  def on_status(self, status):
    """Called when a new status arrives"""

    #log.debug('Got status: %s', status)
    return

  def on_event(self, status):
    """Called when a new event arrives"""

    #log.debug('Got event: %s', status)

    if str(status.event) == 'follow': # XXX make sure tweepy's given
                                      # 'status.event' unicode string can
                                      # always be safely converted to ascii.
      self.bot.handleFollowEvent(status)
    return

  def on_direct_message(self, status):
    """Called when a new direct message arrives or is sent from us

    TODO: make a pull request for tweepy or something, because they say it's
    only when a direct message is *received* (implying, 'by us.')
    """

    # doing twitter user comparisons using id_str makes sense here - it's safe
    # and id_str's are guaranteed to be unique (re: latter, just like id's.)
    # maybe consider deciding how comparisons should be made for sure,
    # and then extend tweepy.models.User to include __eq__?
    if status.direct_message['sender']['id_str'] != self.bot.bot_info.id_str:
      self.bot.handleDirectMessage(status)
    else:
      #log.debug('Caught a direct message sent *from* us')
      pass

    return

  def on_connect(self):
    """Called once connected to streaming server.

    This will be invoked once a successful response
    is received from the server. Allows the listener
    to perform some work prior to entering the read loop.
    """
    pass

  def on_exception(self, exception):
    """Called when an unhandled exception occurs."""
    return

  def on_delete(self, status_id, user_id):
    """Called when a delete notice arrives for a status"""
    return

  def on_limit(self, track):
    """Called when a limitation notice arrvies"""
    return

  def on_error(self, status_code):
    """Called when a non-200 status code is returned"""
    return False

  def on_timeout(self):
    """Called when stream connection times out"""
    return

  def on_disconnect(self, notice):
    """Called when twitter sends a disconnect notice

    Disconnect codes are listed here:
    https://dev.twitter.com/docs/streaming-apis/messages#Disconnect_messages_disconnect
    """
    return

class TwitterBotState(object):
  """Separate component holding bot-user-interaction state.

  Have this be isolated from the rest, because we may want to be able to
  pickle it / persist it one way or another, and so on. Isolation makes sense.

  XXX Write this in a way that treats all data herein as sensitive.
      (i.e. at the very least think this over carefully.)
  XXX Consider implementing proper getters/setters for this, etc etc.

  This will probably be just a placeholder for now.
  """

  def __init__(self):
    # TODO: merge dirty dirty branch involving user state,
    # *or* discard it & possibly get rid of even this.

    self.users = dict()

class TwitterBot(object):
  """Main interface between the stateful listener and Twitter APIs.

  TODO: write docstrings; or just move on with actual non-PoC bot development.
  """

  # TODO: think about secure ways of storing twitter access config.
  # For one, app itself should ideally not be able to have write access to it.
  # For another, ideally it would request details from some other component,
  # authenticate, and not be able to re-authenticate to twitter.
  default_access_config = {
    'api_key': config.API_KEY,
    'api_secret': config.API_SECRET,
    'access_token': config.ACCESS_TOKEN,
    'token_secret': config.TOKEN_SECRET
  }

  def __init__(self, **kw):
    """Constructor that accepts custom access config as named arguments.

    Easy to test things from interactive shell this way.
    Probably won't be needed in production code.
    """

    self.access_config = dict()
    for key, default in self.default_access_config.iteritems():
      self.access_config[key] = kw.get(key, default)

    self.state = TwitterBotState()

    # additional auth (or hashring handover from bridgedb.Distributor)
    # will likely be needed here, etc.:
    self.bridge_getter = bridge_getter.TwitterBotBridgeGetter(
        known_pt_types=config.KNOWN_PT_TYPES)

  def authenticate(self, auth=None):
    """Authenticate to Twitter API, get API handle, and remember it."""

    if auth:
      self.auth = auth
    else:
      self.auth = tweepy.OAuthHandler(
          self.access_config['api_key'],
          self.access_config['api_secret'])
      self.auth.set_access_token(
          self.access_config['access_token'],
          self.access_config['token_secret'])

    try:
      self.api = tweepy.API(self.auth)
    except Exception as e:
      log.fatal('Exception while authenticating to Twitter and getting API '
          'handle: %s', e)
      self.api = None
    finally:
      #del self.auth # ideally we'd be able to delete this, but presently - no
      # anything?
      pass

    if self.api:
      log.info('Authenticated to Twitter and got the RESTful API handle')
      self.bot_info = self.api.me()
      #api.update_status('hello world!') # push a mighty status update

  def subscribeToStreams(self):
    """Subscribe to relevant streams in the Streaming API."""

    self.listener = TwitterBotStreamListener(bot=self, api=self.api)
    self.stream = tweepy.Stream(self.auth, self.listener)

    # user stream gives us direct messages and follow events
    self.stream.userstream(async=config.ASYNC_STREAMING_API)
    # stream.filter may be useful, but we don't need it for now

    # the following will not be executed if we're not going async -
    # userstream() blocks, its event handler loop takes over:
    log.info('Subscribed to relevant streams via Streaming API')

  def handleFollowEvent(self, event):
    user_id = event.source['id'] # 'id' is unique big int

    if user_id != self.bot_info.id:
      user = self.api.get_user(id=user_id)
      user.follow()

    if config.RESPOND_AFTER_FOLLOW:
      # the following line *blocks* the thread that we care about.
      # we should not do this, ever.
      # as long as we're just testing with a few cat accounts, it's ok.
      time.sleep(config.WAIT_TIME_AFTER_FOLLOW) # TODO: use sched.scheduler,
                                                # or threading.Timer (or sth.)

      # previously we just sent some bridges automatically, but now we send
      # an informative message instead. I guess this is good, but maybe it'd
      # be nice for a user to receive bridges just by clicking 'follow.'

      #str_bridges = self.bridge_getter.getBridges(user_id, event.source)
      self.sendMessage(user_id, 'Hello! Say: "get bridges". If you want '
          'pluggable transport bridges, include the PT name (e.g. "obfs3"), '
          'too.')

  def handleDirectMessage(self, status):
    sender_id = status.direct_message['sender_id']
    message = status.direct_message['text'].strip().lower()

    if not ('get' in message and 'bridges' in message): # this is.. overly
      self.sendMessage(sender_id, 'Send a direct '      # simplistic, maybe
          'message with the words "get bridges" somewhere in it.')
      return False

    transports = []
    for pt in config.KNOWN_PT_TYPES:
      if pt in message and pt not in transports:
        transports.append(pt)
    if not transports and len(message) > len('get bridges'):
      self.sendMessage(sender_id, 'Here is a list of transports I know '
          'about: %s' % ', '.join(config.KNOWN_PT_TYPES))
      # should we do this? (below)
      self.sendMessage(sender_id, 'You might have tried specifying a '
          'transport I do not support. Sending you non-PT bridges anyway.')

    str_bridges = self.bridge_getter.getBridges(sender_id,
        status.direct_message['sender'], transports)
    if str_bridges:
      result = self.sendMessage(sender_id, str_bridges)
      if result and config.UNFOLLOW_AFTER_GIVING_BRIDGES:
        self.sendMessage(sender_id, 'For your safety, I will now unfollow '
            'you. You should unfollow me, too. If you then want bridges '
            'once more, just start following me again.')
        self.api.get_user(id=sender_id).unfollow()

    else:
      # XXX this is neither DEBUG, nor safe to log. this is PoC stuff.
      # TODO: an actual scrubbing function which uses config.SAFE_LOG
      log.debug('Have no bridge data to give to %s',
          status.direct_message.sender_screen_name)

  def sendMessage(self, target_id, message):
    # this is quick and ugly. primary splits (if needed) at newlines.
    try:
      cur_message = ''
      for line in message.split('\n'):
        if len(cur_message + ('\n' if cur_message else '') + line)\
            > config.CHARACTER_LIMIT:
          self._split_in_chunks_and_send(target_id, cur_message)
          cur_message = ''
        else:
          cur_message += ('\n' if cur_message else '') + line
      if cur_message:
        self._split_in_chunks_and_send(target_id, cur_message)
    except Exception as e:
      # again, scrubbing 'target_id' should be an option, etc.
      log.warning('Failed to send a direct message to %s. Exception:\n%s',
          str(target_id), e)
      return False
    return True

  def _split_in_chunks_and_send(self, target_id, message):
    # assume any decent humane splitting has been done beforehand.
    # we have to do with what we have here.
    # exception handling at higher call stack.

    while message:
      self.api.send_direct_message(user_id=target_id,
          text=message[:config.CHARACTER_LIMIT])
      message = message[config.CHARACTER_LIMIT:]

  def followAllFollowers(self):
    """Start following everyone who is following us."""

    for follower in tweepy.Cursor(self.api.followers).items():
      follower.follow()

  def unfollowAllFollowers(self):
    """Unfollow everyone who is following us."""

    for follower in tweepy.Cursor(self.api.followers).items():
      follower.unfollow()


def main(argv):
  pass


if __name__ == '__main__':
  main(sys.argv)
