# -*- coding: utf-8 -*-
import argparse
import time
import logging

from cookbot.db import CookDB


logging.basicConfig(format='%(levelname)8s - %(message)s', level=logging.INFO)


def _run(args):

    from cookbot.bot import CookBot

    opts = vars(args)

    db = CookDB()
    db.load()

    game = CookBot(db, **opts)

    time.sleep(1)

    try:
        game.run()
    except KeyboardInterrupt:
        game._running = False

    except RuntimeError:
        if not game._opts['test_recipes']:
            game.window.escape()
        raise


def _interpreter(args):
    from cookbot.interpreter import parser

    if args.recipe:
        cmd = parser.parse(args.recipe)
        print cmd
        return


def main():

    parser = argparse.ArgumentParser(description="CookBot")

    subparsers = parser.add_subparsers(title='Commands')

    parser_run = subparsers.add_parser('run')
    parser_run.set_defaults(func=_run)
    parser_run.add_argument("-a", "--auto", action='store_true', dest='auto_order')
    parser_run.add_argument("-t", "--test-recipes")
    parser_run.add_argument("-l", "--loop-delay", type=float, default=0.05, dest='loop_delay')
    parser_run.add_argument("-k", "--key-delay", type=float, default=0.05, dest='key_delay')
    parser_run.add_argument("--disable-canary", action='store_false', dest='canary')
    parser_run.add_argument("--disable-auto-accept", action='store_false', dest='auto_accept')
    parser_run.add_argument("--db", dest="dbfile", default='cookbot.db')

    parser_interpreter = subparsers.add_parser('interpreter')
    parser_interpreter.set_defaults(func=_interpreter)
    parser_interpreter.add_argument("-r", "--recipe")
    #parser_run.add_argument("-a", "--auto", action='store_true', dest='auto_order')
    #parser_run.add_argument("-t", "--test-recipes")


    args = parser.parse_args()
    args.func(args)


def _main():

    import sqlite3

    conn = sqlite3.connect('data/COOKBOT.db')


    c = conn.cursor()

    c.execute("select * from recipes order by food")

    import tabulate

    rows = [r for r in c]

    print tabulate.tabulate(rows, tablefmt='pipe')



if __name__ == '__main__':
    main()
