# -*- coding: utf-8 -*-
import logging
import os
import random
import string
import time

from PIL import Image

from cookbot.colorops import origin_dist, delta_chi_square
from cookbot.db import NotFound
from cookbot.interpreter import parser
from cookbot.window import GameWindow


class CookBot(object):
    def __init__(self, db, **opts):
        self.db = db

        self._opts = opts

        self.window = GameWindow(db, **opts)

        self._running = False

        self._order_log = {}
        self._waiting = {}
        self._accepted = 0
        self._errors = []
        self._canary = []

        self._refs = {n.split('.')[0]: Image.open('battle/' + n).histogram() for n in os.listdir('battle/')}

    def run(self):
        logging.info("Starting...")
        self._running = True

        self.window.focus()

        while self._running:
            self.window.refresh()

            if self._opts['auto_order'] and self._opts['canary']:
                self._canary.append(self.window.canary)
                del self._canary[:-2]

                if len(set(self._canary)) > 1:
                    logging.info('Canary died. Waiting respawn...')
                    time.sleep(self._opts['loop_delay'])
                    continue

            if self._opts['auto_order'] or self._opts['test_recipes']:
                if self.window.orders:
                    self.order()

            if self.window.at_kitchen():
                self.prepare()

            time.sleep(self._opts['loop_delay'])

    def execute_recipe(self, s):
        while s:
            logging.debug("Executing recipe: %r" % s)
            cmd = parser.parse(s)
            logging.debug("Command built: %r" % cmd)
            s = cmd(bot=self, **self._opts)

        self.check_result('p')

    def get_food(self):
        # XXX: ugly hack needed to circumvent equal names for some foods
        if self.window.title == 'the mix':

            if 'meat' in self.window.text:
                self.window._title += ' burger'

            elif 'ranch' in self.window.text:
                self.window._title += ' salad'

            elif 'mackerel' in self.window.text:
                self.window._title += ' sushi'

            else:
                raise NotImplementedError("the mix: %r" % (p,))

        try:
            food, title, recipe, finished_at = self.db.get_food(self.window.title)

            if self.window.at_grill():
                food = food + '_grill'

            del self._errors[:]
            return food

        except NotFound:
            pass

        if self.window.title.startswith('robbery'):
            del self._errors[:]
            return 'robbery'

        if len(self._errors) > 4:
            logging.error("Couldn't identify task: %r, %r" % (self.window.title, self.window.text))
            self.window._img.show()
            raise RuntimeError("Couldn't identify task %r" % self.window.title)
        else:
            self._errors.append(self.window.title)

    def accept(self, n):
        logging.info("%s accept" % n)

        if self._opts['test_recipes']:
            self.window.change_recipe()

        self.window.key(str(n))

    def ready(self, n):
        # always fine to deliver a ready order
        logging.info("%s ready." %n)

        self.window.key(str(n))
        self.check_result('r')
        self._waiting.pop(n, None)

    def finish(self, n):
        # always fine to finish
        logging.info("%s finishing." % n)

        self.window.key(str(n))
        self.check_result('r')
        self._waiting.pop(n, None)

    def quick_ready(self):
        self.order(refresh=True, only_ready=True)

    def order(self, refresh=False, only_ready=False):
        if refresh:
            self.window.refresh()

        orders = self.window.orders

        # first, accept burning and ready orders
        ready_orders = [o for o in orders if o[2] in {'burning', 'ready'}]
        for n, active, status, x in ready_orders:
            self.ready(n)

        if only_ready:
            return

        # then, finish waiting orders
        waiting_orders = [o for o in orders if o[2] == 'waiting']
        for n, active, status, x in waiting_orders:
            self.finish(n)
            return

        # don't accept new order within 100ms
        if time.time() - self._accepted < 0.5:
            print 'WAITING'
            return

        # then, accept new orders
        if self._opts['auto_accept']:
            new_orders = [o for o in orders if o[2] == 'new']

            # rank orders by arrival and x_factor
            new_orders.sort(key=lambda x: int(x[-1]))

            # set arrival
            for n, active, status, x in new_orders:
                self._waiting.setdefault(n, time.time())

            for n, active, status, x in new_orders:
                if time.time() - self._waiting[n] < 0.2:
                    continue

                self.accept(n)
                self._accepted = time.time()
                break

    def prepare(self):
        log_entry = self._order_log.get(self.window.title, (0, None))

        if time.time() - log_entry[0] < 1:
            if log_entry[1] == self.window.ticket_no:
                logging.warning("Same ticket number. Waiting confirmation...")
                return

        food = self.get_food()
        if food is None:
            return

        logging.info("Food: %s" % food)
        logging.info("Title: %s" % self.window.title)
        del self._errors[:]

        recipe = self.db.get_recipe(food, self.window.title)

        logging.info("Recipe: %s" % recipe)

        if recipe:
            self.execute_recipe(recipe)

        self._order_log[self.window.title] = (time.time(), self.window.ticket_no)

    def check_result(self, w):
        if not self._opts['test_recipes']:
            return

        food = self._opts['test_recipes']

        try:
            finished_at = self.db.get_finished_at(food)
        except NotFound:
            return

        if food.endswith('_grill'):
            return

        if finished_at != w:
            return

        if self.window.order_ok():
            logging.info("Recipe OK!")

        else:
            logging.error("Recipe Failed!")
            exit(1)

    def run_robbery(self):
        text = self.window.text

        text = text.translate({ord(char): ord(u' ') for char in string.punctuation})

        logging.info("Robbery: %r" % text)
        tokens = text.split()

        nouns = {'hair': {'bald': 'h', 'sexy': 'hh', 'spiked': 'hhh', 'poofy': 'hhhh'},
                 'eyes': {'normal': 'y', 'crazy': 'yy', 'sexy': 'yyy', 'beady': 'yyyy'},
                 'ears': {'normal': 'e', 'round': 'ee', 'long': 'eee', 'tiny': 'eeee'},
                 'nose': {'crooked': 'n', 'normal': 'nn', 'fancy': 'nnn'},
                 'lips': {'long': 'l', 'small': 'll', 'sexy': 'lll'},
                 'facial_hair': {'mustache': 'f', 'beard': 'ff', 'fuzz': 'fff'},
                 }

        adjectives = {'sexy', 'spiked', 'poofy', 'normal', 'crazy', 'beady',
                      'round', 'long', 'tiny', 'crooked', 'fancy', 'small'}

        reverse_match = {'bald': 'hair',
                         'mustache': 'facial_hair',
                         'beard': 'facial_hair',
                         'fuzz': 'facial_hair'}

        current_jj = None
        match = {k: [] for k in nouns}
        match['facial_hair'] = []

        tokens = text.replace(',', '').split()

        for word in tokens:
            if word in reverse_match:
                v = reverse_match[word]
                match[v].append(word)

            elif word in adjectives:
                current_jj = word

            elif word in nouns:
                match[word].append(current_jj)

        assert all(match.values()), match

        s = ''

        for k, v in match.iteritems():
            for x in v:
                s += nouns[k][x]


            if k == 'facial_hair':
                if 'mustache' in v and 'beard' in v:
                    s += 'f'

        s += 'E'

        return s

    def run_dishes(self):
        return 'LRLRU' * 6

        bbox = (873, 107, 1124, 223)

        while self.window.at_kitchen():
            im = self.window._img.crop(bbox)
            h = int(origin_dist(im, (157, 24, 24)))

            if h == 54644:
                self.window.key(self.window.k.left_key)

            elif h == 312328:
                self.window.key(self.window.k.right_key)

            elif h == 126311:
                self.window.key(self.window.k.up_key)

            self.window.refresh()

    def run_trash(self):
        return ('U.[0.2]R.[0.2]' * 5) + 's'


        bbox = (873, 107, 1124, 223)

        while self.window.at_kitchen():
            im = self.window._img.crop(bbox)
            h = int(origin_dist(im, (157, 24, 24)))

            if h == 54862:
                self.window.key(self.window.k.up_key)

            elif h == 312328:
                self.window.key(self.window.k.right_key)

            elif h == 136091:
                self.window.key('s')

            self.window.refresh()


    def run_battle_kitchen_upgrade(self):
        img = self.window._img

        i = int(time.time())
        img.save('tmp/battle_%d.bmp' % i)
        print i

        # if there's an upgrade, choose it

        top_im = img.crop((420, 290, 620, 322))
        top_text = self.window.ocr(top_im)

        if 'upgrade' in top_text:
            logging.info("Upgrading top...")
            return 'z'

        bot_im = img.crop((420, 442, 620, 474))
        bot_text = self.window.ocr(bot_im)

        if 'upgrade' in bot_text:
            logging.info("Upgrading bottom...")
            return 'x'

        options = []

        # othwerise, identify the options and choose
        if 'replace' in top_text:
            #imt1 = img.crop((423, 189, 517, 283)).histogram()
            imt2 = img.crop((523, 189, 617, 283)).histogram()

            #ts1 = min([(k, delta_chi_square(imt1, v)) for (k, v) in self._refs.iteritems()], key=lambda x: x[1])
            ts2 = min([(k, delta_chi_square(imt2, v)) for (k, v) in self._refs.iteritems()], key=lambda x: x[1])

            if ts2[1] < 1000:
                options.append((ts2[0], 'z'))

            else:
                raise RuntimeError("Can't identify top upgrade")

        if 'replace' in bot_text:
            #imb1 = img.crop((423, 341, 517, 435)).histogram()
            imb2 = img.crop((523, 341, 617, 435)).histogram()

            #bs1 = min([(k, delta_chi_square(imb1, v)) for (k, v) in self._refs.iteritems()], key=lambda x: x[1])
            bs2 = min([(k, delta_chi_square(imb2, v)) for (k, v) in self._refs.iteritems()], key=lambda x: x[1])

            if bs2[1] < 1000:
                options.append((bs2[0], 'x'))

            else:
                raise RuntimeError("Can't identify bottom upgrade")


        preference = [
            'coffee',
            'salad',
            'icecream',
            'enchiladas',
            'soda',
            'wine',

            'baked_potato',

            'breakfast_sandwich',
            'shish_kebob',
            'fried_rice',
            'fish',
            'chicken_breast',
            'steak',
            'pizza',

            'lobster',
            'nachos',
            'burger',
            'pancakes',
            'pasta',
            'soup',

            'sopapillas',
            'hash_browns',
            ]

        choice = min(options, key=lambda x: preference.index(x[0]))

        logging.info("Options: %s" % repr(options))
        logging.info("Choice: %r, %r" % choice)

        return choice[1]
