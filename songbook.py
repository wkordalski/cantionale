from style import Style
from parser import parse_file
from section import Section
from table_of_contents import TableOfContents
from title_index import TitleIndex

import re
import os


from reportlab.lib import pagesizes
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

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

        R = re.fullmatch('table\s+of\s+contents\s+with\s+(?P<map>.+)', cmd)
        if R != None:
          s = TableOfContents(self, eval(R.group('map')))
          self.contents.append(s)
          continue

        R = re.fullmatch('title index\s+with\s+(?P<map>.+)', cmd)
        if R != None:
          s = TitleIndex(self, eval(R.group('map')))
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
    c.setTitle(self.title)
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Oblique', 'DejaVuSans-Oblique.ttf'))

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
