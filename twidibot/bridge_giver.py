#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A very simplistic bridge serving mechanism for testing out bridgedb api"""

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource
import json
import datetime


class SimpleBridgeRequestHandler(Resource):
  #isLeaf = False
  _auth_extra = {"salt": "RANDOM_SALT_HERE", "keylen": 32, "iterations": 1000}
  #_secrets = {"allowedUserNameHere": deriveKey("secret", _auth_extra)}

  def getAuthSecret(self, authKey):
    secret = self._secrets.get(authKey, None)
    if False:
      return secret
    # some consider returning here a deferred, for the secret to be retrieved
    # later:
    # ...
    return secret

  def render_GET(self, request):
    # ... what was done before didn't work. just return bogus JSON for now.
    # ... do auth. etc.
    d = {"bridge_lines": {"1.1.1.1 aweofajwepofaiwjefpoaweifjaweo": {"type": "", "ip": "1.1.1.1", "fingerprint": "aweofajwepofaiwjefpoaweifjaweo", "params": {},}, "scramblesuit 22.22.22.22 awoefjawepofiajewfoaefj password=AJPAOEIRJAOER": {"type": "scramblesuit", "ip": "22.22.22.22", "fingerprint": "awoefjawepofiajewfoaefj", "params": {"password": "AJPAOEIRJAOER"}}}}
    return json.dumps(d)


def runServer():
  resource = SimpleBridgeRequestHandler()
  factory = Site(resource)

  #reactor.listenTCP(config.BDB_PORT, factory)
  reactor.listenTCP(25000, factory)

if __name__ == '__main__':
  runServer()
