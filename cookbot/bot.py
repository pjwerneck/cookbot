# -*- coding: utf-8 -*-
import time
import logging

from cookbot.interpreter import parser
from cookbot.recipes import FOODS, FINISH_AT, RecipesBase
from cookbot.window import GameWindow


class CookBot(object):
    def __init__(self, **opts):

        self._opts = opts

        self.window = GameWindow(**opts)
        self.recipes = RecipesBase(**opts)

        self._running = False

        self._log = {}

        self._accepted = {}
        self._received = {}
        self._cooking = {}
        self._waiting = {}
        self._ready = {}

        self._errors = []
        self._canary = []

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
        cmd = parser.parse(s)
        cmd(window=self.window, key_delay=self._opts['key_delay'])

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
            logging.error("Couldn't identify task: %r, %r" % (self.window.title, self.window.text))
            self.window._img.show()
            raise RuntimeError("Couldn't identify task %r" % self.window.title)
        else:
            self._errors.append(self.window.title)

    def accept(self, n):
        # accept only if seen at least once before and not accepted within the last second
        self._accepted.setdefault(n, time.time())

        if time.time() - self._accepted[n] > 0.1:
            logging.info("%s accept." % n)

            if self._opts['test_recipes']:
                self.window.change_recipe()

            self.window.key(str(n))
            del self._accepted[n]
            return True

        return False

    def ready(self, n):
        # only ready if ready for at least 0.5 sec
        self._ready.setdefault(n, time.time())

        #if time.time() - self._ready[n] > 0.1:
        if 1:
            logging.info("%s ready." %n)

            self.window.key(str(n))
            self.check_result('r')
            del self._ready[n]
            return True

        return False

    def finish(self, n):
        # only ready if ready for at least 1 sec
        self._waiting.setdefault(n, time.time())

        #if time.time() - self._waiting[n] > 0.5:
        if 1:
            logging.info("%s finishing." % n)

            self.window.key(str(n))
            self.check_result('r')
            del self._waiting[n]
            return True

        return False


    def order(self):
        orders = self.window.orders

        # first, accept burning and ready orders
        ready_orders = [o for o in orders if o[2] in {'burning', 'ready'}]
        for n, active, status, x in ready_orders:
            self.ready(n)

        # then, finish waiting orders
        waiting_orders = [o for o in orders if o[2] == 'waiting']
        for n, active, status, x in waiting_orders:
            if self.finish(n):
                return

        # then, accept new orders
        if self._opts['auto_accept']:
            new_orders = [o for o in orders if o[2] == 'new']

            # rank orders by x_factor
            new_orders.sort(key=lambda x: x[3])

            for n, active, status, x in new_orders:
                if self.accept(n):
                    return


    def prepare(self):
        log_entry = self._log.get(self.window.title, (0, None))

        if time.time() - log_entry[0] < 1:
            if log_entry[1] == self.window.ticket_no:
                logging.warning("Same order and ticket number. Waiting confirmation...")
                return

        food = self.get_food()
        if food is None:
            return

        logging.info("Food: %s" % food)
        del self._errors[:]

        recipe = self.recipes.get_recipe(food, self.window)

        logging.info("Recipe: %s" % recipe)

        if recipe:
            self.execute_recipe(recipe)

        self._log[self.window.title] = (time.time(), self.window.ticket_no)

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
            logging.info("Recipe OK!")

        else:
            logging.error("Recipe Failed!")
            raise KeyboardInterrupt()


