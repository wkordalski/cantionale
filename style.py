# -*- coding: utf-8 -*-

import sys

from parser import parse_file
from content_error import ContentError

class Style:
  def __init__(self, f = None):
    self.pagesize = 'A4'

    self.titlepage = True
    self.titlepage_margin_top = 128.
    self.titlepage_margin_bottom = 64.

    self.titlepage_title_font_name = 'DejaVuSans-Bold'
    self.titlepage_title_font_size = 48.
    self.titlepage_title_line_height = 64.

    self.titlepage_title_subtitle_spacing = 64.

    self.titlepage_subtitle_font_name = 'DejaVuSans'
    self.titlepage_subtitle_font_size = 32.
    self.titlepage_subtitle_line_height = 40.

    self.titlepage_author_font_name = 'DejaVuSans'
    self.titlepage_author_font_size = 24.
    self.titlepage_author_line_height = 28.

    self.notepage = True
    self.notepage_margin_top = 64.
    self.notepage_margin_bottom = 64.
    self.notepage_margin_left = 64.
    self.notepage_margin_right = 64.
    self.notepage_font_name = 'DejaVuSans'
    self.notepage_font_size = 14.
    self.notepage_line_height = 16.

    self.section_margin_top = 64
    self.section_margin_bottom = 64
    self.section_margin_left = 64
    self.section_margin_right = 64
    self.section_title_font_name = 'DejaVuSans'
    self.section_title_font_size = 24.
    self.section_title_line_height = 28.
    self.section_description = True
    self.section_title_description_spacing = 20.
    self.section_description_font_name = 'DejaVuSans'
    self.section_description_font_size = 14.
    self.section_description_line_height = 16.
    self.section_description_song_spacing = 20.
    self.section_song_song_spacing = 10.

    self.section_numbering_height = 32.
    self.section_numbering_edge_distance = 32.
    self.section_numbering_both = True

    self.song_margin_inner = 32.
    self.song_margin_outer = 80.
    self.song_margin_top = 64.
    self.song_margin_bottom = 64.

    self.song_title_font_name = 'DejaVuSans-Bold'
    self.song_title_font_size = 14.
    self.song_title_line_height = 16.
    self.song_title_margin_post = 4.

    self.song_subtitle = True
    self.song_subtitle_font_name = 'DejaVuSans'
    self.song_subtitle_font_size = 12.
    self.song_subtitle_line_height = 14.
    self.song_subtitle_margin_post = 4.
    self.song_subtitle_indent = 8.

    self.song_author = False
    self.song_author_font_name = 'DejaVuSans'
    self.song_author_font_size = 12.
    self.song_author_line_height = 14.
    self.song_author_margin_post = 4.
    self.song_author_indent = 8.

    self.song_tags = False
    self.song_tags_font_name = 'DejaVuSans'
    self.song_tags_font_size = 10.
    self.song_tags_line_height = 12.
    self.song_tags_margin_post = 4.
    self.song_tags_indent = 16.

    self.song_url_font_name = 'DejaVuSans'
    self.song_url_font_size = 10.
    self.song_url_line_height = 12.
    self.song_url_margin_post = 4.
    self.song_url_indent = 8.

    self.song_numbering_edge_distance = 24.
    self.song_numbering_font_name = 'DejaVuSans'
    self.song_numbering_font_size = 14.
    self.song_numbering_line_height = 16.

    self.song_qr_size = 40.
    self.song_numbering_qr_spacing = 8.
    self.song_url_qr_edge_distance = 16.

    self.song_url = ['qr']

    self.song_skip_instrumentals = False

    if f != None:
      self.read_from_file(f)

  def read_from_file(self, f):
    config = parse_file(f)

    if 'page.size' in config: self.pagesize = config.pop('page.size')

    # TITLE PAGE
    if 'title-page' in config:
      s = config.pop('title-page')
      if s == 'on' or s == 'ON' or s == 'y' or s == 'Y' or s == 'On': self.titlepage = True
      elif s == 'off' or s == 'OFF' or s == 'n' or s == 'N' or s == 'Off': self.titlepage = False
      else: raise ContentError("'title-page' must be 'on' or 'off'", f.name)
    if 'title-page.margin.top' in config:
      self.titlepage_margin_top = float(config.pop('title-page.margin.top'))
    if 'title-page.margin.bottom' in config:
      self.titlepage_margin_bottom = float(config.pop('title-page.margin.bottom'))

    if 'title-page.title.font.name' in config:
      self.titlepage_title_font_name = config.pop('title-page.title.font.name')
    if 'title-page.title.font.size' in config:
      self.titlepage_title_font_size = float(config.pop('title-page.title.font.size'))
    if 'title-page.title.line.height' in config:
      self.titlepage_title_line_height = float(config.pop('title-page.title.line.height'))
    else:
      self.titlepage_title_line_height = 1.2 * self.titlepage_title_font_size

    if 'title-page.title-subtitle.spacing' in config:
      self.titlepage_title_subtitle_spacing = float(config.pop('title-page.title-subtitle.spacing'))

    if 'title-page.subtitle.font.name' in config:
      self.titlepage_subtitle_font_name = config.pop('title-page.subtitle.font.name')
    if 'title-page.subtitle.font.size' in config:
      self.titlepage_subtitle_font_size = float(config.pop('title-page.subtitle.font.size'))
    if 'title-page.subtitle.line.height' in config:
      self.titlepage_subtitle_line_height = float(config.pop('title-page.subtitle.line.height'))
    else:
      self.titlepage_subtitle_line_height = 1.2 * self.titlepage_subtitle_font_size

    if 'title-page.author.font.name' in config:
      self.titlepage_author_font_name = config.pop('title-page.author.font.name')
    if 'title-page.author.font.size' in config:
      self.titlepage_author_font_size = float(config.pop('title-page.author.font.size'))
    if 'title-page.author.line.height' in config:
      self.titlepage_author_line_height = float(config.pop('title-page.author.line.height'))
    else:
      self.titlepage_author_line_height = 1.2 * self.titlepage_author_font_size

    # NOTES PAGE
    if 'note-page' in config:
      s = config.pop('note-page')
      if s == 'on' or s == 'ON' or s == 'y' or s == 'Y' or s == 'On': self.notepage = True
      elif s == 'off' or s == 'OFF' or s == 'n' or s == 'N' or s == 'Off': self.notepage = False
      else: raise ContentError("'note-page' must be 'on' or 'off'", f.name)
    if 'note-page.margin.top' in config:
      self.notepage_margin_top = float(config.pop('note-page.margin.top'))
    if 'note-page.margin.bottom' in config:
      self.notepage_margin_bottom = float(config.pop('note-page.margin.bottom'))
    if 'note-page.margin.left' in config:
      self.notepage_margin_left = float(config.pop('note-page.margin.left'))
    if 'note-page.margin.right' in config:
      self.notepage_margin_right = float(config.pop('note-page.margin.right'))

    if 'note-page.font.name' in config:
      self.notepage_font_name = config.pop('note-page.font.name')
    if 'note-page.font.size' in config:
      self.notepage_font_size = float(config.pop('note-page.font.size'))
    if 'note-page.line.height' in config:
      self.notepage_line_height = float(config.pop('note-page.line.height'))
    else:
      self.notepage_line_height = 1.2 * self.notepage_font_size

    # SECTION PAGE
    # TODO

    if len(config) > 0:
      print("Unused labels in "+f.name+": " + str(config.keys()), file=sys.stderr)
