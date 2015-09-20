# -*- coding: utf-8 -*-

import re
from content_error import ContentError

def strip(line, newlines = False):
  def lstrip(line):
    i = 0
    for e in line:
      if type(e) == Letter and e.value.isspace():
        i += 1
      elif newlines and type(e) == Linebreak:
        i += 1
      else: break
    return line[i:]
  def rstrip(line):
    i = 0
    for e in reversed(line):
      if type(e) == Letter and e.value.isspace():
        i -= 1
      elif newlines and type(e) == Linebreak:
        i -= 1
      else: break
    return line[:-i] if i > 0 else line
  return rstrip(lstrip(line))

# according to our assumptions: tag handle only whole lines
def _consumeLines(body, lines, repetitions, finalizer):
  idx = 0
  while True:
    while len(body)>idx and is_whitespace(body[idx]): idx+=1
    if len(body) <= idx:
      finalizer(lines, repetitions)
      return
    # two possibilities:
    # 1) rep tag
    if type(body[idx]) == Tag:
      body[idx].consumeLines(lines, repetitions)
      idx += 1
      while len(body)>idx and type(body[idx]) == Letter and body[idx].value.isspace(): idx+= 1
      # newline or end => OK; else => error
      if len(body)<=idx:
        finalizer(lines, repetitions)
        return # OK
      if type(body[idx]) == Linebreak:
        idx += 1
        continue
      raise ContentError("Newline only allowed after [/rep]",'')
    # 2) simple line
    else:
      acc = []
      # consume till Linebreak or end, fail on Tag
      while len(body)>idx and type(body[idx]) not in {Linebreak, Tag}:
        acc.append(body[idx])
        idx += 1
      if len(body)<=idx or type(body[idx]) == Linebreak:
        acc = strip(acc)
        if acc != []: lines.append(acc)
      if len(body)<=idx:
        finalizer(lines, repetitions)
        return # OK
      if type(body[idx]) == Linebreak:
        idx += 1
        continue
      raise ContentError("Tags inside the line not allowed",'')


class ParsingError(Exception):
  def __init__(self, message):
    self.massage = message

  def __repr__(self):
    return self.message

class Section:
  def __init__(self, head='', options='', body=None):
    self.head = head
    self.options = options
    self.body = (body if body else [])

  def __repr__(self):
    return '<section: '+self.head+'>['+''.join([repr(t) for t in self.body])+']'

  # according to our assumptions: tag handle only whole lines
  def consumeLines(self, lines, repetitions):
    def finalizer(l, r): pass
    _consumeLines(self.body, lines, repetitions, finalizer)

class Letter:
  def __init__(self, value):
    self.value = value
  def __repr__(self): return self.value

class Tag:
  def __init__(self, head='', options='', body=None):
    self.head = head
    self.options = options
    self.body = (body if body else [])


  def __repr__(self):
    return '<tag: '+self.head+'>['+''.join([repr(t) for t in self.body])+']'

  # according to our assumptions: tag handle only whole lines
  def consumeLines(self, lines, repetitions):
    begin = len(lines)
    def finalizer(l, r): r.append((begin, len(l), int(self.options)))
    _consumeLines(self.body, lines, repetitions, finalizer)

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
    ret4 = re.match('^\{(?P<name>[^\}]+)\}', s)
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


def is_whitespace(s):
  return is_code_whitespace(s) or type(s) == LinebreakSuggestion

def is_code_whitespace(s):
  return type(s) == Linebreak or type(s) == Letter and s.value.isspace()
