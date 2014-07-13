#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from twidibot.logger import log
from twidibot.helpers import gpDump, gpLoad, round_float_to_int


class StorageController(object):
  """Generic controller that takes care of all strorage handlers."""

  def __init__(self, handlers=list()):
    self.handlers = handlers

  def addHandler(self, handler):
    self.handlers.append(handler)

  def closeAll(self):
    """To be called when all handlers need to be closed.

    Intended use case is overall program shutdown.
    """

    for handler in self.handlers:
      if not handler.close():
        log.warning("StorageController::closeAll(): skipping over "
            "handler %s because it failed to close cleanly. Look up log lines "
            "before this one for possible indications why that happened.",
            handler)


class StorageHandler(object):
  """Base class. Children take care of specific ``StorageContainer``s.

  Handlers for "ephemeral/volatile" containers may not need take care of
  closing them down. This is needed for persistent storage handlers, though.

  Children should minimally implement
    * attachContainer()
    * detachContainer()
    * close()
  """

  def __init__(self):
    self.containers = list()

  def attachContainer(self, container):
    """Attach a new container (e.g. a single-pickle-file-container)"""

    self.containers.append(container)

  def detachContainer(self, container):
    """Detach a particular container from handler"""

    matches = []
    for i, c in enumerate(self.containers):
      if c == container: # equivalence based on id()
        matches.append(i)
    for i in reversed(matches): # (in case of duplicates)
      self.containers.pop(i)
    # base ``StorageHandler`` doesn't care about the eventual fate
    # of its ``StorageContainer``s.

  def close(self):
    """Close down this whole handler"""

    not_clean = False
    # create a shallow copy of the list of containers: since we may be popping
    # them from the list as we are processing it, we need to do this.
    for container in list(self.containers):
      ret = self.detachContainer(container)
      if not ret:
        not_clean = True
    return not not_clean


class PersistableStorageHandler(StorageHandler):
  """Saves ``PersistableStorageContainer``s."""

  APPEND_CLASS_NAME = False
  APPEND_SUFFIX = True
  DEFAULT_SUFFIX = "state.gz"

  def __init__(self, storage_suffix=None):
    super(PersistableStorageHandler, self).__init__()

    if not storage_suffix and self.APPEND_SUFFIX:
      storage_suffix = self.DEFAULT_SUFFIX
    self.storage_suffix = storage_suffix

  def formatFilenameFor(self, container, name):
    filename = name + "%s%s" % (
        "." + container.__class__.__name__ if self.APPEND_CLASS_NAME else "",
        "." + self.storage_suffix if self.storage_suffix else "")
    return filename

  def loadContainer(self, container, name):
    """Try loading container data from storage.

    PersistableStorageContainer::loadContainer() method uses simple gzip +
    pickle load.
    """

    if not name:
      return False
    filename = self.formatFilenameFor(container, name)
    if not os.path.isfile(filename):
      return False

    try:
      loaded = gpLoad(filename)
      container.__dict__.update(loaded.__dict__)
    except:
      return False
    return True

  def saveContainer(self, container, name):
    """Try saving container data into persistent storage.

    PersistableStorageContainer::saveContainer() method uses simple gzip +
    pickle dump.
    """

    if not name:
      return False
    filename = self.formatFilenameFor(container, name)

    try:
      gpDump(container, filename)
    except Exception as e:
      log.warning("Failed to persist container \"%s\". Error: %s", name, e)
      return False
    return True

  def addContainer(self, name, try_to_load=True, **initial_attributes):
    container = PersistableStorageContainer(name)
    self.attachContainer(container, try_to_load=try_to_load, **initial_attributes)
    return container

  def attachContainer(self, container, try_to_load=True, **initial_attributes):
    super(PersistableStorageHandler, self).attachContainer(container)

    name = container._container_name # all PersistableStorageContainer
                                      # children will have this attribute

    if try_to_load and name: # can't load from storage without a name
      if not self.loadContainer(container, name):
        log.info("Couldn't load persistable container \"%s\" from storage - "
            "continuing.", name)
        for k, v in initial_attributes.iteritems():
          setattr(container, k, v) # only initialize attrs if failed to load
      else:
        log.info("Loaded persistable container \"%s\" from storage", name)

  def detachContainer(self, container, try_to_save=True):
    name = container._container_name
    log.debug("Detaching container \"%s\"...", name if name else "[no name]")

    ret_val = True
    if try_to_save and name:
      if not self.saveContainer(container, name):
        log.warning("Couldn't save persistable container \"%s\" to storage. "
            "This is unexpected.", name)
        ret_val = False
      else:
        log.info("Saved persistable container \"%s\"", name)

    super(PersistableStorageHandler, self).detachContainer(container)

    return ret_val # if we weren't supposed to attempt a save, return True, too

  def close(self):
    return super(PersistableStorageHandler, self).close()


class StorageContainer(object):
  """Base class for things that store some bot data/state."""
  pass


class PersistableStorageContainer(StorageContainer):
  """Generic serializable/persistable-container class."""

  def __init__(self, name=None):
    super(PersistableStorageContainer, self).__init__()

    self._container_name = name


if __name__ == '__main__':
  pass
