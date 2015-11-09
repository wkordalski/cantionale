# -*- coding: utf-8 -*-

class SongView:
	def __init__(self, identifier, song, section_view, style):
		self.id = identifier
		self.song = song
		self.secv = section_view
		self.style = style

	def getCanvas(self):
		return self.secv.getCanvas()
