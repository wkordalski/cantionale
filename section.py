from parser import parse_file
from song import Song

import os

class Section:
  def __init__(self, f):
    self.title = ''
    self.prefix = ''
    self.description = ''
    self.songs = []

    config = parse_file(f)
    directory = '.'

    if 'title' in config: self.title = config.pop('title')
    else: raise ContentError("Section attribute 'title' not specified.", f.name)

    if 'prefix' in config: self.prefix = config.pop('prefix')

    if 'directory' in config: directory = config.pop('directory')
    if 'description' in config: self.description = config.pop('description')
    if 'contents' in config:
      files = config.pop('contents').split(sep='\n')
      for fn in files:
        fname = fn.strip()
        if fname == '': continue
        fl = open(directory + os.sep + fname, encoding='utf-8')
        s = Song(fl)
        fl.close()
        self.songs.append(s)

    if len(config) > 0:
      print("Unused labels in "+f.name+": " + str(config.keys()), file=sys.stderr)

  def index(self, number):
    if self.prefix == '':
      return str(number)
    else:
      return self.prefix + ' ' + str(number)

  def draw(self, canvas, songbook):
    c = canvas
    sb = songbook
    # draw name
    # title
    wrk_widt = sb.width - sb.style.section_margin_left - sb.style.section_margin_right
    lines = self.title.strip().split(sep='\n')
    fnt_size = sb.style.section_title_font_size
    lin_heig = sb.style.section_title_line_height
    c.setFont(sb.style.section_title_font_name, fnt_size)
    pos = sb.height - sb.style.section_margin_top
    for line in lines:
      pos -= lin_heig
      c.drawCentredString(sb.width/2.0, pos, line)

    if sb.style.section_description and self.description != '':
      pos -= sb.style.section_title_description_spacing
      fnt_name = sb.style.section_description_font_name
      fnt_size = sb.style.section_description_font_size
      lines = [ a for b in [ [''] if s == '' else simpleSplit(s, fnt_name, fnt_size, wrk_widt) for s in self.description.strip().split(sep='\n')] for a in b ]
      lin_heig = sb.style.section_description_line_height
      c.setFont(fnt_name, fnt_size)
      for line in lines:
        pos -= lin_heig
        if pos <= sb.style.section_margin_bottom:
          c.showPage()
          c.setFont(fnt_name, fnt_size)
          pos = sb.height - sb.style.section_margin_top - lin_heig
        c.drawString(sb.style.section_margin_left, pos, line)

    pos -= sb.style.section_description_song_spacing
    idx = 0
    fst = self.index(1)
    lst = ''
    for song in self.songs:
      idx += 1
      (pos, fst, lst) = song.draw(c, sb, self, pos, self.index(idx), fst, lst)
      pos -= sb.style.section_song_song_spacing
    if len(self.songs) > 0: self.close_page(c, sb, fst, lst)
    if songbook.is_left_page(c):
      canvas.showPage()
    pass

  def close_page(self, canvas, songbook, left, right):
    # use canvas.getPageNumber() to know if we need to print left or right
    st = songbook.style
    num_heig = songbook.height - songbook.style.section_numbering_height - songbook.style.section_header_numbering_line_height
    num_edgd = songbook.style.section_numbering_edge_distance
    pag_widt = songbook.width
    canvas.setFont(st.section_header_numbering_font_name, st.section_header_numbering_font_size)
    if songbook.style.section_numbering_both:
      # right and left printed
      canvas.drawString(num_edgd, num_heig, left)
      canvas.drawRightString(songbook.width - num_edgd, num_heig, right)
    elif canvas.getPageNumber() %2 == 1:
      # right page => print right
      canvas.drawRightString(songbook.width - num_edgd, num_heig, right)
    else:
      # left page => print left
      canvas.drawString(num_edgd, num_heig, left)
    # TODO: draw some line under/over numbering?
    canvas.showPage()
    pass
