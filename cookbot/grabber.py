# -*- coding: utf-8 -*-

"""
cookbot.grabber

This module should hold all platform-specific code for capturing
windows and sending input.

"""

import ctypes
import os
import sys

from PIL import Image



if sys.platform.startswith('linux'):

    _libpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_grabber.so')
    _grabber = ctypes.CDLL(_libpath)


    def grab(self, x, y, w, h):
        size = w * h
        objlength = size * 3

        grab.getScreen.argtypes = []
        result = (ctypes.c_ubyte*objlength)()

        grab.getScreen(x, y, w, h, result)
        return Image.frombuffer('RGB', (w, h), result, 'raw', 'RGB', 0, 1)


    @contextmanager
    def _refresh_gtk():
        while gtk.events_pending():
            gtk.main_iteration()

        yield


    def





class Grabber(object):

    def __init__(self):
        self._grab = ctypes.CDLL(_libpath)



if __name__ == '__main__':
    x, y, w, h = (635, 76, 1280, 720)

    g = Grabber()


    #im = grab_screen(0, 0, 1920, 1080)
    im = grab_screen(x, y, w, h)

    im.show()
