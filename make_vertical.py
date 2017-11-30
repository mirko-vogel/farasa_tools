#!/usr/bin/python
# coding=utf-8

import sys
import codecs
from itertools import izip
from argparse import ArgumentParser


def parse_pos_tagged_line(l):
    """

    >>> s = u"S/S عنوان/NOUN-MS ال+/DET حلق/NOUN-FS +ة/NSUFF :/PUNC انتخاب/NOUN-FP +ات/NSUFF ال+/DET مغرب/NOUN-MS و+/CONJ مسار/NOUN-MS ال+/DET إصلاح/NOUN-MS E/E "
    >>> parse_pos_tagged_line(s)

    """
    # Dropping sentence start / end markers
    tok_pos_pairs = (t.rsplit("/", 1) for t in l.split(" ")[1:-2])
    #  Need to reattach the pre- and suffixes to get surface form
    toks, tags = [], []
    has_prefix = False

    for tok, tag in tok_pos_pairs:
        if tok.endswith("+"):
            if not has_prefix:
                has_prefix = True
                toks.append("")
            toks[-1] += tok[:1]
        elif tok.startswith("+"):
            toks[-1] += tok[1:]
        else:
            if not has_prefix:
                toks.append("")
            toks[-1] += tok
            tags.append(tag)

    return toks, tags

if __name__ == "__main__":
    p = ArgumentParser()
    # p.add_argument("surface_form_file")
    p.add_argument("pos_file")  # contains surface form and tags (split)
    p.add_argument("lemma_file")
    p.add_argument("--vertical_file")
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
        toks, tags = parse_pos_tagged_line(pos_tagged)
        lemma_toks = lemmatized.strip().split(" ")
        if not (len(toks) == len(lemma_toks)):
            stderr.write("Line %d: Token count mismatch:%s%s"
                         % (n, lemmatized, pos_tagged))
            continue

        f_out.write("<s>\n")
        f_out.write("\n".join("\t".join(tup)
                              for tup in izip(toks, tags, lemma_toks)))
        f_out.write("</s>\n")
