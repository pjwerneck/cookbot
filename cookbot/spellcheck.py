# -*- coding: utf-8 -*-
import difflib
import distance
import itertools
import string


# Recipe title is correct 99% of the time. Recipe text however is
# wrong more often than not, but the text is needed only for coffee
# and robbery, so the actual dictionary is relatively small.

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))


def remove_balanced_parenthesis(text):
    # first, the easy way
    lparen = text.count('(')
    rparen = text.count(')')

    if lparen == rparen:
        return text.translate({ord(char): None for char in '()'})

    # if a single paren, do nothing
    if (lparen == 1 and rparen == 0) or (lparen == 0 and rparen == 1):
        return text

    raise NotImplementedError


class SpellChecker(object):

    def __init__(self, db, **opts):
        self.db = db
        self._opts = opts

        self.WORDS = self.db.get_words()
        self.REPLACEMENTS = self.db.get_replacements()

    def build_replacements(self, word):
        reps = [[(i, r) for r in self.REPLACEMENTS[c]] for i, c in enumerate(word) if c in self.REPLACEMENTS]

        for repset in powerset(reps):
            for x in itertools.product(*repset):
                yield dict(x)

    def ocr_error(self, word):
        reps = self.build_replacements(word)
        words = {u''.join(r.get(i, c) for (i, c) in enumerate(word)) for r in reps}

        return self.known(words)

    def common_error(self, word):
        return set(difflib.get_close_matches(word, self.WORDS, cutoff=0.7))

    def known(self, words):
        return words.intersection(self.WORDS)

    def correct(self, word):
        if len(word) == 1:
            # XXX weird case
            if word == 'z':
                word = '2'

            if word == 'r':
                word = 'p'

            return word

        if word.isdigit():
            return word

        candidates = self.known({word}) or self.ocr_error(word) or self.common_error(word)# or {word}
        if not candidates:
            raise RuntimeError("No candidates for: %r" % word)

        return sorted(candidates, key=lambda candidate: distance.jaccard(word, candidate))[0]

    def tokenize(self, text):
        # lowercase
        text = text.lower()

        # remove useless punctuation
        text = text.translate({ord(char): ord(' ') for char in '!"#$%&\'*+,-./:;<=>?@[\\]_{|}'})

        # remove balanced parenthesis
        text = remove_balanced_parenthesis(text)

        # split
        return text.split()


        return text


    def __call__(self, text):
        words = self.tokenize(text)

        words = [self.correct(w) for w in words]

        text = u' '.join(words)

        return text


