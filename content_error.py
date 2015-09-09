# -*- coding: utf-8 -*-

class ContentError(Exception):
  def __init__(self, message, filename):
    self.message = message
    self.filename = filename

  def __str__(self):
    return self.message + ' [' + self.filename + ']'

