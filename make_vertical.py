#!/usr/bin/python
# coding=utf-8

import sys
import codecs
from itertools import izip
from argparse import ArgumentParser


def parse_pos_tagged_line(l, truncate_tags = False):
    u"""
    Parsing a pos-tagged line, attaching pre- and suffixes and dropping the corresponding pos-tags.

    >>> s = u"S/S عنوان/NOUN-MS ال+/DET حلق/NOUN-FS +ة/NSUFF :/PUNC انتخاب/NOUN-FP +ات/NSUFF ال+/DET مغرب/NOUN-MS و+/CONJ مسار/NOUN-MS ال+/DET إصلاح/NOUN-MS E/E "
    >>> toks, tags = parse_pos_tagged_line(s)
    >>> print u" ".join("/".join(p) for p in zip(toks, tags))
    عنوان/NOUN-MS الحلقة/NOUN-FS :/PUNC انتخابات/NOUN-FP المغرب/NOUN-MS ومسار/NOUN-MS الإصلاح/NOUN-MS
    >>> parse_pos_tagged_line(s, truncate_tags=True)[1]
    [u'NOUN', u'NOUN', u'PUNC', u'NOUN', u'NOUN', u'NOUN', u'NOUN']

    """
    # Dropping sentence start / end markers
    tok_pos_pairs = (t.rsplit("/", 1) for t in l.split(" ")[1:-2])

    #  Attaching pre- and suffixes to get surface form
    toks, tags = [], []
    last_token_prefix = False

    for tok, tag in tok_pos_pairs:
        if tok.endswith("+"):
            if last_token_prefix:
                toks[-1] += tok[:-1]
            else:
                toks.append(tok[:-1])
                last_token_prefix = True
        elif tok.startswith("+"):
            toks[-1] += tok[1:]
            last_token_prefix = False
        else:
            if truncate_tags:
                tag = tag.split("-", 1)[0]
            tags.append(tag)
            if last_token_prefix:
                toks[-1] += tok
            else:
                toks.append(tok)

            last_token_prefix = False


    return toks, tags

if __name__ == "__main__":
    p = ArgumentParser()
    # p.add_argument("surface_form_file")
    p.add_argument("pos_file")  # contains surface form and tags (split)
    p.add_argument("lemma_file")
    p.add_argument("--vertical-file")
    p.add_argument("--truncate-tags", action="store_true")
    args = p.parse_args()

    # f_surface = codecs.open(args.surface_form_file, "r", "utf-8")
    f_pos = codecs.open(args.pos_file, "r", "utf-8")
    f_lemma = codecs.open(args.lemma_file, "r", "utf-8")

    if args.vertical_file:
        f_out = codecs.open(args.vertical_file, "w", "utf-8")
    else:
        f_out = codecs.getwriter('utf8')(sys.stdout)

    stderr = codecs.getwriter("utf-8")(sys.stderr)

    for n, (lemmatized, pos_tagged) in enumerate(izip(f_lemma, f_pos)):
        toks, tags = parse_pos_tagged_line(pos_tagged, args.truncate_tags)
        lemma_toks = lemmatized.strip().split(" ")
        if not (len(toks) == len(lemma_toks)):
            stderr.write("Line %d: Token count mismatch:%s%s"
                         % (n, lemmatized, pos_tagged))
            continue

        f_out.write("<s>\n")
        f_out.write("\n".join("\t".join(tup)
                              for tup in izip(toks, tags, lemma_toks)))
        f_out.write("\n</s>\n")
