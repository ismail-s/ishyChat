"""Hyperlink manager code to add hyperlink support to tkinter view."""
# This code is a modified version of the code at :
# http://effbot.org/zone/tkinter-text-hyperlink.htm.
# This code is in the public domain, according to:
# http://effbot.org/zone/copyright.htm.
# Just in case, however, here's a license thing from:
# http://effbot.org/zone/copyright.htm.

# Copyright © 1995-2013 by Fredrik Lundh

# By obtaining, using, and/or copying this software and/or its associated
# documentation, you agree that you have read, understood, and will comply
# with the following terms and conditions:

# Permission to use, copy, modify, and distribute this software and its
# associated documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appears in all copies, and that
# both that copyright notice and this permission notice appear in supporting
# documentation, and that the name of Secret Labs AB or the author not be
# used in advertising or publicity pertaining to distribution of the software
# without specific, written prior permission.

# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO
# THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import webbrowser, sys

if sys.version_info >= (3, 0):
      from tkinter import CURRENT
else:
      from Tkinter import CURRENT

class HyperlinkManager(object):

      def __init__(self, text):

            self.text = text

            self.text.tag_config("hyper", foreground="blue", underline=1)

            self.text.tag_bind("hyper", "<Enter>", self._enter)
            self.text.tag_bind("hyper", "<Leave>", self._leave)
            self.text.tag_bind("hyper", "<Button-1>", self._click)

            self.reset()

      def reset(self):
            self.links = {}
      
      def add(self, link):
          # add an action to the manager.  returns tags to use in
          # associated text widget
            tag = "hyper-{}".format(len(self.links))
            self.links[tag] = link
            return "hyper", tag
      
      def _enter(self, event):
            self.text.config(cursor="hand2")
      
      def _leave(self, event):
            self.text.config(cursor="")
      
      def _click(self, event):
            for tag in self.text.tag_names(CURRENT):
                if tag[:6] == "hyper-": # 6 is used as 6 == len('hyper-')
                  webbrowser.open(self.links[tag])
                  return
