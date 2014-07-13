#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twidibot.bot_storage import PersistableStorageHandler


class TwitterBotState(object):
  """Separate component holding bot-user-interaction state.

  We don't want to persist any additional class instance methods, so we
  keep it minimal: the actual persistable data is contained in
  ``PersistableStorageContainer``s, handled by ``PersistableStorageHandler``s.

  This state includes:

    * a dictionary of hashed Twitter screen names mapping hashed names to the
      timestamp when the user was last given bridges.

    * a dictionary of hashed Twitter screen names mapping hashed names to
      answers to challenge-responses (response objects including an answer and
      a timestamp when the answer challenge was generated.)

  Bot state may have multiple "containers" attached per storage handler,
  as well as multiple, different storage handlers (all managed by a central
  controller.) Some handlers may handle non-persistable state/data, etc.
  """

  def __init__(self, storage_controller):
    main_handler = PersistableStorageHandler()
    self.user_access_times = main_handler.addContainer(
        "user_access_times", users=dict())

    # XXX consider putting the user C-Rs into an ephemeral container (which
    # XXX could e.g. make sure everything is wiped when handler is closed)
    # i.e., we may not even want to persist C-Rs; let me them expire if the
    # program needs to shut down.
    self.user_challenges = main_handler.addContainer(
        "user_challenges", users=dict())

    storage_controller.addHandler(main_handler)


if __name__ == '__main__':
  pass
