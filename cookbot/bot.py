# -*- coding: utf-8 -*-

import commands
import gtk
import itertools
import math
import os
import re
import time
import wnck

from contextlib import contextmanager

from cookbot.ocr import OCR
from cookbot.recipes import RECIPES, FOODS, FINISH_AT, COOKING_TIME, RecipesBase
from cookbot.interpreter import parser
from cookbot.window import GameWindow

from StringIO import StringIO



class CookBot(object):
    def __init__(self, **opts):

        opts.setdefault('auto_order', False)
        opts.setdefault('test_recipes', False)

        self._opts = opts

        self.window = GameWindow()
        self.recipes = RecipesBase()

        self._running = False

        self._log = {}

        self._accepted = {}
        self._received = {}
        self._cooking = {}
        self._waiting = {}
        self._ready = {}

        self._errors = []
        self._canary = []

    def set_opts(self, **kwargs):
        self._opts.update(kwargs)

    def run(self):
        self._running = True

        self.window.focus()

        while self._running:
            self.window.refresh()

            if self._opts['auto_order']:
                self._canary.append(self.window.canary)
                del self._canary[:-2]

                if len(set(self._canary)) > 1:
                    print 'canary died. waiting...'
                    time.sleep(0.1)
                    continue

            if (self._opts['auto_order'] or self._opts['test_recipes']) and self.window.orders:
                self.order()

            if self.window.at_kitchen():
                self.prepare()

            time.sleep(0.1)

    def execute_recipe(self, s):
        for cmd in parser.parse(s):
            cmd(self.window)

        self.check_result('p')

    def get_food(self):
        # XXX: ugly hack needed to circumvent equal names for some foods
        if self.window.title == 'the mix':
            p = self.window._img.getpixel((394, 283))

            if p == (21, 18, 16):
                self.window._title += ' sushi'

            elif p == (47, 91, 21):
                self.window._title += ' salad'

            elif p == (134, 134, 132):
                self.window._title += ' burger'

            elif p == (148, 179, 229):
                self.window._title += ' burger'

            elif p == (129, 75, 68):
                self.window._title += ' burger'

            else:
                raise NotImplementedError("the mix: %r" % (p,))

        try:
            food = FOODS[self.window.title]
            if self.window.at_grill():
                food = food + '_grill'
            return food
        except KeyError:
            pass

        if self.window.title.startswith('robbery'):
            return 'robbery'

        if self._errors:
            print self.window.text
            raise RuntimeError("Couldn't identify task %r" % self.window.title)
        else:
            self._errors.append(self.window.title)

    def accept(self, n):
        # accept only if seen at least once before and not accepted within the last second
        self._accepted.setdefault(n, time.time())

        if time.time() - self._accepted[n] > 0.5:
            print 'accept', n

            if self._opts['test_recipes']:
                self.window.change_recipe()

            self.window.key(str(n))
            del self._accepted[n]
            del self._received[n]
            return True

        return False

    def ready(self, n):
        # only ready if ready for at least 1 sec
        self._ready.setdefault(n, time.time())

        if time.time() - self._ready[n] > 0.5:
            print 'ready', n

            self.window.key(str(n))
            self.check_result('r')
            del self._ready[n]
            return True

        return False

    def finish(self, n):
        # only ready if ready for at least 1 sec
        self._waiting.setdefault(n, time.time())

        if time.time() - self._waiting[n] > 0.5:
            print 'finish', n

            self.window.key(str(n))
            self.check_result('r')
            del self._waiting[n]
            return True

        return False


    def order(self):
        orders = self.window.orders

        #print [x[2] for x in orders]
        #print time.time()

        seq = ['burning', 'ready', 'waiting', 'new', 'active', 'cooking', None]

        # oldest orders first
        #orders.sort(key=lambda x: (x[3], self._received.get(x[0], 0)))

        def _key(a):
            return (seql.index(a[2]), a[3], self._received.get(a[0], 0))

        orders.sort(key=lambda x: seq.index(x[2]))

        for n, active, status, x in orders:
            if status == 'burning':
                self.window.key(n)
                return

            if status == 'ready':
                if self.ready(n):
                    return

            if status == 'waiting':
                if self.finish(n):
                    return

            if status == 'new':
                self._received.setdefault(n, time.time())
                if self.accept(n):
                    return



            ## elif status == 'cooking':
            ##     self._cooking.setdefault(n, time.time())
            ##     return


    def prepare(self):
        log_entry = self._log.get(self.window.title, (0, None))
        print 'log_entry', self.window.title, log_entry

        if time.time() - log_entry[0] < 1:
            if log_entry[1] == self.window.ticket_no:
                print 'REQUIRE CONFIRMATION'
                return

        food = self.get_food()
        if food is None:
            return

        print 'Food:', food
        del self._errors[:]

        recipe = self.recipes.get_recipe(food, self.window)

        print "Recipe:", recipe

        if recipe:
            self.execute_recipe(recipe)

        self._log[self.window.title] = (time.time(), self.window.ticket_no)

    def run_robbery(self):
        print 'robbery'

        #self.key(self.k.escape_key)

        text = self.get_text()
        print text
        print

        hair = raw_input('hair: ')
        eyes = raw_input('eyes: ')
        ears = raw_input('ears: ')
        nose = raw_input('nose: ')
        lips = raw_input('lips: ')
        face = raw_input('face: ')

        HAIR = {'bald': 'h', 'sexy': 'hh', 'spiked': 'hhh', 'poofy': 'hhhh'}
        EYES = {'normal': 'y', 'crazy': 'yy', 'sexy': 'yyy', 'beady': 'yyyy'}
        EARS = {'normal': 'e', 'round': 'ee', 'long': 'eee', 'tiny': 'eeee'}
        NOSE = {'crooked': 'n', 'normal': 'nn', 'fancy': 'nnn'}
        LIPS = {'long': 'l', 'small': 'll', 'sexy': 'lll'}
        FACE = {'mustache': 'f', 'beard': 'ff', 'fuzz': 'fff', 'both': 'ffff'}

        s = ''

        s += HAIR.get(hair, '')
        s += EYES.get(eyes, '')
        s += EARS.get(ears, '')
        s += NOSE.get(nose, '')
        s += LIPS.get(lips, '')
        s += FACE.get(face, '')

        s += 'E'

        self._window.activate(int(time.time()))

        time.sleep(0.1)

        return s

    def check_result(self, w):
        if not self._opts['test_recipes']:
            return

        food = self.get_food()
        if not food:
            return

        if food.endswith('_grill'):
            return

        f = FINISH_AT[self._opts['test_recipes']]

        if f != w:
            return

        if self.window.order_ok():
            print 'Recipe OK!'

        else:
            print 'Recipe failed.'
            raise KeyboardInterrupt()


