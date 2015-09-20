from content_error import ContentError

import lycode


from reportlab.pdfbase import pdfmetrics

class ReferencingPart:
  def __init__(self, part, song):
    self.rname = part.options.strip()
    self.referee = song.part_by_name.get(self.rname, None)
    if not self.referee: raise ContentError("Referencing unknown part (%s)."%self.rname, song.filename)
    if lycode.strip(part.body, True) != []: raise ContentError("Referencing part can't have body.", song.filename)

  def height(self, songbook, section, song, width):
    if self.referee in song.known_parts:
      return songbook.style.song_referencing_text_line_height
    else:
      return self.referee.height(songbook, section, song, width)

  def is_instrumental(self):
    return False

  def draw(self, canvas, songbook, section, song, position, identifier, first, last):
    if self.referee in song.known_parts:
      # draw part name if defined
      sb = songbook
      st = sb.style
      c = canvas
      if sb.is_left_page(c):
        margin_left = st.song_margin_outer
        margin_right = st.song_margin_inner
      else:
        margin_left = st.song_margin_inner
        margin_right = st.song_margin_outer
      if self.rname != '':
        c.setFont(st.song_part_numbering_font_name, st.song_part_numbering_font_size)
        c.drawRightString(margin_left + st.song_part_numbering_width, position - st.song_part_numbering_line_height, self.rname)
      if self.referee.lines != []:
        line = self.referee.lines[0]
        width = sb.width - st.song_margin_inner - st.song_margin_outer - ((st.song_chords_column_width + st.song_repetition_chords_spacing) if st.song_chords else 0)
        td = pdfmetrics.stringWidth('...', st.song_referencing_text_font_name, st.song_referencing_text_font_size)
        ls = self.referee._processLine(line, songbook, section, song, width-td, 0, False)[0]
        if ls != []:
          tp = ls[0][0].strip().strip(st.song_referencing_stripped_characters) + '...'
          c.setFont(st.song_referencing_text_font_name, st.song_referencing_text_font_size)
          strt = margin_left + st.song_referencing_text_line_indent
          lh = songbook.style.song_referencing_text_line_height
          position -= lh
          c.drawString(strt, position, tp)
          return (position, first, last)
    else:
      return self.referee.draw(canvas, songbook, section, song, position, identifier, first, last)
