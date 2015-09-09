# -*- coding: utf-8 -*-

class ParsingError(Exception):
  def __init__(self, message, filename, line):
    self.message = message
    self.filename = filename
    self.line = line

  def __str__(self):
    return self.message + ' [' + self.filename + ': line ' + str(self.line) + ']'

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
