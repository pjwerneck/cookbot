# -*- coding: utf-8 -*-

import time

DEFAULT_SLEEP = 0.1

tokens = ('KEY',
          'ICONST',
          'FCONST',
          'WFIX',
          'TIMES',
          'LBRACKET',
          'RBRACKET',
          'LPAREN',
          'RPAREN',
          'COMMA',
          'ASK',
          )

t_TIMES = r'\*'
t_KEY   = r'[a-zEUDLR\!\?]'
t_WFIX  = r'\.'
t_COMMA = r','
t_ASK = r'\?'

t_ignore = r' '

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
    
    
# Build the lexer
import ply.lex as lex
lex.lex()


class Command(object):
    def __init__(self, key):
        self.key = key

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.key)

    def __call__(self, win):
        
        kbd = win.k
        m = {'E': kbd.return_key,
             'L': kbd.left_key,
             'U': kbd.up_key,
             'R': kbd.right_key,
             'D': kbd.down_key,
             '!': kbd.escape_key,
             }

        return m.get(self.key, self.key)


class Press(Command):
    def __call__(self, win):
        k = super(Press, self).__call__(win)
        win.k.press_key(k)
        
    
class Release(Command):
    def __call__(self, win):
        k = super(Release, self).__call__(win)
        win.k.release_key(k)


class Sleep(object):
    def __init__(self, seconds):
        self.seconds = seconds
    
    def __repr__(self):
        return 'Sleep(%0.2f)' % self.seconds

    def __add__(self, other):
        return Sleep(self.seconds + other.seconds)

    def __call__(self, kbd):
        time.sleep(self.seconds)


precedence = (('right', 'TIMES'),
              )


def p_recipe(p):
    """
    recipe : cmd_list
    """

    recipe = []

    for (c, k, p_, r) in p[1]:
        if c == 'k':
            recipe.append(Press(k))
            recipe.append(Sleep(p_))
            recipe.append(Release(k))
            recipe.append(Sleep(r))

        elif c == 's':
            recipe.append(Sleep(p_))

        else:
            raise NotImplementedError(c)

    p[0] = recipe
    

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
    expr_list : expr_list TIMES ICONST
    """

    if len(p) == 3:
        for v in p[1]:
            v[2] = p[2][0]
            v[3] = p[2][1]
        
        p[0] = p[1]

    elif len(p) == 4:
        p[0] = p[1] * p[3]


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
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = p[1] + p[2]


def p_expr_op(p):
    """
    expr : expr trailer
    expr : expr TIMES ICONST
    """

    if len(p) == 3:
        for v in p[1]:
            v[-2:] = p[2]
        p[0] = p[1]

    elif len(p) == 4:
        p[0] = p[1] * p[3]


def p_key(p):
    """
    expr : KEY
    """

    p[0] = [['k', p[1], DEFAULT_SLEEP, DEFAULT_SLEEP]]


def p_sleep(p):
    """
    expr : WFIX
    """
    p[0] = [['s', None, 0.1, None]]


def p_trailer(p):
    """
    trailer : LBRACKET number RBRACKET
    trailer : LBRACKET number COMMA number RBRACKET
    """
    if len(p) == 4:
        p[0] = (p[2], DEFAULT_SLEEP)
    elif len(p) == 6:
        p[0] = (p[2], p[4])


def p_number(p):
    """
    number : FCONST
    number : ICONST
    """
    p[0] = p[1]
        

def p_error(p):
    raise SyntaxError("Syntax error at '%s'" % p.value)


import ply.yacc as yacc
parser = yacc.yacc()



def test():
    from cookrecipes import RECIPES


    for food, recipes in RECIPES.items():
        for name, recipe in recipes.items():
            if '|' not in recipe:
                print name
                for x in parser.parse(recipe):
                    print x
    


if __name__ == '__main__':
    test()
