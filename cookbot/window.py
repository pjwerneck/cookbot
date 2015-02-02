# -*- coding: utf-8 -*-
import os
import sys
import time
import string

import gtk
import wnck
from PIL import Image
from pykeyboard import PyKeyboard

from cookbot.colorops import rgb_to_hsv, rgb_delta, delta_hist
from cookbot.ocr import OCR


if sys.platform.startswith('linux'):
    import ctypes


TIMER_BOX = [(219, 72 + i*60, 241, 72 + i*60 + 56) for i in xrange(8)]

ACTIVE_BOX = [(199, 72 + i*60, 247, 72 + i*60 + 56) for i in xrange(8)]

OUTLINES = [(248, 72 + i*60, 249, 72 + i*60 + 56) for i in xrange(8)]


RECIPE_TITLE = (276, 560, 880, 604)

RECIPE_TEXT = (276, 604, 1027, 670)

TICKET_NO = (912, 576, 1009, 599)

#CANARY_PX = (481, 36)
CANARY_PX = (66, 679)

ROSTER = [(24, 90),
          (24, 164),
          (24, 216),
          (24, 285),
          (24, 324),
          (24, 398),
          (24, 461),
          (24, 516),
          ]


def _getcolors(im, color):
    n = im.size[0] * im.size[1]
    return {k:v for (v, k) in im.getcolors(n)}.get(color, 0)


def yellow(im):
    return _getcolors(im, (255, 242, 0))



class BaseWindow(object):
    def __init__(self, **opts):
        self._opts = opts

        self._window = None
        self._img = None

        self._title = None
        self._text = None
        self._ticket_no = None
        self._orders = None

        self.k = PyKeyboard()
        self.ocr = OCR(**opts)

    def get_window(self):
        raise NotImplementedError

    def focus(self):
        raise NotImplementedError

    def grab(self, *args):
        raise NotImplementedError

    def capture(self, bbox=None):
        x, y, w, h = self.get_coords()

        img = self.grab(x, y, w, h)

        if bbox:
            img = img.crop(bbox)

        return img

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError(attr)

        # maybe this is too much magic?
        value = getattr(self, '_' + attr)

        if value is None:
            value = getattr(self, 'get_' + attr)()
            setattr(self, '_' + attr, value)

        return value

    def refresh(self, img=None):
        t = time.time()

        self._img = img or self.capture()

        self._title = None
        self._text = None
        self._orders = None
        self._ticket_no = None
        self._active = None

    def get_title(self):
        # returns the recipe title
        return self.ocr(self._img.crop(RECIPE_TITLE), mode='line',
                        whitelist=string.letters + '()')

    def get_text(self):
        # returns the recipe text
        return self.ocr(self._img.crop(RECIPE_TEXT), mode='text',
                        whitelist=string.letters + string.digits + ',./!?()')

    def get_ticket_no(self):
        # returns the number of the ticket, or None
        try:
            return int(self.ocr(self._img.crop(TICKET_NO), mode='word',
                                whitelist=string.digits,
                                contrast=True))
        except ValueError:
            return None

    def get_orders(self):
        # returns the complete status for each slot
        n = range(1, 9)
        roster = self.get_roster()
        outlines, x_factor = self.get_outlines(roster)

        return zip(n, roster, outlines, x_factor)

    def get_outlines(self, roster=None):
        # returns the actual state for each slot, and how far they
        # receded to the left
        if roster is None:
            roster = [True] * 8

        outlines = []
        x_factor = []

        for i, v in enumerate(roster):
            if not v:
                outlines.append(None)
                x_factor.append(None)
                continue

            bbox = OUTLINES[i]
            x1, y1, x2, y2 = bbox

            out = _identify_outline(self._img.crop(bbox))

            if out is not None:
                outlines.append(out)
                x_factor.append(x2)
                continue

            while x1 > 60:
                x1 -= 1
                x2 -= 1

                out = _identify_outline(self._img.crop((x1, y1, x2, y2)))

                if out is not None:
                    outlines.append(out)
                    x_factor.append(x2)
                    break

            else:
                outlines.append(None)
                x_factor.append(None)


        assert len(outlines) == 8
        assert len(x_factor) == 8

        return outlines, x_factor

    def get_roster(self):
        # returns the state for each slot, if highlighted or not
        roster = [rgb_delta(self._img.getpixel(b), (255, 255, 255)) < 1 for b in ROSTER]
        assert len(roster) == 8
        return roster

    @property
    def canary(self):
        # this is a 'canary' pixel that should be immutable during normal
        # gameplay. This is used to avoid doing something wrong during
        # the screen flashes, like Rush Hour.
        return self._img.getpixel(CANARY_PX)

    def at_kitchen(self):
        # true if at the kitchen preparation screen
        return self._img.getpixel((840, 164)) == (37, 44, 139)

    def at_grill(self):
        # true if at the grill/boiler screen
        p = self._img.getpixel((394, 283))
        return p in {(134, 134, 132), (106, 106, 104), (95, 94, 100), (85, 83, 89)}

    def key(self, k, d=0.1):
        self.k.press_key(k)
        time.sleep(self._opts['key_delay'])
        self.k.release_key(k)
        time.sleep(self._opts['key_delay'])

    def escape(self):
        # used to pause the game on bot errors
        self.key(self.k.escape_key)

    def change_recipe(self):
        # for testing recipes. Change to the next recipe.
        self.key(self.k.control_key)
        time.sleep(self._opts['loop_delay'])

    def order_ok(self):
        # for testing recipes. Check if the order was successul.
        SMILEY_BBOX = (61, 72, 221, 128)
        return max([yellow(self.capture(SMILEY_BBOX)) for x in xrange(20)]) > 800





