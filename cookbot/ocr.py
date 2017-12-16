# -*- coding: utf-8 -*-
import json
import logging
import pytesseract
import re
import sqlite3
from tempfile import NamedTemporaryFile

from PIL import ImageOps

from cookbot.spellcheck import SpellChecker
from cookbot.colorops import histx


pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'


# page segmentation modes
(PSM_OSD_ONLY, PSM_AUTO_OSD, PSM_AUTO_ONLY, PSM_AUTO, PSM_SINGLE_COLUMN,
 PSM_SINGLE_BLOCK_VERT_TEXT, PSM_SINGLE_BLOCK, PSM_SINGLE_LINE,
 PSM_SINGLE_WORD, PSM_CIRCLE_WORD, PSM_SINGLE_CHAR, PSM_SPARSE_TEXT,
 PSM_SPARSE_TEXT_OSD, PSM_COUNT) = range(14)

MODES = {'text': PSM_AUTO, 'line': PSM_SINGLE_LINE, 'word': PSM_SINGLE_WORD}

def _tempfile(delete=True, suffix=''):
    return NamedTemporaryFile(prefix='cookbot_', delete=delete, suffix=suffix)


class OCR(object):
    def __init__(self, db, **opts):
        self.db = db
        self._opts = opts
        self.spellchecker = SpellChecker(db, **opts)

        self.cache = sqlite3.connect('data/OCR_CACHE.db')

    def _tesseract(self, im, mode='text', lang='eng', whitelist='', blacklist='', contrast=False, **opts):
        if contrast:
            im = ImageOps.autocontrast(ImageOps.grayscale(im))

        with _tempfile(suffix='.bmp') as f:
            im.save(f, 'BMP')

            tesseract_config = '--psm ' + str(MODES.get(mode, PSM_AUTO))
            if whitelist:
                tesseract_config += ' -c tessedit_char_whitelist=\'' + whitelist + '\''

            if blacklist:
                tesseract_config += ' -c tessedit_char_blacklist=\'' + blacklist + '\''

            result_text = pytesseract.image_to_string(im, lang='eng', config=tesseract_config)

            return result_text.decode('utf-8')

    def __call__(self, im, p=None, name=False, **kwargs):

        h = histx(im)
        text = self.get_from_cache(h)
        if text is not None:
            logging.info("Cache hit (%r): %r" % (h, text))
            return text

        text = self._tesseract(im, **kwargs)
        logging.debug("Raw text: %r" % text)

        if p != None and p.search(text) != None:
            text = p.search(text).group()
        text = self.spellchecker(text, name)
        logging.debug("Text: %r" % text)

        self.set_to_cache(h, text)

        return text

    def get_from_cache(self, key):
        v = self.cache.execute("SELECT text FROM cache WHERE h = ? LIMIT 1", (key,)).fetchone()

        if v:
            return v[0]

    def set_to_cache(self, key, value):
        self.cache.execute("INSERT INTO cache (h, text) VALUES (?, ?)", (key, value))
        self.cache.commit()
