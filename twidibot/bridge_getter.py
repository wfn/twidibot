#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A stub (-> PoC -> ?) for a bridge-getter for bridge distributors.

BridgeDB -> [?] -> bridge-getter -> gives bridges to particular distributor.
  => bridge-getter gives bridges to distributors, and is the distributor-side
  part of a semi-decentralized

    BridgeDB -> Core (e.g. RESTful) Distributor -> ..multiple distributors..

  chain (cf. current bridgedb.Distributor -> distributors inherit directly and
  are part of the main bridgedb codebase.) bridge-getter is to be part of
  every distributor's codebase (it's a 'client' in the eyes of core bridgedb
  and a 'giver' in the eyes of particular distributors), except for the core
  bridgedb.Distributor (or whatever becomes of it.)

Generic class ->
  -> child stub that
    -> just pretends to give 'bridge lines'/etc. for our bot
      -> [this early PoC uses this stub functionality]
    [later on..]
    -> gives fake descriptors
  [later on..]
  -> getter/consumer that simply inherits from bridgedb.Distributor
    -> simplest way to get the whole thing to actually do the job here
    -> clear way to end up with a working (twitter) bot
    -> but should provide enough abstraction to later on easily become..
  -> getter/consumer for a generic bridgedb RESTful distributor
    -> thus resulting in an architecture which supports
       'distributed distributors' that are isolated from core BridgeDB.
"""

class BridgeGetter(object):
  """A generic class for a bridge-getter that gets bridges from bridgedb.

  BridgeGetter gets bridges from bridgedb, and gives them to distributors
  that use BridgeGetter.

  There can be many ways of 'actually getting the bridges.' One of them is
  'pretend to get bridges, and just give test data to whoever is asking.'

  BridgeGetter should be subclassed by a particular bridge-getter mechanism.
  """
  pass

class BridgeGetterStub(BridgeGetter):
  """A bridge-getter that 'just gives something so we can run the thing.'

  This is not even intended to be good for mockups / unit testing / etc.
  As of now, this is not even.. something. It just gives strings.
  """

  def getBridges(self, user_id, **kw):
    return "Here's a string for %s, replace me with something better "\
        "please!" % str(user_id)

class TwitterBotBridgeGetter(BridgeGetterStub):
  """bridge-getter for the twitter bot distributor.

  Now: subclass from BridgeGetterStub.
  Later: either subclass from FakeBridgeGetter,
  or subclass from SomeActualBridgeGetter (that itself inherits from
  BridgeGetter.)
  """

  def __init__(self, known_pt_types):
    self.known_pt_types = known_pt_types

  def getBridges(self, user_id, user_info, transports):
    fake_string = ''
    for transport in transports:
      fake_string += 'some-%s-bridge\n' % transport
    for i in range(len(transports), 3): # everything is ugly here
      fake_string += 'some-bridge\n'
    return "Some bridges for you, %s:\n%s" % (user_info['name'], fake_string)

class FakeBridgeGetter(BridgeGetter):
  """A bridge-getter that 'gets' fake bridge descriptors, and gives them
  as if for real, to whoever's asking.
  """
  pass # XXX Either write this up, or implement the whole thing, and remove
       #     this (though it would probably be ideal for tests. Probably.)

if __name__ == '__main__':
  pass
