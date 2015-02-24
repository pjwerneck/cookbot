# -*- coding: utf-8 -*-
import ctypes
import json
import logging
import sqlite3
from tempfile import NamedTemporaryFile

from PIL import ImageOps

from cookbot.spellcheck import SpellChecker
from cookbot.colorops import histx


libname = '/usr/lib/libtesseract.so.3'
TESSDATA_PREFIX = '/usr/share/tesseract-ocr'

libtesseract = ctypes.cdll.LoadLibrary(libname)

# page segmentation modes
(PSM_OSD_ONLY, PSM_AUTO_OSD, PSM_AUTO_ONLY, PSM_AUTO, PSM_SINGLE_COLUMN,
 PSM_SINGLE_BLOCK_VERT_TEXT, PSM_SINGLE_BLOCK, PSM_SINGLE_LINE,
 PSM_SINGLE_WORD, PSM_CIRCLE_WORD, PSM_SINGLE_CHAR, PSM_SPARSE_TEXT,
 PSM_SPARSE_TEXT_OSD, PSM_COUNT) = map(ctypes.c_int, xrange(14))

MODES = {'text': PSM_AUTO, 'line': PSM_SINGLE_LINE, 'word': PSM_SINGLE_WORD}


def _tempfile(delete=True, suffix=''):
    return NamedTemporaryFile(prefix='cookbot_', dir='./tmp', delete=delete, suffix=suffix)


class OCR(object):
    def __init__(self, db, **opts):
        self.db = db
        self._opts = opts
        self.spellchecker = SpellChecker(db, **opts)

        self.cache = sqlite3.connect('data/OCR_CACHE.db')

    def _tesseract(self, im, mode='text', lang='eng', whitelist='', blacklist='', contrast=False, **opts):
        api = libtesseract.TessBaseAPICreate()

        if contrast:
            im = ImageOps.autocontrast(ImageOps.grayscale(im))

        with _tempfile(suffix='.bmp') as f:
            im.save(f, 'BMP')

            try:
                rc = libtesseract.TessBaseAPIInit3(api, TESSDATA_PREFIX, lang)
                if rc:
                    raise RuntimeError("Could not initialize tesseract.")

                if whitelist:
                    libtesseract.TessBaseAPISetVariable(api, "tessedit_char_whitelist", whitelist)

                if blacklist:
                    libtesseract.TessBaseAPISetVariable(api, "tessedit_char_blacklist", blacklist)

                psm = MODES.get(mode, PSM_AUTO)

                libtesseract.TessBaseAPISetPageSegMode(api, psm)

                text_out = libtesseract.TessBaseAPIProcessPages(api, f.name, None, 0)

                result_text = ctypes.string_at(text_out)

                return result_text.decode('utf-8')

            finally:
                libtesseract.TessBaseAPIDelete(api)

    def __call__(self, im, contrast=False, **kwargs):

        h = histx(im)
        text = self.get_from_cache(h)
        if text is not None:
            logging.info("Cache hit (%r): %r" % (h, text))
            return text

        text = self._tesseract(im, **kwargs)
        logging.debug("Raw text: %r" % text)

        text = self.spellchecker(text)
        logging.debug("Text: %r" % text)

        self.set_to_cache(h, text)

        return text

    def get_from_cache(self, key):
        v = self.cache.execute("select text from cache where h = ? limit 1", (key,)).fetchone()

        if v:
            return v[0]

    def set_to_cache(self, key, value):
        self.cache.execute("insert into cache (h, text) values (?, ?)", (key, value))
        self.cache.commit()
