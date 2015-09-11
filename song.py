# -*- coding: utf-8 -*-

from parser import parse_file
from content_error import ContentError
from lib import betterSplit

from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing

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
      print("Unused labels in "+f.name+": " + str(config.keys()), file=sys.stderr)
  
  def getFirstPartHeight(self, songbook, section):
    return 0. # TODO
  
  def draw(self, canvas, songbook, section, position, identifier, first, last):
    st = songbook.style
    sb = songbook
    c = canvas
    wrk_widt = sb.width - st.song_margin_inner - st.song_margin_outer
    fpos = position
    
    titleA = betterSplit(self.title.strip(), st.song_title_font_name, st.song_title_font_size, wrk_widt)
    subtitleA = betterSplit(self.subtitle.strip(), st.song_subtitle_font_name, st.song_subtitle_font_size, wrk_widt)
    authorA = betterSplit(self.author.strip(), st.song_author_font_name, st.song_author_font_size, wrk_widt)
    tagsA = betterSplit(' '.join(self.tags).strip(), st.song_tags_font_name, st.song_tags_font_size, wrk_widt)
    urlA = betterSplit(self.url.strip(), st.song_url_font_name, st.song_url_font_size, wrk_widt)
    
    min_hej = len(titleA)*st.song_title_line_height + st.song_title_margin_post
    min_hej += 0 if not st.song_subtitle else len(subtitleA)*st.song_subtitle_line_height + st.song_subtitle_margin_post
    min_hej += 0 if not st.song_author else len(authorA)*st.song_author_line_height + st.song_author_margin_post
    min_hej += 0 if not st.song_tags else len(tagsA)*st.song_tags_line_height + st.song_tags_margin_post
    min_hej += 0 if 'text' not in st.song_url else len(urlA)*st.song_url_line_height + st.song_url_margin_post
    min_hej += self.getFirstPartHeight(sb, section)
    min_hej = max(min_hej, st.song_numbering_line_height + st.song_numbering_qr_spacing + st.song_qr_size)
    if position - st.song_margin_bottom < min_hej:
      section.close_page(c, sb, first, last)
      fpos = mpos = position = sb.height - st.song_margin_top
      
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
        c.drawString(margin_left, position, line)
    # author
    if st.song_author:
      fnt_name = st.song_author_font_name
      fnt_size = st.song_author_font_size
      c.setFont(fnt_name, fnt_size)
      for line in authorA:
        position -= st.song_author_line_height
        c.drawString(margin_left, position, line)
    # tags
    if st.song_tags:
      fnt_name = st.song_tags_font_name
      fnt_size = st.song_tags_font_size
      c.setFont(fnt_name, fnt_size)
      for line in tagsA:
        position -= st.song_tags_line_height
        c.drawString(margin_left, position, line)
    # url
    if 'text' in st.song_url:
      fnt_name = st.song_url_font_name
      fnt_size = st.song_url_font_size
      c.setFont(fnt_name, fnt_size)
      for line in urlA:
        position -= st.song_url_line_height
        c.drawString(margin_left, position, line)
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
      if sb.is_left_page(c):
        renderPDF.draw(d, c, st.song_url_qr_edge_distance, mpos - st.song_numbering_qr_spacing - st.song_qr_size)
      else:
        renderPDF.draw(d, c, sb.width - st.song_url_qr_edge_distance - st.song_qr_size, mpos - st.song_numbering_qr_spacing - st.song_qr_size)
    return (position, first, identifier) 
