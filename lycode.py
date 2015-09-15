# -*- coding: utf-8 -*-

import re

class ParsingError(Exception):
  def __init__(self, message):
    self.massage = message

  def __repr__(self):
    return self.message

class Section:
  def __init__(self, head='', options='', body=None):
    self.head = head
    self.options = options
    if body: self.body = body
    else: self.body = []

  def __repr__(self):
    return '<section: '+self.head+'>['+''.join([repr(t) for t in self.body])+']'

class Letter:
  def __init__(self, value):
    self.value = value
  def __repr__(self): return self.value

class Tag:
  def __init__(self, head='', options='', body=None):
    self.head = head
    self.options = options
    if body: self.body = body
    else: self.body = []


  def __repr__(self):
    return '<tag: '+self.head+'>['+''.join([repr(t) for t in self.body])+']'

class Chord:
  def __init__(self, value):
    self.value = value

  def __repr__(self):
    return '<chord: '+self.value+'>'

class Linebreak:
  def __init__(self):
    pass

  def __repr__(self):
    return '\\\\'

class LinebreakSuggestion:
  def __init__(self):
    pass

  def __repr__(self):
    return '\\'

def parse(s):
  section = Section()
  sections = [section]
  container = [] # tags here
  def top_container():
    return (section if container == [] else container[-1]).body
  def get_group(match, group, default):
    r = match.group(group)
    if r: return r
    else: return default
  while s != '':
    ret1 = re.match('^\[#\s*(?P<head>\w+)(\s+(?P<options>[^\]]*))?\]', s)
    ret2 = re.match('^\[\s*(?P<head>\w+)(\s+(?P<options>[^\]]*))?\]', s)
    ret3 = re.match('^\[/\s*(?P<head>\w+)\s*\]', s)
    ret4 = re.match('^\{(?P<name>.+)\}', s)
    if ret1:
      if container != []: raise ParsingError('Not closed tag')
      section = Section(ret1.group('head').strip(), get_group(ret1, 'options', '').strip())
      sections.append(section)
      s = s[ret1.end():]
    elif ret2:
      tag = Tag(ret2.group('head').strip(), get_group(ret2, 'options', '').strip())
      top_container().append(tag)
      container.append(tag)
      s = s[ret2.end():]
    elif ret3:
      if container == [] or ret3.group('head').strip() != container[-1].head:
        raise ParsingError('Wrong closing tag: '+ret3.group('head').strip())
      container.pop()
      s = s[ret3.end():]
    elif ret4:
      chord = Chord(ret4.group('name'))
      top_container().append(chord)
      s = s[ret4.end():]
    else:
      if s[0] == '\n': top_container().append(Linebreak())
      elif s[0] == '\\':top_container().append(LinebreakSuggestion())
      else: top_container().append(Letter(s[0]))
      s = s[1:]
  for elt in sections[0].body:
    if not is_code_whitespace(elt): raise ParsingError('Some content out of section')
  return sections[1:]

def is_code_whitespace(s):
  return type(s) == Linebreak or type(s) == Letter and s.value.isspace()
