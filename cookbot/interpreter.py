# -*- coding: utf-8 -*-
import logging
import re
import time

import ply.lex as lex
import ply.yacc as yacc


class Node(object):
    def __call__(self, *args, **kwargs):
        for c in self:
            c(*args, **kwargs)


class Number(Node):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'Number(%r)' % self.value


class Trailer(Node):
    def __init__(self, press=None, release=None):
        self.press = press
        self.release = release

    def __repr__(self):
        return 'Trailer(%r, %r)' % (self.press, self.release)


class IConst(Node):
    def __init__(self, const):
        self.const = const

    def __repr__(self):
        return 'IConst(%r)' % self.const

    def __call__(self, *args, **kwargs):
        return self.const


class Times(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return 'Times(%r, %r)' % (self.left, self.right)

    def __call__(self, *args, **kwargs):
        v = int(self.right(*args, **kwargs))

        for x in xrange(v):
            self.left(*args, **kwargs)


class Sleep(Node):
    def __init__(self, seconds=None):
        self.seconds = seconds

    def __repr__(self):
        return 'Sleep(%r)' % (self.seconds)

    def __call__(self, *args, **kwargs):
        logging.debug(repr(self))

        time.sleep(self.seconds or kwargs['key_delay'])

    def set_trailer(self, trailer):
        self.seconds = trailer.press


class Key(Node):
    def __init__(self, key, press=None, release=None):
        self.key = key
        self.press = press
        self.release = release

    def __repr__(self):
        return 'Key(%r, %r, %r)' % (self.key, self.press, self.release)

    def __iter__(self):
        yield KeyPress(self.key)
        yield Sleep(self.press)
        yield KeyRelease(self.key)
        yield Sleep(self.release)

    def set_trailer(self, trailer):
        self.press = trailer.press
        self.release = trailer.release


class KeyPress(Node):
    def __init__(self, key):
        self.key = key

    def __repr__(self):
        return 'KeyPress(%r)' % self.key

    def __call__(self, *args, **kwargs):
        logging.debug(repr(self))

        k = kwargs['bot'].window.k
        keymap = {'E': k.return_key,
                  'U': k.up_key,
                  'D': k.down_key,
                  'L': k.left_key,
                  'R': k.right_key,
                  }

        key = keymap.get(self.key, self.key)

        k.press_key(key)


class KeyRelease(Node):
    def __init__(self, key):
        self.key = key

    def __repr__(self):
        return 'KeyRelease(%r)' % self.key

    def __call__(self, *args, **kwargs):
        logging.debug(repr(self))

        k = kwargs['bot'].window.k
        keymap = {'E': k.return_key,
                  'U': k.up_key,
                  'D': k.down_key,
                  'L': k.left_key,
                  'R': k.right_key,
                  }

        key = keymap.get(self.key, self.key)
        k.release_key(key)


class RegExpr(Node):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return 'RegExpr(%r)' % self.expr

    def __call__(self, *args, **kwargs):        
        text = kwargs['bot'].window.text

        logging.info("%r with text=%r" % (self, text)) 

        match = re.search(self.expr, text)

        if match:
            return match.groups()[0]

        raise ValueError("RegExpr evaluation failed: %r" % text)


class MethodCall(Node):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'MethodCall(%r)' % self.name

    def __call__(self, *args, **kwargs):
        try:
            method = getattr(kwargs['bot'], self.name)
        except AttributeError:
            raise ValueError("Method evaluation failed: %r" % self.name)

        return method()


class Recipe(Node):
    def __init__(self, cmds):
        self.cmds = cmds

    def __repr__(self):
        return 'Recipe(%r)' % self.cmds

    def __iter__(self):
        return iter(self.cmds)



# Lexer tokens

tokens = ('KEY',
          'ICONST',
          'FCONST',
          'WFIX',
          'TIMES',
          'LBRACE',
          'RBRACE',
          'LBRACKET',
          'RBRACKET',
          'LPAREN',
          'RPAREN',
          'COMMA',
          'ASK',
          'MCALL',
          'REXPR',
          'FEXPR',
          )

t_TIMES = r'\*'
t_KEY   = r'[a-zEUDLR\!\?]'
t_WFIX  = r'\.'
t_COMMA = r','
t_ASK = r'\?'

t_ignore = r' '



def t_REXPR(t):
    r'\{([^\\\n]|(\\.))*?\}'
    return t


def t_MCALL(t):
    r'\$.*'
    return t

def t_FEXPR(t):
    r'\|.*'
    # ignored


def t_FCONST(t):
    r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'
    t.value = float(t.value)
    return t

def t_ICONST(t):
    r'\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'
    t.value = int(t.value)
    return t

def t_error(t):
    raise SyntaxError("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def t_LBRACKET(t):
    r'\['
    try:
        t.lexer.bracket_count += 1
    except AttributeError:
        t.lexer.bracket_count = 1
    return t

def t_RBRACKET(t):
    r'\]'
    t.lexer.bracket_count -= 1
    return t

def t_LPAREN(t):
    r'\('
    try:
        t.lexer.paren_count += 1
    except AttributeError:
        t.lexer.paren_count = 1
    return t

def t_RPAREN(t):
    r'\)'
    t.lexer.paren_count -= 1
    return t

def t_LBRACE(t):
    r'\{'
    return t

def t_RBRACE(t):
    r'\}'
    return t


# Build the lexer
lex.lex()

precedence = (('right', 'TIMES'),
              )

def p_recipe_call(p):
    """
    recipe : mcall
    """
    p[0] = p[1]



def p_recipe(p):
    """
    recipe : cmd_list
    """

    p[0] = Recipe(p[1])


def p_cmd_list(p):
    """
    cmd_list : cmd
    cmd_list : cmd cmd_list
    """

    if len(p) == 2:
        p[0] = p[1]

    elif len(p) == 3:
        p[0] = p[1] + p[2]


def p_cmd(p):
    """
    cmd : expr_list
    """

    p[0] = p[1]


def p_arg_expr(p):
    """
    expr_list : expr_list trailer
    expr_list : expr_list TIMES expr
    """

    if len(p) == 3:
        for v in p[1]:
            for v in p[1]:
                v.set_trailer(p[2])

        p[0] = p[1]

    elif len(p) == 4:
        p[0] = [Times(p[1], p[3])]


def p_paren_expr_list(p):
    """
    expr_list : LPAREN expr_list RPAREN
    """
    p[0] = p[2]


def p_expr_list(p):
    """
    expr_list : expr
    expr_list : expr_list expr
    """

    if len(p) == 2:
        p[0] = [p[1]]

    elif len(p) == 3:
        p[0] = p[1] + [p[2]]


def p_expr_op(p):
    """
    expr : expr TIMES expr
    """
    p[0] = Times(p[1], p[3])


def p_trailer_expr(p):
    """
    expr : expr trailer
    """
    p[1].set_trailer(p[2])
    p[0] = p[1]


def p_rexpr(p):
    """
    expr : REXPR
    """

    p[0] = RegExpr(p[1][1:-1])


def p_key(p):
    """
    expr : KEY
    """

    p[0] = Key(p[1])


def p_sleep(p):
    """
    expr : WFIX
    """
    p[0] = Sleep()

def p_iconst(p):
    """
    expr : ICONST
    """
    p[0] = IConst(p[1])


def p_trailer(p):
    """
    trailer : LBRACKET number RBRACKET
    trailer : LBRACKET number COMMA number RBRACKET
    """
    if len(p) == 4:
        p[0] = Trailer(p[2])
    elif len(p) == 6:
        p[0] = Trailer(p[2], p[4])


def p_number(p):
    """
    number : FCONST
    number : ICONST
    """
    p[0] = p[1]


def p_mcall(p):
    """
    mcall : MCALL
    """
    p[0] = MethodCall(p[1].strip('$'))


def p_error(p):
    raise SyntaxError("Syntax error at '%s'" % p.value)


parser = yacc.yacc()



