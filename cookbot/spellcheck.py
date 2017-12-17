# -*- coding: utf-8 -*-
import difflib
import distance
import itertools
import string


# Recipe name is correct 99% of the time. Recipe text however is
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

        self.NAMES = self.db.get_names()
        self.WORDS = self.db.get_words()
        self.REPLACEMENTS = self.db.get_replacements()

    def build_replacements(self, word, name):
        reps = [[(i, r) for r in self.REPLACEMENTS[c]] for i, c in enumerate(word) if c in self.REPLACEMENTS]

        for repset in powerset(reps):
            for x in itertools.product(*repset):
                yield dict(x)

    def ocr_error(self, word, name):
        reps = self.build_replacements(word, name)
        words = {u''.join(r.get(i, c) for (i, c) in enumerate(word)) for r in reps}

        return self.known(words, name)

    def common_error(self, word, name):
        if name:
            return set(difflib.get_close_matches(word.replace(" ","-"), self.NAMES))
        return set(difflib.get_close_matches(word, self.WORDS, cutoff=0.7))

    def known(self, words, name):
        if name:
            return [word for word in words if word in self.NAMES]
        return [word for word in words if word.lower() in self.WORDS]

    def correct(self, word, name):
        if not name and len(word) == 1:
            # XXX weird case
            if word == 'l':
                word = '1'

            if word == 'Z':
                word = '2'

            return word

        if not name and word.isdigit(): #ticket number
            return word

        if name:
            if word == 'The Mix':
                return word
            candidates = self.common_error(word, name)
        else:
            candidates = self.known([word], name) or self.ocr_error(word, name) or self.common_error(word, name)# or {word}
        if not candidates:
            raise RuntimeError("No candidates for: %r" % word)

        return sorted(candidates, key=lambda candidate: distance.jaccard(word, candidate))[0]

    def tokenize(self, text, name):
        # remove useless punctuation
        text = text.translate({ord(char): ord(' ') for char in '!"#$%&\'*+,./:;<=>?@[\\]_{|}'})

        # remove balanced parenthesis
        text = remove_balanced_parenthesis(text)

        # split
        if name:
            return [text.strip()]
        return text.split()


    def __call__(self, text, name=False):
        words = self.tokenize(text, name)

        words = [self.correct(w, name) for w in words]

        text = u' '.join(words)

        return text
