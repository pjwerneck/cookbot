# -*- coding: utf-8 -*-

import commands
import os
import sys
import subprocess
import tempfile
import math
import json
import time

from cStringIO import StringIO

from PIL import Image, ImageOps, ImageChops


RECIPE_TITLE = (276, 560, 880, 604)

RECIPE_TEXT = (276, 600, 1027, 680)

TICKET_NO = (912, 576, 1009, 599)



try:
    with open('OCR_CACHE.json') as f:
        OCR_CACHE = json.loads(f.read())
except IOError:
    OCR_CACHE = {}



def _ocr(img, config='', delete=False):
    h = hist(img)

    try:
        output = OCR_CACHE[h].encode('utf-8')
        print 'cache hit:', output
    except KeyError:

        w, h = img.size
        
        with tempfile.NamedTemporaryFile(suffix='%sx%s.bmp' % (w, h), dir='./tmp', delete=delete) as f:
            img.save(f, 'BMP')

        status, output = commands.getstatusoutput('tesseract %s stdout %s' % (f.name, config))

    return output


def spell(text):
    text = text.lower()

    for s, v in WORDS:
        text = text.replace(s, v)

    text = text.translate(None, "!\"'").strip()

    return text


class OCR(object):
    def __init__(self, img):
        self.img = img

    def get_title(self):
        im = self.img.crop(RECIPE_TITLE)
        title = spell(_ocr(im, config='-psm 3 -l eng'))
        return title

    def get_text(self):
        im = self.img.crop(RECIPE_TEXT)
        
        return spell(_ocr(im, config='-psm 7 -l eng'))

    def get_ticket_no(self):
        im = self.img.crop(TICKET_NO)
        im = ImageOps.grayscale(im)
        im = ImageOps.autocontrast(im)

        try:
            return int(_ocr(im, config='-psm 8 -l eng digits').strip())
        except ValueError:
            return None



WORDS = [('kefchop', 'ketchup'),
         ('105+', 'just'),
         ('musfard', 'mustard'),
         ('meaf', 'meat'),
         ('tomafoes', 'tomatoes'),
         ('onlg', 'only'),
         ('(heese', 'cheese'),
         ('geese', 'cheese'),
         ('(h)', '(2x)'),
         ('meat {1x}', 'meat (2x)'),
         ('meat (u)', 'meat (2x)'),
         ('meat {3x)', 'meat (3x)'),
         ('meat {3x}', 'meat (3x)'),
         ('lehuce', 'lettuce'),
         ('lehoce', 'lettuce'),
         ('(hives', 'chives'),
         ('buffer', 'butter'),
         ('meai', 'meat'),
         ('tomafo\xe2\x80\x98\nonionsns', 'tomatoes, onions'),
         ('jalapeno:', 'jalapenos'),
         ('sah\xe2\x80\x98', 'salt'),
         ('sal?', 'salt'),
         ('buh\xe2\x80\x98er', 'butter'),
         ('c innamon', 'cinnamon'),
         ('305+', 'just'),
         ('bail', 'boil'),
         ('(lichen', 'chicken'),
         ('le\xef\xac\x81oce', 'lettuce'),
         ('diel', 'diet'),
         ('chocolafe', 'chocolate'),
         ('cherrg', 'cherry'),
         ('(hocolafe', 'chocolate'),
         ('(herrg', 'cherry'),
         ('(ola', 'cola'),
         ('flavor blur', 'flavor blast'),
         ('die?', 'diet'),
         ('dief', 'diet'),
         ('wh\xef\xac\x81e', 'white'),
         ('\xe2\x80\x98i sugars', '4 sugars'),
         ('6r\xc3\xa9ens', 'greens'),
         ('carrofs', 'carrots'),
         ('(arrofs', 'carrots'),
         ('unh\xc2\xbb', 'with'),
         ('wi\xef\xac\x82~', 'with'),
         ('53\xe2\x80\x9d', 'salt'),
         ('everg\xef\xac\x82nmg', 'everything'),
         ('evergfhing', 'everything'),
         ('shll', 'still'),
         ('haonh', 'haunts'),
         ('sexg', 'sexy'),
         ('eges', 'eyes'),
         ('fancg', 'fancy'),
         ('bm‘', 'but'),
         ('buf', 'but'),
         ('musfache', 'mustache'),
         ('{', '('),
         ('}', ')'),
         ('(l)', '(1)'),
         ('tona', 'tuna'),
         ('t0na', 'tuna'),
         ('(z)', '(2)'),
         ('018+', 'diet'),
         ('vinaigre\xef\xac\x81e', 'vinaigrette'),
         ('\xe2\x80\x9ccase', 'cheese'),
         ('(roufons', 'croutons'),
         ('evergthing', 'everything'),
         ('anchovaes', 'anchovies'),
         ('and-owes', 'anchovies'),
         ('sums cheese', 'swissc'),
         ('sunss cheese', 'swissc'),
         ('swiss cheese', 'swissc'),
         ('\xe2\x80\x9d', '"'),
         ('great?', 'great'),
         ('onie-ns', 'onions'),         
         ('wllemon', 'w/lemon'),
         ("boil tray", "bail tray"),
         ('wifh', 'with'),
         ('z sugars', '2 sugars'),
         ('w/oueso', 'w/queso'),
         ('with \xe2\x80\x981 sugars', 'with 4 sugars'),

         ]




def main():
    fname = sys.argv[1]

    im = Image.open(fname)

    ocr = OCR(im)

    print repr(ocr.get_title())
    print '-' * 80

    print repr(ocr.get_text())
    print '-' * 80

    print repr(ocr.get_ticket_no())
    print '-' * 80

    print repr(ocr.get_orders())
    print '-' * 80



def hist(im):
    h = im.histogram()
    return repr(math.sqrt(sum([(x**2) * (i+1) for (i, x) in enumerate(h)]) / len(h)))


def build_opt():

    cache = {}

    for f in os.listdir('tmp'):
        if not f.endswith('bmp'):
            continue

        p = os.path.join('tmp', f)

        im = Image.open(p)

        if im.size != (604, 44):
            continue

        config = '-psm 3 -l eng'

        h = hist(im)

        print p
        print repr(h)
        status, ocr_output = commands.getstatusoutput('tesseract %s stdout %s' % (p, config))

        if not ocr_output:
            continue

        try:
            output = cache[h]
            assert output == ocr_output, f
            print 'cache hit', repr(output)
        except KeyError:
            cache[h] = ocr_output
            print 'cached', repr(ocr_output)

        print '-' * 80

    with open('OCR_CACHE.json', 'w') as f:
        f.write(json.dumps(cache))
    


if __name__ == '__main__':
    #main()

    build_opt()
