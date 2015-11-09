# -*- coding: utf-8 -*-

from reportlab.pdfgen import canvas

class Canvas(canvas.Canvas):
	def isLeftPage(self):
		return (self.getPageNumber()%2 == 0)
	def isRightPage(self):
		return (self.getPageNumber()%2 == 1)
