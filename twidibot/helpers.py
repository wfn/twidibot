#!/usr/bin/env python

import cPickle as pickle
import gzip


def gpDump(obj, fn, protocol=pickle.HIGHEST_PROTOCOL):
  """Pickle dump + gzip file"""

  with gzip.open(fn, "wb") as f:
    pickle.dump(obj, f, protocol)

def gpLoad(fn):
  """Load and return an object from a gzipped pickle file"""

  with gzip.open(fn, "rb") as f:
    obj = pickle.load(f)
  return obj

def round_float_to_int(f_num):
  """Round a floating point number to the nearest int.

  This should work around the issues of int(round(f_num))
  that are experienced when round(f_num) returns a near-integer value,
  and there are discontinuities produced by the int() function near those
  values.
  """

  if f_num > 0:
    return int(f_num + 0.5) # XXX is this too simplistic? any possible weird
                            # XXX edge cases?
  return int(f_num - 0.5)


if __name__ == '__main__':
  pass
