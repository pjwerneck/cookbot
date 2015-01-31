# -*- coding: utf-8 -*-

import argparse
import time

from cookbot.bot import CookBot


def main():

    parser = argparse.ArgumentParser(description="CookBot")

    parser.add_argument("-a", "--auto", action='store_true', dest='auto_order')
    parser.add_argument("-t", "--test-recipes")

    args = parser.parse_args()

    game = CookBot()
    game.set_opts(**vars(args))

    time.sleep(1)


    try:
        game.run()
    except KeyboardInterrupt:
        game._running = False

    except RuntimeError:
        if not game._opts['test_recipes']:
            game.window.escape()
        raise


if __name__ == '__main__':
    main()
