from content_error import ContentError

import lycode


from reportlab.pdfbase import pdfmetrics

class DefiningPart:
  def __init__(self, part, song):
    self.name = part.options.strip()
    song.part_by_name[self.name] = self
    self.body = part.body
    self.lines = []         # array of arrays of elements (letters, chords, linebreak suggestions)
    self.repetitions = []   # array of pairs of indices
    part.consumeLines(self.lines, self.repetitions)
    self.repetitions.sort(key=lambda repetition: (repetition[1]-repetition[0], repetition[0]))

  def _calculate_repetition_indentation_and_column_width(self, songbook, section):
    L = len(self.lines)
    w = [0.] * L
    st = songbook.style
    c = st.song_repeat_character
    fnt_name = st.song_repeat_font_name
    fnt_size = st.song_repeat_font_size
    bef_line = st.song_repeat_margin_left
    aft_line = st.song_repeat_line_text_spacing
    lin_widt = bef_line + aft_line
    ret = [0.] * len(self.repetitions)
    for no, (b, e, q) in enumerate(self.repetitions):
      wd = pdfmetrics.stringWidth(c+str(q), fnt_name, fnt_size)+lin_widt
      pl = max(w[b:e], default=0)
      ret[no] = pl
      for x in range(b, e):
        w[x] = pl + wd
    return (ret, max(w, default=0))

  # splits line if needed and returns minimal lyrics width for these lines
  def _processLine(self, line, songbook, section, song, lyrics_width, chords_width, do_chords = True):
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
      ly = []
      ch = ''
      for elt in line:
        if type(elt) == lycode.Letter or type(elt) == lycode.Note:
          ly.append(elt)
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
    pch = st.song_chords and do_chords
    lyw = list(map(lambda s: sum(map(lambda p: pdfmetrics.stringWidth(p.value, lyfn, lyfs), s)), lyr))
    chw = list(map(lambda s: pdfmetrics.stringWidth(s, chfn, chfs), cho))
    # try to join parts of lines in O(n)
    n = len(lyr)
    lyl = flin
    chl = 0.
    lya = []
    cha = ''
    ret = []
    mlw = 0.
    for i in range(n):
      if lyl + lyw[i] < lyrics_width and (chl + chw[i] < chords_width or not pch):
        lyl += lyw[i]
        lya.extend(lyr[i])
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
          raise ContentError('Please, add linebreak suggestion on line: %s'%lyr[i], song.filename)
    ret.append((lya, cha))
    mlw = max(mlw, lyl)
    return (ret, mlw)

  def height(self, songbook, section, song, width):
    return self.height_and_width(songbook, section, song, width)[0]

  def height_and_width(self, songbook, section, song, width):
    st = songbook.style
    rw = self._calculate_repetition_indentation_and_column_width(songbook, section)[1] + st.song_lyrics_repetition_spacing
    ro = st.song_repetition_column_optimal_width + st.song_lyrics_repetition_spacing  # won't be used here
    lh = max(st.song_text_line_height, st.song_chords_line_height if st.song_chords else 0)
    cw = (st.song_chords_column_width + st.song_repetition_chords_spacing) if st.song_chords else 0
    lw = width - rw - cw
    a = 0.
    b = 0.
    for no, line in enumerate(self.lines):
      ls, w = self._processLine(line, songbook, section, song, lw, cw)
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
    rw = self._calculate_repetition_indentation_and_column_width(songbook, section)[1] + st.song_lyrics_repetition_spacing
    ro = st.song_repetition_column_optimal_width + st.song_lyrics_repetition_spacing
    cw = (st.song_chords_column_width + st.song_repetition_chords_spacing) if st.song_chords else 0
    lw = width - rw - cw
    lh = max(st.song_text_line_height, st.song_chords_line_height if st.song_chords else 0)
    lb = [-1.]*len(self.lines)
    ph, mw = self.height_and_width(songbook, section, song, width)
    slin = st.song_text_line_indent
    flin = st.song_text_line_indent_first
    if not sb.is_left_page(c):
      ph = self.height(songbook, section, song, width)
      if ph + st.song_margin_bottom > position:
        song.close_page(c, sb, section, first, last)
        position = sb.height - st.song_margin_top
        first = identifier
    if sb.is_left_page(c):
      margin_left = st.song_margin_outer
      margin_right = st.song_margin_inner
    else:
      margin_left = st.song_margin_inner
      margin_right = st.song_margin_outer
    chpos = sb.width - st.song_chords_column_width - margin_right
    repos = max(chpos - st.song_repetition_chords_spacing - st.song_repetition_column_optimal_width, margin_left + mw)
    flotp = 0
    repin = self._calculate_repetition_indentation_and_column_width(songbook, section)[0]
    song.known_parts.add(self)
    # draw lyrics
    for no, line in enumerate(self.lines):
      ls = self._processLine(line, songbook, section, song, lw, cw)[0]
      # sprawdź czy mamy tyle miejsca na stronie
      lph = len(ls)*lh
      if lph + st.song_margin_bottom > position:
        # make page close:
        # draw repetitions (only visible ones on this page)
        for no2, rep in filter(lambda x: x[1][0] < no and x[1][1] > flotp, enumerate(self.repetitions)):
          beg = max(rep[0], flotp)
          end = min(rep[1], no)
          x = repin[no2]
          lay = lb[beg] - st.song_repetition_line_margin_outer
          lby = (position if end == no else lb[end]) + st.song_repetition_line_margin_outer
          c.line(repos + x+st.song_repeat_margin_left, lay, repos + x+st.song_repeat_margin_left, lby)
          if end == rep[1]:
            c.setFont(st.song_repeat_font_name, st.song_repeat_font_size)
            c.drawString(repos + x + st.song_repeat_margin_left+st.song_repeat_line_text_spacing, lby, st.song_repeat_character+str(rep[2]))
        song.close_page(c, sb, section, first, last)
        position = sb.height - st.song_margin_top
        first = identifier
        flotp = no
        if sb.is_left_page(c):
          margin_left = st.song_margin_outer
          margin_right = st.song_margin_inner
        else:
          margin_left = st.song_margin_inner
          margin_right = st.song_margin_outer
        chpos = sb.width - st.song_chords_column_width - margin_right
        repos = max(chpos - st.song_repetition_chords_spacing - st.song_repetition_column_optimal_width, margin_left + mw)
      # draw part name if defined
      if self.name != '' and no == 0:
        c.setFont(st.song_part_numbering_font_name, st.song_part_numbering_font_size)
        c.drawRightString(margin_left + st.song_part_numbering_width, position - st.song_part_numbering_line_height, self.name)
      # draw lyrics (and chords)
      fst = True
      lb[no] = position
      for lyr, cho in ls:
        strt = margin_left + (flin if fst else slin)
        fst = False
        position -= lh
        c.setFont(st.song_text_font_name, st.song_text_font_size)
        for elt in lyr:
          if type(elt) == lycode.Note:
            c.setFillColorRGB(0.4,0.4,0.4)
          else:
            c.setFillColorRGB(0,0,0)
          pwdt = pdfmetrics.stringWidth(elt.value, st.song_text_font_name, st.song_text_font_size)
          c.drawString(strt, position, elt.value)
          strt += pwdt
        if st.song_chords:
          c.setFont(st.song_chords_font_name, st.song_chords_font_size)
          c.drawString(chpos, position, cho)

    no = len(self.lines)
    c.setFillColorRGB(0,0,0)
    for no2, rep in filter(lambda x: x[1][0] < no and x[1][1] > flotp, enumerate(self.repetitions)):
      beg = max(rep[0], flotp)
      end = min(rep[1], no)
      x = repin[no2]
      lay = lb[beg] - st.song_repetition_line_margin_outer
      lby = (position if end == no else lb[end]) + st.song_repetition_line_margin_outer
      c.line(repos + x+st.song_repeat_margin_left, lay, repos + x+st.song_repeat_margin_left, lby)
      if end == rep[1]:
        c.setFont(st.song_repeat_font_name, st.song_repeat_font_size)
        c.drawString(repos + x +st.song_repeat_margin_left+st.song_repeat_line_text_spacing, lby, st.song_repeat_character+str(rep[2]))
    return (position, first, last)
