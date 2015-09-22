
class TitleIndex:
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
		position = sb.height - st.title_index_margin_top
		c.setFont(st.title_index_title_font_name, st.title_index_title_font_size)
		for line in self.title.strip().split(sep='\n'):
			position -= st.title_index_title_line_height
			c.drawCentredString(wdt/2, position, line)

		position -= st.title_index_title_song_spacing

		songs = []
		for section in songbook.sections:
			for no, song in enumerate(section.songs):
				if self.filter((no,song)):
					songs.append((song.title, section.index(no+1)))
		songs.sort()

		if sb.is_left_page(c):
			margin_left = st.title_index_margin_outer
			margin_right = st.title_index_margin_inner
		else:
			margin_left = st.toc_margin_inner
			margin_right = st.toc_margin_outer

		lh = st.title_index_song_line_height
		for title, index in songs:
			if lh + st.title_index_margin_bottom > position:
				c.showPage()
				position = sb.height - st.title_index_margin_top
				if sb.is_left_page(c):
					margin_left = st.title_index_margin_outer
					margin_right = st.title_index_margin_inner
				else:
					margin_left = st.title_index_margin_inner
					margin_right = st.title_index_margin_outer
			position -= st.title_index_song_song_spacing
			position -= lh
			c.setFont(st.title_index_song_number_font_name, st.title_index_song_number_font_size)
			c.drawRightString(st.title_index_song_number_indent + margin_left, position, index)
			c.setFont(st.title_index_song_title_font_name, st.title_index_song_title_font_size)
			c.drawString(st.title_index_song_title_indent + margin_left, position, title)

		c.showPage()
		if sb.is_left_page(c):
			c.showPage()
