#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import hashlib
import random
import cookielib

from twisted.web.client import Agent, CookieAgent
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.http_headers import Headers
from twisted.internet.ssl import ClientContextFactory

from twidibot import config
from twidibot.logger import log
from twidibot.helpers import round_float_to_int


class SimpleDataHolder(object):
  """A simple object that has the 'data' attribute.

  It may have additional attributes set to it by the
  ``ChallengeResponseSystem``.
  """

  def __init__(self):
    self.data = None

class ChallengeDataHolder(SimpleDataHolder):
  pass

class ResponseDataHolder(SimpleDataHolder):
  pass


class ChallengeResponse(object):
  """Base/abstract class for a challenge-response test for a distributor"""

  def __init__(self, user_handle, user_data):
    # don't store any user data here if there's no need for it.
    # if we do end up storing something here, it's a good idea
    # to wipe it out later, so that data does not get persisted to any storage
    # in any way.

    # XXX consider making this class be completely virtual?
    self._challenge = ChallengeDataHolder()
    self._response = ResponseDataHolder()

  def getChallenge(self):
    return self._challenge

  def getResponse(self):
    return self._response


class ChallengeResponseSystem(object):
  """A base class that takes care of challenge-responses"""

  STORE_RESPONSES_HASHED = False # children should override this if they can
                                 # guarantee that response data objects are
                                 # hashable (they really should be, of course)

  CR_object_class = ChallengeResponse # base/abstract/stub CR class

  def __init__(self, user_challenges):
    """Initialize the CR controller.

    'user_challenges' is a container that has the attribute 'users', which is
    a map from hashed user handles to 'response' objects which hold
      * correct response (response object) to the last challenge to this user
      * timestamp when this challenge was generated

    In our intended use cases, all responses will be text-based; hence we can
    store and compare responses in hashed form.
    """

    self.user_challenges = user_challenges

  def generateChallengeForUser(self, user_handle, user_data):
    # we pass un unhashed user handle and user data (if any) to the CR
    # constructor; the idea is that some CR systems may make use of this
    # handle and/or additional data ("type in your screen name")
    cr = self.CR_object_class(user_handle, user_data)

    current_timestamp = self.getCurrentTimestamp()
    hashed_handle = self.hashUserHandle(user_handle)
    intended_response = cr.getResponse()
    if self.STORE_RESPONSES_HASHED:
      intended_response.data = self.hashResponse(intended_response.data)
    intended_response.timestamp = self.roundTimestamp(current_timestamp)

    # if there already was a CR generated for this user, naively overwrite it
    # with a new CR:
    self.user_challenges.users[hashed_handle] = intended_response

    return cr.getChallenge().data

  def userHasAChallenge(self, user_handle):
    hashed_handle = self.hashUserHandle(user_handle)
    return self.user_challenges.users.get(hashed_handle)

  def checkUserAnswer(self, user_handle, answer):
    current_timestamp = self.getCurrentTimestamp()
    hashed_handle = self.hashUserHandle(user_handle)
    intended_response = self.user_challenges.users.get(hashed_handle)

    if not intended_response:
      return False # do not say why check failed (leak information only
                   # indirectly, via not-completely-constant-time dictionary
                   # lookups)

    if self.STORE_RESPONSES_HASHED:
      answer = self.hashResponse(answer)

    if intended_response.data != answer: # XXX do constant-time compare maybe?
      return False

    return (intended_response.timestamp + \
        config.CHALLENGE_RESPONSE_EXPIRY_TIME >= current_timestamp)

  @staticmethod
  def hashUserHandle(user_handle):
    """Do a one-way hash of Twitter user handle."""

    # we should probably move functions such as this to ``helpers``

    # XXX sha256? sha512? configurable at a higher level?
    return hashlib.sha1(user_handle).hexdigest()

  @staticmethod
  def hashResponse(response_data):
    """Do a one-way hash of the response data object.

    Assumes the response data object is hashable.
    """

    return hashlib.sha1(response_data).hexdigest()

  @staticmethod
  def roundTimestamp(timestamp):
    return round_float_to_int(timestamp)

  @staticmethod
  def getCurrentTimestamp():
    return time.time()


