# -*- coding: utf-8 -*-

from parser import parse_file
from content_error import ContentError
from lib import betterSplit

import lycode

from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class DefiningPart:
  def __init__(self, part, song):
    self.name = part.options.strip()
    song.part_by_name[self.name] = self
    self.body = part.body
    self.lines = []         # array of arrays of elements (letters, chords, linebreak suggestions)
    self.repetitions = []   # array of pairs of indices
    part.consumeLines(self.lines, self.repetitions)
    self.repetitions.sort(key=lambda repetition: repetition[1]-repetition[0])

  def _repetition_column_width(self, songbook, section):
    L = len(self.lines)
    w = [0.] * L
    st = songbook.style
    c = st.song_repeat_character
    fnt_name = st.song_repeat_font_name
    fnt_size = st.song_repeat_font_size
    bef_line = st.song_repeat_margin_left
    aft_line = st.song_repeat_line_text_spacing
    lin_widt = bef_line + aft_line
    for (b, e, q) in self.repetitions:
      wd = pdfmetrics.stringWidth(c+str(q), fnt_name, fnt_size)+lin_widt
      pl = max(w[b:e], default=0)
      for x in range(b, e):
        w[x] = pl + wd
    return max(w, default=0)

    # splits line if needed and returns minimal lyrics width for these lines
  def _processLine(self, line, songbook, section, lyrics_width, chords_width):
    # split data on lines
    acc = []
    cur = []
    for elt in line:
      if type(elt) == lycode.LinebreakSuggestion:
        acc.append(cur)
        cur = []
      else:
        cur.append(elt)
    acc.append(cur)
    # filter lyrics and chords separately
    lyr = []
    cho = []
    for line in acc:
      ly = ''
      ch = ''
      for elt in line:
        if type(elt) == lycode.Letter:
          ly += elt.value
        elif type(elt) == lycode.Chord:
          ch += elt.value + ' '
      lyr.append(ly)
      cho.append(ch)
    # calculate width of each part
    st = songbook.style
    lyfn = st.song_text_font_name
    lyfs = st.song_text_font_size
    chfn = st.song_chords_font_name
    chfs = st.song_chords_font_size
    slin = st.song_text_line_indent
    flin = st.song_text_line_indent_first
    pch = st.song_chords
    lyw = list(map(lambda s: pdfmetrics.stringWidth(s, lyfn, lyfs), lyr))
    chw = list(map(lambda s: pdfmetrics.stringWidth(s, chfn, chfs), cho))
    # try to join parts of lines in O(n)
    n = len(lyr)
    lyl = flin
    chl = 0.
    lya = ''
    cha = ''
    ret = []
    mlw = 0.
    for i in range(n):
      if lyl + lyw[i] < lyrics_width and (chl + chw[i] < chords_width or not pch):
        lyl += lyw[i]
        lya += lyr[i]
        chl += chw[i]
        cha += cho[i]
      else:
        if slin + lyw[i] < lyrics_width and (chw[i] < chords_width or not pch):
          # output
          ret.append((lya, cha))
          mlw = max(mlw, lyl)
          # new line
          lyl = lyw[i] + slin
          lya = lyr[i]
          chl = chw[i]
          cha = cho[i]
        else:
          raise ContentError('Please, add linebreak suggestion on line: %s'%lyr[i], '<unknown>')
    ret.append((lya, cha))
    mlw = max(mlw, lyl)
    return (ret, mlw)

  def height(self, songbook, section, width):
    st = songbook.style
    rw = self._repetition_column_width(songbook, section) + st.song_lyrics_repetition_spacing
    ro = st.song_repetition_column_optimal_width + st.song_lyrics_repetition_spacing  # won't be used here
    lh = max(st.song_text_line_height, st.song_chords_line_height if st.song_chords else 0)
    cw = (st.song_chords_column_width + st.song_repetition_chords_spacing) if st.song_chords else 0
    lw = width - rw - cw
    a = 0
    for no, line in enumerate(self.lines):
      a += len(self._processLine(line, songbook, section, lw, cw)[0])*lh
    return a

  def height_and_width(self, songbook, section, width):
    st = songbook.style
    rw = self._repetition_column_width(songbook, section) + st.song_lyrics_repetition_spacing
    ro = st.song_repetition_column_optimal_width + st.song_lyrics_repetition_spacing  # won't be used here
    lh = max(st.song_text_line_height, st.song_chords_line_height if st.song_chords else 0)
    cw = (st.song_chords_column_width + st.song_repetition_chords_spacing) if st.song_chords else 0
    lw = width - rw - cw
    a = 0.
    b = 0.
    for no, line in enumerate(self.lines):
      ls, w = self._processLine(line, songbook, section, lw, cw)
      a += len(ls)*lh
      b = max(b, w)
    return (a, b)

  def is_instrumental(self):
    return False

  def draw(self, canvas, songbook, section, song, position, identifier, first, last):
    # czy mamy gdzie narysować sekcje (jeśli prawa strona)
    sb = songbook
    c = canvas
    st = sb.style
    width = sb.width - st.song_margin_inner - st.song_margin_outer
    rw = self._repetition_column_width(songbook, section) + st.song_lyrics_repetition_spacing
    ro = st.song_repetition_column_optimal_width + st.song_lyrics_repetition_spacing  # won't be used here
    cw = (st.song_chords_column_width + st.song_repetition_chords_spacing) if st.song_chords else 0
    lw = width - rw - cw
    lh = max(st.song_text_line_height, st.song_chords_line_height if st.song_chords else 0)
    lb = [0.]*len(self.lines)
    ph, mw = self.height_and_width(songbook, section, width)
    slin = st.song_text_line_indent
    flin = st.song_text_line_indent_first
    if not sb.is_left_page(c):
      ph = self.height(songbook, section, width)
      if ph + st.song_margin_bottom > position:
        section.close_page(c, sb, first, last)
        position = sb.height - st.song_margin_top
        first = identifier
    if sb.is_left_page(c):
      margin_left = st.song_margin_outer
      margin_right = st.song_margin_inner
    else:
      margin_left = st.song_margin_inner
      margin_right = st.song_margin_outer
    chpos = sb.width - st.song_chords_column_width - margin_right
    # draw part name if defined
    if self.name != '':
      c.setFont(st.song_part_numbering_font_name, st.song_part_numbering_font_size)
      c.drawRightString(margin_left + st.song_part_numbering_width, position - st.song_part_numbering_line_height, self.name)
    # draw lyrics
    for no, line in enumerate(self.lines):
      ls = self._processLine(line, songbook, section, lw, cw)[0]
      # sprawdź czy mamy tyle miejsca na stronie
      lph = len(ls)*lh
      if lph + st.song_margin_bottom > position:
        # make page close:
        # draw repetitions
        # do: section.close_page(...)
        # update lb[no] to beginning of page
        pass
      # draw lyrics (and chords)
      fst = True
      for lyr, cho in ls:
        strt = margin_left + (flin if fst else slin)
        fst = False
        position -= lh
        c.setFont(st.song_text_font_name, st.song_text_font_size)
        c.drawString(strt, position, lyr)
        if st.song_chords:
          c.setFont(st.song_chords_font_name, st.song_chords_font_size)
          c.drawString(chpos, position, cho)
    return (position, first, last)


class ReferencingPart:
  def __init__(self, part, song):
    self.rname = part.options.strip()
    self.referee = song.part_by_name.get(self.rname, None)
    if not referee: raise ContentError("Referencing unknown part (%s)."%self.rname)
    self.body = part.body

  def height(self, songbook, section, width):
    return 0

  def is_instrumental(self):
    return False

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

  def getFirstPartHeight(self, songbook, section, width):
    parts = self.parts
    if songbook.style.song_skip_instrumentals:
      parts = filter(lambda x: not x.is_instrumental(), parts)
    if parts == []: return 0.
    else: return parts[0].height(songbook, section, width)

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
