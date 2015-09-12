# -*- coding: utf-8 -*-

from reportlab.lib.utils import simpleSplit

def betterSplit(string, font_name, font_size, width):
  r = [ a for b in [ [''] if s == '' else simpleSplit(s, font_name, font_size, width) for s in string.split(sep='\n') ] for a in b ]
  if r == ['']: return []
  else: return r
