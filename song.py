# -*- coding: utf-8 -*-

from parser import parse_file
from content_error import ContentError
from lib import betterSplit
from defining_part import DefiningPart
from referencing_part import ReferencingPart

import lycode

from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont




class InstrumentalPart:
  def __init__(self, part, song):
    self.body = part.body

  def height(self, songbook, section, width):
    return 0

  def is_instrumental(self):
    return True

class Song:
  def __init__(self, f):
    self.title = ''
    self.subtitle = ''
    self.author = ''
    self.url = ''
    self.translator = ''
    self.based = ''
    self.original = ''
    self.copyright = ''
    self.tags = []
    self.note = []
    self.parts = []
    self.part_by_name = {}
    self.filename = f.name
    self.known_parts = set()

    config = parse_file(f)

    if 'title' in config: self.title = config.pop('title')
    else: raise ContentError("Song attribute 'title' not specified.", f.name)

    if 'subtitle' in config: self.subtitle = config.pop('subtitle')
    if 'author' in config: self.author = config.pop('author')
    if 'url' in config: self.url = config.pop('url')
    if 'tags' in config: self.tags = config.pop('tags').split()
    if 'note' in config: self.note = config.pop('note')
    lyrics = ''
    if 'lyrics' in config: lyrics = config.pop('lyrics')

    if len(config) > 0:
      print("Unused labels in "+f.name+": " + str(config.keys()), file=sys.stderr)

    sects = lycode.parse(lyrics)
    for sect in sects:
      if sect.head == 'def':
        self.parts.append(DefiningPart(sect, self))
      elif sect.head == 'ref':
        self.parts.append(ReferencingPart(sect, self))
      elif sect.head == 'instrumental':
        self.parts.append(InstrumentalPart(sect, self))
      else:
        raise ContentError("Unknown section type", f.name)

  def close_page(self, canvas, songbook, section, left, right):
    section.close_page(canvas, songbook, left, right)
    if songbook.is_left_page(canvas):
      self.known_parts = set()

  def getFirstPartHeight(self, songbook, section, width):
    parts = self.parts
    if songbook.style.song_skip_instrumentals:
      parts = filter(lambda x: not x.is_instrumental(), parts)
    if parts == []: return 0.
    else: return parts[0].height(songbook, section, self, width)

  def draw(self, canvas, songbook, section, position, identifier, first, last):
    st = songbook.style
    sb = songbook
    c = canvas
    wrk_widt = sb.width - st.song_margin_inner - st.song_margin_outer
    fpos = position

    titleA = betterSplit(self.title.strip(), st.song_title_font_name, st.song_title_font_size, wrk_widt)
    subtitleA = betterSplit(self.subtitle.strip(), st.song_subtitle_font_name, st.song_subtitle_font_size, wrk_widt - st.song_subtitle_indent)
    authorA = betterSplit(self.author.strip(), st.song_author_font_name, st.song_author_font_size, wrk_widt - st.song_author_indent)
    tagsA = betterSplit(' '.join(self.tags).strip(), st.song_tags_font_name, st.song_tags_font_size, wrk_widt - st.song_tags_indent)
    urlA = betterSplit(self.url.strip(), st.song_url_font_name, st.song_url_font_size, wrk_widt - st.song_url_indent)

    min_hej = len(titleA)*st.song_title_line_height + st.song_title_margin_post
    min_hej += 0 if not st.song_subtitle else len(subtitleA)*st.song_subtitle_line_height + st.song_subtitle_margin_post
    min_hej += 0 if not st.song_author else len(authorA)*st.song_author_line_height + st.song_author_margin_post
    min_hej += 0 if not st.song_tags else len(tagsA)*st.song_tags_line_height + st.song_tags_margin_post
    min_hej += 0 if 'text' not in st.song_url else len(urlA)*st.song_url_line_height + st.song_url_margin_post
    min_hej += st.song_part_margin_top
    min_hej += self.getFirstPartHeight(sb, section, wrk_widt)   # TODO: czy taka szerokość robocza?
    min_hej = max(min_hej, st.song_numbering_line_height + st.song_numbering_qr_spacing + st.song_qr_size)
    if position - st.song_margin_bottom < min_hej:
      section.close_page(c, sb, first, last)
      fpos = mpos = position = sb.height - st.song_margin_top
      first = identifier

    if sb.is_left_page(c):
      margin_left = st.song_margin_outer
      margin_right = st.song_margin_inner
    else:
      margin_left = st.song_margin_inner
      margin_right = st.song_margin_outer
    # title
    fnt_name = st.song_title_font_name
    fnt_size = st.song_title_font_size
    c.setFont(fnt_name, fnt_size)
    for line in titleA:
      position -= st.song_title_line_height
      c.drawString(margin_left, position, line)
    # subtitle
    if st.song_subtitle:
      fnt_name = st.song_subtitle_font_name
      fnt_size = st.song_subtitle_font_size
      c.setFont(fnt_name, fnt_size)
      for line in subtitleA:
        position -= st.song_subtitle_line_height
        c.drawString(margin_left+st.song_subtitle_indent, position, line)
    # author
    if st.song_author:
      fnt_name = st.song_author_font_name
      fnt_size = st.song_author_font_size
      c.setFont(fnt_name, fnt_size)
      for line in authorA:
        position -= st.song_author_line_height
        c.drawString(margin_left+st.song_author_indent, position, line)
    # tags
    if st.song_tags:
      fnt_name = st.song_tags_font_name
      fnt_size = st.song_tags_font_size
      c.setFont(fnt_name, fnt_size)
      for line in tagsA:
        position -= st.song_tags_line_height
        c.drawString(margin_left+st.song_tags_indent, position, line)
    # url
    if 'text' in st.song_url:
      fnt_name = st.song_url_font_name
      fnt_size = st.song_url_font_size
      c.setFont(fnt_name, fnt_size)
      for line in urlA:
        position -= st.song_url_line_height
        c.drawString(margin_left+st.song_url_indent, position, line)
    # numbering
    fnt_name = st.song_numbering_font_name
    fnt_size = st.song_numbering_font_size
    c.setFont(fnt_name, fnt_size)
    mpos = fpos - st.song_numbering_line_height
    if sb.is_left_page(c):
      c.drawString(st.song_numbering_edge_distance, mpos, identifier)
    else:
      c.drawRightString(sb.width - st.song_numbering_edge_distance, mpos, identifier)
    # qr url
    if self.url != '' and 'qr' in st.song_url:
      qr = QrCodeWidget(self.url)
      d = Drawing(st.song_qr_size, st.song_qr_size, transform=[st.song_qr_size/qr.barWidth,0,0,st.song_qr_size/qr.barHeight,0,0])
      d.add(qr)
      mpos -= st.song_qr_size + st.song_numbering_qr_spacing
      if sb.is_left_page(c):
        renderPDF.draw(d, c, st.song_url_qr_edge_distance, mpos)
      else:
        renderPDF.draw(d, c, sb.width - st.song_url_qr_edge_distance - st.song_qr_size, mpos)
    fpn = c.getPageNumber()
    cpos = position
    cfst = first
    clst = identifier
    for part in self.parts:
      cpos -= st.song_part_margin_top
      cpos, cfst, clst = part.draw(canvas, songbook, section, self, cpos, identifier, cfst, clst)
    lpn = c.getPageNumber()
    return (cpos if fpn != lpn else min(cpos, mpos), cfst, identifier)
