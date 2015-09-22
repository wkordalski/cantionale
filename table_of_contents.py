
class TableOfContents:
  def __init__(self, songbook, params):
    self.title = ''
    self.filter = lambda x : True
    if 'title' in params: self.title = params['title']
    if 'filter' in params: self.filter = params['filter']

  def draw(self, canvas, songbook):
    sb = songbook
    st = sb.style
    c = canvas
    wdt = sb.width
    position = sb.height - st.toc_margin_top
    c.setFont(st.toc_title_font_name, st.toc_title_font_size)
    for line in self.title.strip().split(sep='\n'):
      position -= st.toc_title_line_height
      c.drawCentredString(wdt/2, position, line)

    for section in songbook.sections:
      position -= st.toc_section_section_spacing
      position = self.draw_section(canvas, songbook, section, position)

    c.showPage()
    if sb.is_left_page(c):
      c.showPage()

  def draw_section(self, canvas, songbook, section, position):
    sb = songbook
    st = sb.style
    c = canvas
    sclh = st.toc_section_title_line_height
    if 2 * sclh + st.toc_margin_bottom > position:
      c.showPage()
      position = sb.height - st.toc_margin_top
    if sb.is_left_page(c):
      margin_left = st.toc_margin_outer
      margin_right = st.toc_margin_inner
    else:
      margin_left = st.toc_margin_inner
      margin_right = st.toc_margin_outer
    position -= sclh
    c.setFont(st.toc_section_title_font_name, st.toc_section_title_font_size)
    c.drawString(margin_left + st.toc_section_title_indent, position, section.title)
    c.drawRightString(margin_left + st.toc_section_prefix_indent, position, section.prefix)
    position -= st.toc_section_title_song_spacing
    lh = st.toc_song_line_height
    for no, song in filter(self.filter, enumerate(section.songs)):
      if lh + st.toc_margin_bottom > position:
        c.showPage()
        position = sb.height - st.toc_margin_top
        if sb.is_left_page(c):
          margin_left = st.toc_margin_outer
          margin_right = st.toc_margin_inner
        else:
          margin_left = st.toc_margin_inner
          margin_right = st.toc_margin_outer
      position -= st.toc_song_song_spacing
      position -= lh
      c.setFont(st.toc_song_number_font_name, st.toc_song_number_font_size)
      c.drawRightString(st.toc_song_number_indent + margin_left, position, str(no+1))
      c.setFont(st.toc_song_title_font_name, st.toc_song_title_font_size)
      c.drawString(st.toc_song_title_indent + margin_left, position, song.title)
    return position
