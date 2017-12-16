# -*- coding: utf-8 -*-

import re
import time
import random
import string
import sqlite3
import logging
import tablib
from contextlib import contextmanager

from cookbot.colorops import origin_dist

class NotFound(Exception):
    pass


class CookDB(object):
    def __init__(self, **opts):
        self.db = sqlite3.connect(':memory:')

    def load(self):
        self._import_from_csv('data/SC_WORDS.csv', 'words')
        self._import_from_csv('data/SC_REPLACEMENTS.csv', 'replacements')
        self._import_from_csv('data/RECIPES.csv', 'recipes')

    def _import_from_csv(self, filename, table):
        with open(filename) as f:
            ds = tablib.Dataset()
            ds.csv = f.read()

        columns = ', '.join(ds.headers)
        insert = "insert into %s (%s) values (%s)" % (table, columns, ', '.join(['?'] * len(ds.headers)))

        self.db.execute("CREATE TABLE %s (%s)" % (table, columns))

        for row in ds.dict:
            self.db.execute(insert, row.values())

        self.db.commit()

    def query(self, *args, **kwargs):
        logging.debug("Query: %r, %r" % (args, kwargs))
        results = [r for r in self.db.execute(*args, **kwargs)]

        if not results:
            raise NotFound()

        return results

    def query_one(self, *args, **kwargs):
        for r in self.query(*args, **kwargs):
            return r

    def get_recipe(self, food, name):
        return self.query_one('SELECT recipe FROM recipes WHERE food = ? AND name = ?', (food, name))[0]

    def get_food(self, name):
        return self.query_one('SELECT food, name, recipe, finished_at FROM recipes WHERE name = ?', (name,))

    def get_finished_at(self, food):
        return self.query_one('SELECT finished_at FROM recipes WHERE food = ? LIMIT 1', (food,))[0]

    def get_words(self):
        return set(x[0] for x in self.db.execute("select word from words"))

    def get_replacements(self):
        d = {}

        for old, new in self.db.execute("select old, new from replacements"):
            try:
                d[old].add(new)
            except KeyError:
                d[old] = {new}

        return d

