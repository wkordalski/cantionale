# -*- coding: utf-8 -*-

import sys

from parser import parse_file
from content_error import ContentError

class Style:
  def __init__(self, f = None):
    if f != None:
      config = parse_file(f)
      filename = f.name
    else:
      config = dict()
      filename = ''

    def switch(s):
      if s in ['Y', 'y', 'ON', 'On', 'on', '1']: return True
      if s in ['N', 'n', 'OFF', 'Off', 'off', '0']: return False
      ContentError('Unknown option %s'%s, filename)

    def options(s):
      if s in ['none', 'None']: return []
      else: return s.split()

    def opt(name, default, func = None):
      if not func:
        if type(default) == str: func = str
        elif type(default) == float: func = float
        elif type(default) == bool: func = switch
        else: func = str

      if name in config:
        return func(config.pop(name))
      else:
        return default

    self.pagesize = opt('page.size', 'A4')

    self.titlepage = opt('title-page', True, switch)
    self.titlepage_margin_top = opt('title-page.margin.top', 128., float)
    self.titlepage_margin_bottom = opt('title-page.margin.bottom', 64., float)

    self.titlepage_title_font_name = opt('title-page.title.font.name', 'DejaVuSans-Bold')
    self.titlepage_title_font_size = opt('title-page.title.font.size', 48., float)
    self.titlepage_title_line_height = opt('title-page.title.line-height', 1.2*self.titlepage_title_font_size, float)

    self.titlepage_title_subtitle_spacing = opt('title-page.title-subtitle.spacing', 64., float)

    self.titlepage_subtitle_font_name = opt('title-page.subtitle.font.name', 'DejaVuSans')
    self.titlepage_subtitle_font_size = opt('title-page.subtitle.font.size', 32., float)
    self.titlepage_subtitle_line_height = opt('title-page.subtitle.line-height', 1.2*self.titlepage_subtitle_font_size, float)

    self.titlepage_author_font_name = opt('title-page.author.font.name', 'DejaVuSans')
    self.titlepage_author_font_size = opt('title-page.author.font.size', 24., float)
    self.titlepage_author_line_height = opt('title-page.author.line-height', 1.2*self.titlepage_author_font_size, float)

    self.notepage = opt('note-page', True, switch)
    self.notepage_margin_top = opt('note-page.margin.top', 64., float)
    self.notepage_margin_bottom = opt('note-page.margin.bottom', 64., float)
    self.notepage_margin_left = opt('note-page.margin.left', 64., float)
    self.notepage_margin_right = opt('note-page.margin.right', 64., float)
    self.notepage_font_name = opt('note-page.font.name', 'DejaVuSans')
    self.notepage_font_size = opt('note-page.font.size', 14., float)
    self.notepage_line_height = opt('note-page.line-height', 1.2*self.notepage_font_size, float)

    self.section_header_numbering_font_name = opt('section.header.numbering.font.name', 'DejaVuSans')
    self.section_header_numbering_font_size = opt('section.header.numbering.font.size', 12., float)
    self.section_header_numbering_line_height = opt('section.header.numbering.line-height', 1.2*self.section_header_numbering_font_size, float)
    self.section_margin_top = opt('section.margin.top', 64., float)
    self.section_margin_bottom = opt('section.margin.bottom', 64., float)
    self.section_margin_left = opt('section.margin.left', 64., float)
    self.section_margin_right = opt('section.margin.right', 64., float)
    self.section_title_font_name = opt('section.title.font.name', 'DejaVuSans')
    self.section_title_font_size = opt('section.title.font.size',24., float)
    self.section_title_line_height = opt('section.title.line-height', 28., float)
    self.section_description = opt('section.description', True, switch)
    self.section_title_description_spacing = opt('section.title-description.spacing', 20., float)
    self.section_description_font_name = opt('section.description.font.name', 'DejaVuSans')
    self.section_description_font_size = opt('section.description.font.size', 14., float)
    self.section_description_line_height = opt('section.description.line-height', 1.2*self.section_description_font_size, float)
    self.section_description_song_spacing = opt('section.description-song.spacing', 20., float)
    self.section_song_song_spacing = opt('section.song-song.spacing', 10., float)
    self.section_numbering_height = opt('section.numbering,height', 24., float)
    self.section_numbering_edge_distance = opt('section_numbering_edge_distance', 24., float)
    self.section_numbering_both = opt('section.numbering.both', True, switch)

    self.song_margin_inner = opt('song.margin.inner', 32., float)
    self.song_margin_outer = opt('song.margin.outer', 72., float)
    self.song_margin_top = opt('song.margin.top', 64., float)
    self.song_margin_bottom = opt('song.margin.bottom', 64., float)

    self.song_title_font_name = opt('song.title.font.name', 'DejaVuSans-Bold')
    self.song_title_font_size = opt('song.title.font.size', 14., float)
    self.song_title_line_height = opt('song.title.line-height', 1.2*self.song_title_font_size, float)
    self.song_title_margin_post = opt('song.title.margin.post', 4., float)

    self.song_subtitle = opt('song.subtitle', False)
    self.song_subtitle_font_name = opt('song.subtitle.font.name', 'DejaVuSans')
    self.song_subtitle_font_size = opt('song.subtitle.font.size', 12.)
    self.song_subtitle_line_height = opt('song.subtitle.line-height', 1.2*self.song_subtitle_font_size)
    self.song_subtitle_margin_post = opt('song.subtitle.margin.post', 4.)
    self.song_subtitle_indent = opt('song.subtitle.indent', 8.)

    self.song_author = opt('song.author', False)
    self.song_author_font_name = opt('song.author.font.name', 'DejaVuSans')
    self.song_author_font_size = opt('song.author.font.size', 12.)
    self.song_author_line_height = opt('song.author.line-height', 1.2*self.song_author_font_size)
    self.song_author_margin_post = opt('song.author.margin.post', 4.)
    self.song_author_indent = opt('song.author.indent', 8.)

    self.song_tags = opt('song.tags', False)
    self.song_tags_font_name = opt('song.tags.font.name', 'DejaVuSans')
    self.song_tags_font_size = opt('song.tags.font.size', 10.)
    self.song_tags_line_height = opt('song.tags.line-height', 1.2*self.song_tags_font_size)
    self.song_tags_margin_post = opt('song.tags.margin.post', 4.)
    self.song_tags_indent = opt('song.tags.indent', 16.)

    self.song_url_font_name = opt('song.url.font.name', 'DejaVuSans')
    self.song_url_font_size = opt('song.url.font.size', 10.)
    self.song_url_line_height = opt('song.url.line-height', 1.2*self.song_url_font_size)
    self.song_url_margin_post = opt('song.url.margin.post', 4.)
    self.song_url_indent = opt('song.url.indent', 8.)

    self.song_numbering_edge_distance = opt('song.numbering.edge-distance', 20.)
    self.song_numbering_font_name = opt('song.numbering.font.name', 'DejaVuSans')
    self.song_numbering_font_size = opt('song.numbering.font.size', 14.)
    self.song_numbering_line_height = opt('song.numbering.line-height', 1.2*self.song_numbering_font_size)

    self.song_qr_size = opt('song.url.qr.size', 40.)
    self.song_numbering_qr_spacing = opt('song.numbering-qr.spacing', 8.)
    self.song_url_qr_edge_distance = opt('song.url.qr.edge-distance', 16.)

    self.song_url = opt('song.url', ['qr'], options)

    self.song_skip_instrumentals = opt('song.instrumental.skip', False)
    self.song_repeat_character = opt('song.repeat.character', '✕')
    self.song_repeat_font_name = opt('song.repeat.font.name', 'DejaVuSans')
    self.song_repeat_font_size = opt('song.repeat.font.size', 10.)
    self.song_repeat_margin_left = opt('song.repeat.margin.left', 8.)
    self.song_repeat_line_text_spacing = opt('song.repeat.line-text.spacing', 4.)

    self.song_lyrics_repetition_spacing = opt('song.lyrics-repetition.spacing', 2.)
    self.song_repetition_chords_spacing = opt('song.repetition-chords.spacing', 2.)
    self.song_repetition_column_optimal_width = opt('song.repetition.column.optimal-width', 64.)
    self.song_chords_column_width = opt('song.chords.column.width', 80.)
    self.song_repetition_line_margin_outer = opt('song.repetition.line.margin-outer', 1.)

    self.song_text_line_indent = opt('song.text.line-indent', 20.)
    self.song_text_line_indent_first = opt('song.text.line-indent.first', 12.)
    self.song_text_font_name = opt('song.text.font.name', 'DejaVuSans')
    self.song_text_font_size = opt('song.text.font.size', 11.)
    self.song_text_line_height = opt('song.text.line-height', 12.)
    self.song_chords = opt('song.chords', True)
    self.song_chords_font_name = opt('song.chords.font.name', 'DejaVuSans-Bold')
    self.song_chords_font_size = opt('song.chords.font.size', 10.)
    self.song_chords_line_height = opt('song.chords.line-height', 1.2*self.song_chords_font_size)
    self.song_part_numbering_font_name = opt('song.part.numbering.font.name', 'DejaVuSans')
    self.song_part_numbering_font_size = opt('song.part.numbering.font.size', 11.)
    self.song_part_numbering_line_height = opt('song.part.numbering.line-height', 12.)
    self.song_part_numbering_width = opt('song.part.numbering.width', 8.)

    self.song_part_margin_top = opt('song.part.margin.top', 8.)

    self.song_referencing_text_font_name = opt('song.referencing.text.font.name', 'DejaVuSans-Oblique')
    self.song_referencing_text_font_size = opt('song.referencing.text.font.size', 11.)
    self.song_referencing_text_line_height = opt('song.referencing.text.line-height', 12.)
    self.song_referencing_stripped_characters = opt('song.referencing.stripped-characters', '.,:;')
    self.song_referencing_text_line_indent = opt('song.referencing.text.line-indent', 12.)

    self.song_instrumental_font_name = opt('song.instrumental.font.name', 'DejaVuSans-Oblique')
    self.song_instrumental_font_size = opt('song.instrumental.font.size', 11.)
    self.song_instrumental_line_height = opt('song.instrumental.line-height', 1.2*self.song_instrumental_font_size)
    self.song_instrumental_line_indent = opt('song.instrumental.line-indent', 20.)
    self.song_instrumental_line_indent_first = opt('song.instrumental.line-indent.first', 12.)

    self.toc_margin_top = opt('toc.margin.top', 64.)
    self.toc_title_font_name = opt('toc.title.font.name', 'DejaVuSans-Bold')
    self.toc_title_font_size = opt('toc.title.font.size', 24.)
    self.toc_title_line_height = opt('toc.title.line-height', 1.2*self.toc_title_font_size)
    self.toc_section_section_spacing = opt('toc.section-section.spacing', 8.)
    self.toc_section_title_font_name = opt('toc.section.title.font.name', 'DejaVuSans-Bold')
    self.toc_section_title_font_size = opt('toc.section.title.font.size', 14.)
    self.toc_section_title_line_height = opt('toc.section.title.line-height', 1.2*self.toc_section_title_font_size)
    self.toc_section_title_indent = opt('toc.section.title.indent', 48.)
    self.toc_section_prefix_indent = opt('toc.section.prefix.indent', 40.)
    self.toc_margin_bottom = opt('toc.margin.bottom', 64.)
    self.toc_margin_inner = opt('toc.margin.inner', 24.)
    self.toc_margin_outer = opt('toc.margin.outer', 48.)

    self.toc_song_number_font_name = opt('toc.song.number.font.name','DejaVuSans')
    self.toc_song_number_font_size = opt('toc.song.number.font.size', 11.)
    self.toc_song_title_font_name = opt('toc.song.title.font.name', 'DejaVuSans')
    self.toc_song_title_font_size = opt('toc.song.title.font.size', 11.)
    self.toc_song_number_indent = opt('toc.song.number.indent', 40.)
    self.toc_song_title_indent = opt('toc.song.title.indent', 48.)
    self.toc_song_song_spacing = opt('toc.song-song.spacing', 1.)
    self.toc_section_title_song_spacing = opt('toc.section.title-song.spacing', 4.)
    self.toc_song_line_height = opt('toc.song.line-height', 1.2*max(self.toc_song_number_font_size, self.toc_song_title_font_size))

    self.title_index_margin_top = opt('title-index.margin.top', 64.)
    self.title_index_margin_bottom = opt('title-index.margin.bottom', 64.)
    self.title_index_title_font_name = opt('title-index.title.font.name', 'DejaVuSans-Bold')
    self.title_index_title_font_size = opt('title-index.title.font.size', 24.)
    self.title_index_song_song_spacing = opt('title-index.song-song.spacing', 1.)
    self.title_index_song_title_indent = opt('title-index.song.title.indent', 48.)
    self.title_index_title_line_height = opt('title-index.title.line-height', 1.2*self.title_index_title_font_size)
    self.title_index_song_number_font_name = opt('title-index.song.number.font.name', 'DejaVuSans')
    self.title_index_song_number_font_size = opt('title-index.song.number.font.size', 11.)
    self.title_index_song_title_font_size = opt('title-index.song.title.font.size', 11.)
    self.title_index_song_title_font_name = opt('title-index.song.title.font.name', 'DejaVuSans')
    self.title_index_song_number_indent = opt('title-index.song.number.indent', 40.)
    self.title_index_title_song_spacing = opt('title-index.title-song.spacing', 16.)
    self.title_index_margin_outer = opt('title-index.margin.outer', 48.)
    self.title_index_margin_inner = opt('title-index.margin.inner', 24.)
    self.title_index_song_line_height = opt('title-index.song.line-height', 1.2*max(self.title_index_song_number_font_size, self.title_index_song_title_font_size))

    self.song_separator_height = opt('song.separator.height', 4.)

    self.fonts = opt('fonts', {'DejaVuSans':'DejaVuSans.ttf', 'DejaVuSans-Bold':'DejaVuSans-Bold.ttf', 'DejaVuSans-Oblique':'DejaVuSans-Oblique.ttf'}, eval)

    if len(config) > 0:
      print("Unused labels in "+f.name+": " + str(config.keys()), file=sys.stderr)
