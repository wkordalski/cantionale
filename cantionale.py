#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re
import os

from parser import parse_file
from style import Style
from content_error import ContentError
from song import Song
from songbook import Songbook



'''
If your text is one line string then you can use
from reportlab.pdfbase.pdfmetrics import stringWidth
textWidth = stringWidth(text, fontName, fontSize)

If your text was multi-lines, assuming you are working
in a rectangular area with defined width, then do

from reportlab.lib.utils import simpleSplit
lines = simpleSplit(text, fontName, fontSize, maxWidth)

lines is a list of all the lines of your paragraph, if you know the line spacing value then the
height of the paragraph can be calculated as lineSpacing*len(lines)
'''




def main():
  if len(sys.argv) != 3:
    print("Calling format:\n  " + sys.argv[0] + " <songbook file> <pdf file>\n", file=sys.stderr)
  else:
    f = open(sys.argv[1], encoding='utf-8')
    s = Songbook(f)
    s.draw(sys.argv[2])
  return 0


if __name__ == "__main__":
  main()
