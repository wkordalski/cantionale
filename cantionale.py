#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re
import os

from parser import parse_file
from style import Style
from content_error import ContentError
from song import Song

from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit


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



class Section:
  def __init__(self, f):
    self.title = ''
    self.prefix = ''
    self.description = ''
    self.songs = []

    config = parse_file(f)
    directory = '.'

    if 'title' in config: self.title = config.pop('title')
    else: raise ContentError("Section attribute 'title' not specified.", f.name)

    if 'prefix' in config: self.prefix = config.pop('prefix')

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
      print("Unused labels in "+f.name+": " + str(config.keys()), file=sys.stderr)
      
  def index(self, number):
    if self.prefix == '':
      return str(number)
    else:
      return self.prefix + ' ' + str(number)
    
  def draw(self, canvas, songbook):
    c = canvas
    sb = songbook
    # draw name
    # title
    wrk_widt = sb.width - sb.style.section_margin_left - sb.style.section_margin_right
    lines = self.title.strip().split(sep='\n')
    fnt_size = sb.style.section_title_font_size
    lin_heig = sb.style.section_title_line_height
    c.setFont(sb.style.section_title_font_name, fnt_size)
    pos = sb.height - sb.style.section_margin_top
    for line in lines:
      pos -= lin_heig
      c.drawCentredString(sb.width/2.0, pos, line)
      
    if sb.style.section_description and self.description != '':
      pos -= sb.style.section_title_description_spacing
      fnt_name = sb.style.section_description_font_name
      fnt_size = sb.style.section_description_font_size
      lines = [ a for b in [ [''] if s == '' else simpleSplit(s, fnt_name, fnt_size, wrk_widt) for s in self.description.strip().split(sep='\n')] for a in b ]
      lin_heig = sb.style.section_description_line_height
      c.setFont(fnt_name, fnt_size)
      for line in lines:
        pos -= lin_heig
        if pos <= sb.style.section_margin_bottom:
          c.showPage()
          c.setFont(fnt_name, fnt_size)
          pos = sb.height - sb.style.section_margin_top - lin_heig
        c.drawString(sb.style.section_margin_left, pos, line)
    
    pos -= sb.style.section_description_song_spacing
    idx = 0
    fst = self.index(1)
    lst = ''
    for song in self.songs:
      idx += 1
      (pos, fst, lst) = song.draw(c, sb, self, pos, self.index(idx), fst, lst)
      pos -= sb.style.section_song_song_spacing
    if len(self.songs) > 0: self.close_page(c, sb, fst, lst)
    pass
  
  def close_page(self, canvas, songbook, left, right):
    # use canvas.getPageNumber() to know if we need to print left or right
    num_heig = songbook.height - songbook.style.section_numbering_height
    num_edgd = songbook.style.section_numbering_edge_distance
    pag_widt = songbook.width
    if songbook.style.section_numbering_both:
      # right and left printed
      canvas.drawString(num_edgd, num_heig, left)
      canvas.drawRightString(songbook.width - num_edgd, num_heig, right)
    elif canvas.getPageNumber() %2 == 1:
      # right page => print right
      canvas.drawRightString(songbook.width - num_edgd, num_heig, right)
    else:
      # left page => print left
      canvas.drawString(num_edgd, num_heig, left)
    # TODO: draw some line under/over numbering?
    canvas.showPage()
    pass


class TableOfContents:
  def __init__(self, title, songbook):
    pass



class Songbook:
  def __init__(self, f):
    self.title = ''
    self.subtitle = ''
    self.author = ''
    self.style = Style()
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
      fl = open(style_filename, encoding='utf-8')
      self.style = Style(fl)
      fl.close()
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
      print("Unused labels in "+f.name+": " + str(config.keys()), file=sys.stderr)

  def is_left_page(self, canvas):
    return (canvas.getPageNumber() %2 == 0)

  def draw(self, filename):
    pagesize = pagesizes.A4
    if self.style.pagesize == 'A4': pagesize = pagesizes.A4
    elif self.style.pagesize == 'A5': pagesize = pagesizes.A5
    elif self.style.pagesize == 'B5': pagesize = pagesizes.B5
    else: raise NotImplementedError()
    c = canvas.Canvas(filename, pagesize=pagesize)
    (self.width, self.height) = pagesize
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
    
    self.draw_title_page(c)
    self.draw_note_page(c)
    for chapter in self.contents:
      chapter.draw(c, self)
    c.save()
    
  def draw_title_page(self, c):
    if self.style.titlepage:
      # title
      lines = self.title.strip().split(sep='\n')
      fnt_size = self.style.titlepage_title_font_size
      lin_heig = self.style.titlepage_title_line_height
      c.setFont(self.style.titlepage_title_font_name, fnt_size)
      pos = self.height - self.style.titlepage_margin_top
      for line in lines:
        pos -= lin_heig
        c.drawCentredString(self.width/2.0, pos, line)
      
        
      pos -= self.style.titlepage_title_subtitle_spacing
      
      lines = self.subtitle.strip().split(sep='\n')
      fnt_size = self.style.titlepage_subtitle_font_size
      lin_heig = self.style.titlepage_subtitle_line_height
      c.setFont(self.style.titlepage_subtitle_font_name, fnt_size)
      for line in lines:
        pos -= lin_heig
        c.drawCentredString(self.width/2.0, pos, line)
      
      lines = self.author.strip().split(sep='\n')
      fnt_size = self.style.titlepage_author_font_size
      lin_heig = self.style.titlepage_author_line_height
      c.setFont(self.style.titlepage_author_font_name, fnt_size)
      bpos = len(lines)*lin_heig + self.style.titlepage_margin_bottom
      for line in lines:
        bpos -= lin_heig
        c.drawCentredString(self.width/2.0, bpos, line)
        
      c.showPage()
      c.showPage()
        
  def draw_note_page(self, c):
    if self.style.notepage and self.note.strip() != '':
      fnt_size = self.style.notepage_font_size
      wrk_widt = self.width - self.style.notepage_margin_left - self.style.notepage_margin_right
      fnt_name = self.style.notepage_font_name
      lines = [a for b in [[''] if s == '' else simpleSplit(s, fnt_name, fnt_size, wrk_widt) for s in self.note.split(sep='\n')] for a in b]
      lin_heig = self.style.notepage_line_height
      mar_left = self.style.notepage_margin_left
      pos = self.height - self.style.notepage_margin_top
      c.setFont(self.style.titlepage_author_font_name, fnt_size)
      pags = 0
      for line in lines:
        pos -= lin_heig
        if pos <= self.style.notepage_margin_bottom:
          c.showPage()
          c.setFont(self.style.titlepage_author_font_name, fnt_size)
          pags += 1
          pos = self.height - self.style.notepage_margin_top - lin_heig
        c.drawString(mar_left, pos, line)
      c.showPage()
      pags += 1
      if pags % 2 == 1: c.showPage()

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
