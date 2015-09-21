import lycode

from reportlab.pdfbase import pdfmetrics

class InstrumentalPart:
  def __init__(self, part, song):
    self.body = part.body
    self.lines = []
    part.consumeLines(self.lines, [])

  # splits line if needed and returns minimal lyrics width for these lines
  def _processLine(self, line, songbook, section, song, instrumental_width, chords_width, do_chords = True):
    # split data on lines
    lyrics_width = instrumental_width
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
    lyfn = st.song_instrumental_font_name
    lyfs = st.song_instrumental_font_size
    chfn = st.song_chords_font_name
    chfs = st.song_chords_font_size
    slin = st.song_instrumental_line_indent
    flin = st.song_instrumental_line_indent_first
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
    lh = max(st.song_text_line_height, st.song_chords_line_height if st.song_chords else 0)
    cw = (st.song_chords_column_width + st.song_repetition_chords_spacing) if st.song_chords else 0
    lw = width - cw
    a = 0.
    b = 0.
    for no, line in enumerate(self.lines):
      ls, w = self._processLine(line, songbook, section, song, lw, cw)
      a += len(ls)*lh
      b = max(b, w)
    return (a, b)

  def is_instrumental(self):
    return True

  def draw(self, canvas, songbook, section, song, position, identifier, first, last):
    # czy mamy gdzie narysować sekcje (jeśli prawa strona)
    sb = songbook
    c = canvas
    st = sb.style
    width = sb.width - st.song_margin_inner - st.song_margin_outer
    cw = (st.song_chords_column_width + st.song_repetition_chords_spacing) if st.song_chords else 0
    lw = width - cw
    lh = max(st.song_instrumental_line_height, st.song_chords_line_height if st.song_chords else 0)
    ph, mw = self.height_and_width(songbook, section, song, width)
    slin = st.song_instrumental_line_indent
    flin = st.song_instrumental_line_indent_first
    if not sb.is_left_page(c):
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
    flotp = 0
    # draw notes
    for no, line in enumerate(self.lines):
      ls = self._processLine(line, songbook, section, song, lw, cw)[0]
      # sprawdź czy mamy tyle miejsca na stronie
      lph = len(ls)*lh
      if lph + st.song_margin_bottom > position:
        # make page close:
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
      # draw lyrics (and chords)
      fst = True
      for lyr, cho in ls:
        strt = margin_left + (flin if fst else slin)
        fst = False
        position -= lh
        c.setFont(st.song_instrumental_font_name, st.song_instrumental_font_size)
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
    c.setFillColorRGB(0,0,0)
    return (position, first, last)
