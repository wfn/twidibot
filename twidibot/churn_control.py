#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import time

from twidibot import config
from twidibot.helpers import round_float_to_int


class ChurnController(object):
  def __init__(self, access_times):
    """Initialize churn controller.

    'access_times' is a container that has the attribute 'users', which is a
    map from hashed user handles to timestamps. We don't care what kind of
    container it actually is (whether it gets persisted or not, etc.)
    """

    self.access_times = access_times

  @staticmethod
  def hashUserHandle(user_handle):
    """Do a one-way hash of Twitter user handle."""

    # XXX sha256? sha512? configurable at a higher level?
    return hashlib.sha1(user_handle).hexdigest()

  @staticmethod
  def roundTimestamp(timestamp):
    """Round timestamp of user bridge request to nearest integer."""

    # XXX is this needed? it is probably a good idea not to store precise
    # XXX timestamps if we do not need to. so let's not do that for now.
    return round_float_to_int(timestamp)

  def addOrUpdateUser(self, user_handle, timestamp):
    """Add or update timestamp for a user handle.

    The user handle is the user's Twitter screen name.
    Timestamp is in floating point form.

    We hash the user handle, and we round up the timestamp.

    If hashed user handle does not exist in hashset,
      add hashed handle => rounded timestamp to hashset.
    If hashed user handle does exist in hashset,
      update rounded timestamp for the hashed user handle;
      do not care if timestamp is smaller or bigger.
    """

    hashed_handle = self.hashUserHandle(user_handle)
    rounded_timestamp = self.roundTimestamp(timestamp)
    self.access_times.users[hashed_handle] = rounded_timestamp

  def removeOldUsers(self, removeBefore):
    """Remove old user handles that have timestamps < removeBefore."""

    old_users = list()
    for user, timestamp in self.access_times.users.iteritems():
      if timestamp < removeBefore:
        old_users.append(user)
    for old_user in old_users:
      del self.access_times.users[old_user]
    del old_users # for good measure (though, if we really cared about
                  # wiping / properly gc'ing sensitive data, we'd have to try
                  # harder than this.)

  def getTimestampForUser(self, user_handle):

    # re: dictionaries: note: https://wiki.python.org/moin/TimeComplexity
    # tl;dr: lookups tend to slow down (approach Amortized Worst Case)
    # as the hashset gets bigger. (i.e. O(1) -> O(n).)
    # => lookups are near-constant-time, but (1) not-exactly-constant,
    #    and (2) we may (very indirectly) leak current saved-user-set size.

    return self.access_times.users.get(self.hashUserHandle(user_handle))

  @staticmethod
  def getCurrentTimestamp():
    return time.time()

  def canGiveBridgesToUser(self, user_handle,
      expiry_time=config.MIN_REREQUEST_TIME):

    # do this before possibly returning early,
    # so the operation varies a bit less in time:
    current_timestamp = self.getCurrentTimestamp()

    last_timestamp = self.getTimestampForUser(user_handle)
    if last_timestamp is None:
      return True
    last_timestamp = float(last_timestamp) # do explicit cast so types match
    return (last_timestamp + expiry_time <= current_timestamp)


if __name__ == '__main__':
  pass