def _identify_outline(im):
    t = im.size[0] * im.size[1]

    colors = im.getcolors(t)

    n, c = max(colors, key=lambda x: x[0])

    f = n/float(t)

    if f < 0.8:
        return None

    if rgb_delta(c, (0, 0, 0)) < 1:
        return 'new'

    if rgb_delta(c, (79, 79, 79)) < 1:
        return 'active'

    if rgb_delta(c, (114, 114, 114)) < 1:
        return 'cooking'

    if rgb_delta(c, (190, 0, 0)) < 1:
        return 'burning'

    if rgb_delta(c, (255, 255, 64)) < 1:
        return 'ready'

    if rgb_delta(c, (106, 255, 255)) < 1:
        return 'waiting'

    h, s, v = rgb_to_hsv(*c)

    if h == 0.5 and s == 0 and v > 100:
        return 'waiting'

    if h == 1/6.0 and s == 0 and v > 100:
        return 'ready'

    #raise RuntimeError("Cannot identify outline")


class GTKWindow(BaseWindow):

    _libpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_grabber.so')
    _grabber = ctypes.CDLL(_libpath)

    def grab(self, x, y, w, h):
        size = w * h
        objlength = size * 3

        self._grabber.get_screen.argtypes = []
        result = (ctypes.c_ubyte*objlength)()

        self._grabber.get_screen(x, y, w, h, result)
        return Image.frombuffer('RGB', (w, h), result, 'raw', 'RGB', 0, 1)

    def focus(self):
        self.window.activate(int(time.time()))

    def get_window(self):
        screen = wnck.screen_get_default()

        # flush gtk events
        while gtk.events_pending():
            gtk.main_iteration()

        # find the game window
        for window in screen.get_windows():
            if window.get_name() == 'CookServeDelicious':
                return window

        raise RuntimeError("Can't find game window")

    def get_coords(self):
        x, y, w, h = self.window.get_geometry()

        # remove the title bar
        h -= 28
        y += 28

        return x, y, w, h



if sys.platform.startswith('linux'):
    GameWindow = GTKWindow

else:
    raise NotImplementedError("Platform not supported: %s" % sys.platform)



if __name__ == '__main__':
    win = GameWindow()

    while 1:
        win.refresh()
        win.get_outlines()
