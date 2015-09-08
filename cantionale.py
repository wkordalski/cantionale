#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re
import os

from reportlab.pdfgen import canvas
from reportlab.graphics.barcode.qr import QrCodeWidget

class ParsingError(Exception):
  def __init__(self, message, filename, line):
    self.message = message
    self.filename = filename
    self.line = line

  def __str__(self):
    return self.message + ' [' + self.filename + ': line ' + str(self.line) + ']'

class ContentError(Exception):
  def __init__(self, message, filename):
    self.message = message
    self.filename = filename

  def __str__(self):
    return self.message + ' [' + self.filename + ']'


def parse_file(f):
  # read field name [a-zA-Z0-9_\.-]+:
  # skip spaces
  # read value or if endl => read value till line with "---"
  d = dict()
  T = f.readlines()
  # parse lines
  # trim them
  T = [ s.strip() for s in T ]
  # simply parse
  label = ''
  value = ''
  row = 0
  for s in T:
    row += 1
    if label == '':
      # read label
      if s == '': continue
      line = s.split(sep=':', maxsplit=1)
      if len(line) <= 1: raise ParsingError("Expected label.", f.name, row)
      lbl = line[0].strip()
      val = line[1].strip()
      if lbl == '': raise ParsingError("Empty label.", f.name, row)
      if lbl in d: raise ParsingError("Label already exists.", f.name, row)
      if val == '':
        label = lbl
        value = ''
        continue
      else:
        d[lbl] = val
    else:
      if s == '---':
        d[label] = value
        label = ''
        value = ''
      else:
        value += s + '\n'
  if label != '':
    d[label] = value
  return d

class Song:
  def __init__(self, f):
    self.title = ''
    self.subtitle = ''
    self.author = ''
    self.url = ''
    self.tags = []
    self.note = []
    self.lyrics = ''

    config = parse_file(f)

    if 'title' in config: self.title = config.pop('title')
    else: raise ContentError("Song attribute 'title' not specified.", f.name)

    if 'subtitle' in config: self.subtitle = config.pop('subtitle')
    if 'author' in config: self.author = config.pop('author')
    if 'url' in config: self.url = config.pop('url')
    if 'tags' in config: self.tags = config.pop('tags').split()
    if 'note' in config: self.note = config.pop('note')
    if 'lyrics' in config: self.lyrics = config.pop('lyrics')

    if len(config) > 0:
      print("Unused labels: " + str(config.keys()), file=sys.stderr)

class Section:
  def __init__(self, f):
    self.name = ''
    self.prefix = ''
    self.description = ''
    self.songs = []

    config = parse_file(f)
    directory = '.'

    if 'name' in config: self.name = config.pop('name')
    else: raise ContentError("Section attribute 'name' not specified.", f.name)

    if 'prefix' in config: self.prefix = config.pop('prefix')
    else: raise ContentError("Section attribute 'prefix' not specified.", f.name)

    if 'directory' in config: directory = config.pop('directory')
    if 'description' in config: self.description = config.pop('description')
    if 'contents' in config:
      files = config.pop('contents').split(sep='\n')
      for fn in files:
        fname = fn.strip()
        if fname == '': continue
        fl = open(directory + os.sep + fname, encoding='utf-8')
        s = Song(fl)
        fl.close()
        self.songs.append(s)

    if len(config) > 0:
      print("Unused labels: " + str(config.keys()), file=sys.strerr)


class TableOfContents:
  def __init__(self, title, songbook):
    pass

class Songbook:
  def __init__(self, f):
    self.title = ''
    self.subtitle = ''
    self.author = ''
    self.style = None # na razie
    self.note = ''
    self.sections = []
    self.contents = []

    config = parse_file(f)
    directory = '.'

    if 'title' in config: self.title = config.pop('title')
    else: raise ContentError("Songbook attribute 'title' not specified.", f.name)

    if 'subtitle' in config: self.subtitle = config.pop('subtitle')
    if 'author' in config: self.author = config.pop('author')
    if 'directory' in config: directory = config.pop('directory')
    if 'style' in config:
      style_filename = config.pop('style')
      # TODO: ładowanie stylu
    if 'note' in config: self.note = config.pop('note')
    if 'contents' in config:
      contents = config.pop('contents').split(sep='\n')
      for line in contents:
        cmd = line.strip()
        if cmd == '': continue

        R = re.fullmatch('section\s(?P<file>.+)', cmd)
        if R != None:
          filename = R.group('file').strip()
          fl = open(directory + os.sep + filename, encoding='utf-8')
          s = Section(fl)
          fl.close()
          self.sections.append(s)
          self.contents.append(s)
          continue

        R = re.fullmatch('table\s+of\s+contents\s+as\s(?P<name>.+)', cmd)
        if R != None:
          s = TableOfContents(R.group('name'), self)
          self.contents.append(s)
          continue

        # and so on...

    if len(config) > 0:
      print("Unused labels: " + str(config.keys()), file=sys.stderr)


  def draw(self, filename):
    c = canvas.Canvas(filename)
    # TODO: printing...
    c.showPage()
    # end of TODO
    c.save()

def main():
  if len(sys.argv) != 3:
    print("Calling format:\n  " + sys.argv[0] + " <songbook file> <pdf file>\n", file=sys.stderr)
  else:
    f = open(sys.argv[1], encoding='utf-8')
    s = Songbook(f)
    s.draw(sys.argv[2])
  return 0


main()
