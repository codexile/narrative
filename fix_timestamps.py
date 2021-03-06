#!/usr/bin/python2
import datetime
import json
import os
import re
import sys

import pyexiv2

DIR_TIMESTAMP_RE = re.compile('(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/'
                              '(?P<hour>\d{2})(?P<min>\d{2})(?P<sec>\d{2})'
                              '\.jpg')


class Error(Exception):
  """base exception class for narrative util functions."""


def UsageError(msg=None):
  print ("""
    Usage:
      ./fix_timestamps.py <narrative_directory> [<utc offset>]

    Example:
      ./fix_timestamps.py /home/user/narrative/ -6
  """)
  if msg:
    print msg
  sys.exit(1)


def GetParsedValidatedArgv(argv):
  if not len(argv) > 1:
    UsageError('Narrative directory is required.')

  if not os.path.isdir(argv[1]):
    UsageError('Path supplied [%s] is not a valid directory.' % argv[1])

  offset = 0
  if len(argv) > 2:
    try:
      offset = int(argv[2])
    except ValueError:
      UsageError('Timezone offset [%s] not an integer.' % argv[2])

  return argv[1], offset


def GetJsonPath(jpg_path):
  dirname, jpg = os.path.split(jpg_path)
  image, _ = os.path.splitext(jpg)
  return os.path.join(dirname, 'meta', image, '.json')


def main(argv):
  narrative_dir, offset = GetParsedValidatedArgv(argv)

  changes = []
  for dirpath, dirnames, filenames in os.walk(argv[1]):
    jpgs = [j for j in filenames if os.path.splitext(j)[1] == '.jpg']
    for jpg in jpgs:
      abspath = os.path.join(dirpath, jpg)

      dir_timestamp = DIR_TIMESTAMP_RE.search(abspath)
      ts = datetime.datetime(int(dir_timestamp.group('year')),
                             int(dir_timestamp.group('month')),
                             int(dir_timestamp.group('day')),
                             int(dir_timestamp.group('hour')),
                             int(dir_timestamp.group('min')),
                             int(dir_timestamp.group('sec')))
      ts += datetime.timedelta(hours=offset)

      metadata = pyexiv2.ImageMetadata(abspath)
      try:
        metadata.read()
        # TODO(codexile): flag to force even if metadata exists
        if 'Exif.Image.DateTime' not in metadata:
          metadata['Exif.Image.DateTime'] = ts
          metadata.write()
      except IOError:
        print 'Problem modifying EXIF data for %s.  File corrupt?' % filename

  print 'Done!'


if __name__ == '__main__':
  main(sys.argv)
