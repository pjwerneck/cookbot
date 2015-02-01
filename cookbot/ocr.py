# -*- coding: utf-8 -*-
import commands
import json
import logging
import math
import os
from tempfile import NamedTemporaryFile

from PIL import Image, ImageOps

from cookbot.spellcheck import spellcheck
from cookbot.colorops import histx


# Tesseract is much faster and easier since it outputs text to stdout,
# so we use it to do the heavy-lifting and recognize the recipe title
# and ticket number and other small texts.

# Cuneiform is slower, but a lot more accurate when recognizing the
# fancy font used on the recipe text, but that's needed only for
# coffee and robbery_id.


def tempfile(delete=False):
    return NamedTemporaryFile(prefix='cookbot_', dir='./tmp', delete=delete)


def ocr_tesseract(img, format='text', digits=False):
    with tempfile() as f:
        img.save(f, 'BMP')

        config = ['-l eng']
        config.append({'text': '-psm 3', 'line': '-psm 7', 'word': '-psm 8'}[format])

        if digits:
            config.append('digits')

        config = ' '.join(config)

        status, output = commands.getstatusoutput('tesseract {0} stdout {1}'.format(f.name, config))
        assert status == 0
        return output


def ocr_cuneiform(img, format='text', digits=False):
    with tempfile() as f, tempfile() as out:
        #img = img.resize((img.size[0]*3, img.size[1]*3), Image.ANTIALIAS)
        img.save(f, 'BMP')
        f.close()

        status, output = commands.getstatusoutput('cuneiform -l eng -f text -o {1} {0}'.format(f.name, out.name))

        assert status == 0, (output, f.name)

        out.seek(0)
        output = out.read()

        return output


class OCR(object):

    def __init__(self):
        try:
            with open('OCR_CACHE.json') as f:
                self._cache = json.loads(f.read())
        except IOError:
            self._cache = {}

    def _ocr(self, img, format='text', digits=False, contrast=False, cache=True):

        h = repr(histx(img))

        if cache:
            try:
                output = self._cache[h].encode('utf-8')
                logging.info("Cache hit: %r" % output)
                return output
            except KeyError:
                pass

        if contrast:
            img = ImageOps.autocontrast(ImageOps.grayscale(img))

        if format == 'text':
            return ocr_cuneiform(img)

        else:
            return ocr_tesseract(img, format=format, digits=digits)

    def get_line(self, im, **kwargs):
        return spellcheck(self._ocr(im, format='line', **kwargs))

    def get_text(self, im, **kwargs):
        return spellcheck(self._ocr(im, format='text', contrast=True, **kwargs))

    def get_digits(self, im, **kwargs):
        try:
            return str(int(self._ocr(im, format='word', digits=True, **kwargs).strip()))
        except ValueError:
            return None


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

        h = repr(histx(im))

        print p
        print h
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
