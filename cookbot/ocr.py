# -*- coding: utf-8 -*-
import ctypes
import json
import logging
from tempfile import NamedTemporaryFile

from PIL import ImageOps

from cookbot.spellcheck import spellcheck


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
    def __init__(self, **opts):
        pass

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
        text = self._tesseract(im, **kwargs)
        logging.debug("Raw text: %r" % text)

        text = spellcheck(text)
        logging.debug("Text: %r" % text)

        return text

    def save_cache(self):
        with open('OCR_CACHE.json', 'w') as f:
            f.write(json.dumps(self._cache))