class WebClientContextFactory(ClientContextFactory):
  """Context factory for Twisted SSL.

  TODO use isis' certificate checking code here.
  """

  def getContext(self, hostname, port):
    return ClientContextFactory.getContext(self)


class ResponseBodyHolder(Protocol):
  """Holds a response body of a Twisted request."""

  def __init__(self, deferred, callback):
    self.body = None
    self.deferred = deferred
    self.callback = callback

  def dataReceived(self, bReceived):
    if not self.body:
      self.body = bReceived
    else:
      self.body += bReceived
    if self.callback:
      self.callback(bReceived)

  def connectionLost(self, reason):
    self.deferred.callback(None)


class TwitterReactorChallengeResponse(ChallengeResponse):
  def __init__(self, user_handle, user_data):
    self._challenge = ChallengeDataHolder()
    self._response = ResponseDataHolder()

    #self._deferreds = list()
    self._deferred = None
    self._cookieJar = cookiejar.CookieJar() # we'll use the same jar for all
                                            # requests
    self._contextFactory = WebClientContextFactory()
    self._pool = HTTPConnectionPool(reactor)

    # make ourselves a web agent which also handles cookies and does
    # persistent connections:
    self._agent = CookieAgent(
        Agent(reactor, self._contextFactory, pool=self._pool),
        self._cookieJar)

    #self.requestPOST("https://...", ...)

  def getChallenge(self):
    #deferred = self.requestGET("https://...")
    # extract challenge, store in self._challenge
    pass

  def getResponse(self):
    pass

  def requestGET(self, url):
    #self._deferreds.append(self._agent.request("GET", url))
    self._deferred = self._agent.request("GET", url)
    self._deferred.addCallback(self.doneRequest)
    return self._deferred

  def doneRequest(self, response):
    finished = Deferred()
    response.deliverBody(ResponseBodyHolder(finished, self.someDataReceved))

  def someDataReceived(self, bReceived):
    pass # we probably don't want to look at data until response is complete


number_units = ("zero", "one", "two", "three", "four", "five", "six", "seven",
                "eight", "nine", "ten", "eleven", "twelve", "thirteen",
                "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
                "nineteen")

class BogusTextBasedChallengeResponse(ChallengeResponse):
  def __init__(self, user_handle, user_data):
    self._challenge = ChallengeDataHolder()
    self._response = ResponseDataHolder()

    str_number = random.choice(number_units)
    number = number_units.index(str_number)
    total_number = len(user_handle) + number

    # in text-based CR, challenge data is just a string => things are easy:
    self._challenge.data = "Reply with a number which is the number of " \
        "characters in your username (without the \"@\"), plus %s. e.g., " \
        "\"25\" (without the quotes.)" % str_number # max length: 138

    self._response.data = str(total_number) # make sure later comparisons are
                                            # between the same data types

    #log.debug("Screen name is \"%s\", len is %d, number is %d.", user_handle,
    #    len(user_handle), number)


class BogusTextBasedChallengeResponseSystem(ChallengeResponseSystem):
  """A mostly-stub text-based CR system for testing things.

  Actual text generation etc. happens at the ``ChallengeResponse`` child
  object level, so we don't need to change much here.
  """

  STORE_RESPONSES_HASHED = True
  CR_object_class = BogusTextBasedChallengeResponse


class TwitterReactorBasedChallengeResponseSystem(ChallengeResponseSystem):
  """CR system that uses Twisted-reactor-based flow to get/deliver C/R over
  twisted.web requests.
  """

  STORE_RESPONSES_HASHED = True
  CR_object_class = TwitterReactorChallengeResponse


if __name__ == '__main__':
  pass
