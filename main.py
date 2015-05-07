# -*- coding: utf-8 -*-
import json
from stego_utils import morpho, replacer, tableMaker
from random import randint
from codecs import open
from argparse import ArgumentParser, RawTextHelpFormatter
from time import time


def build_table(curMorpho, count=50, printRes=True):
    with open(args.t) as f:
        texts = json.load(f)
        table = tableMaker(texts[:count], curMorpho)
    with open(args.s, "w") as f:
        table.dump(f)
    return len(table.processedTable), len(" ".join(texts[:count]))


def embed(curMorpho, textSize=None, printRes=True):
    with open(args.s) as f:
        curReplacer = replacer(json.load(f), curMorpho)
    if args.secret:
        msg = [int(s) for s in args.secret if s in "01"]
    else:
        msg = [randint(0, 1) for c in xrange(1000)]

    with open(args.c, encoding="utf-8") as f:
        if textSize:
            text, l = curReplacer.embed(f.read()[:textSize], msg, args.test)
        else:
            text, l = curReplacer.embed(f.read(), msg, args.test)
    if printRes:
        print "{0} bites was embeded in text:\n{1}".format(l, "".join(map(str, msg[:l])))

    with open(args.e, "w", encoding="utf-8") as f:
        f.write(text)
    return l


def extract(curMorph, textSize=None, printRes=True):
    with open(args.s) as f:
        curReplacer = replacer(json.load(f), curMorph)
    with open(args.e, encoding="utf-8") as f:
        text = f.read() if not textSize else f.read()[:textSize]
    msg = curReplacer.extract(text)
    if printRes:
        print "Secret message:"
        print "".join(map(str, msg))
    else:
        curReplacer.extract(text)
    return len(msg)


def timeIt(func, curMorpho, param=None, count=1):
    times = []
    for j in range(count):
        a = time()
        res = func(curMorpho, param, printRes=False)
        times.append(time() - a)
    s = "func: {0}, min: {1}, average: {2} average filtred: {3}, res: {4}"
    s = s.format(func.__name__,
                 min(times)*1000,
                 (sum(times)/count)*1000,
                 (sum(times) - max(times) - min(times))/(count-2)*1000,
                 res)
    print s


def score(curMorpho):
    for i in range(20, 400, 20):
        print i
        timeIt(build_table, curMorpho, i)
        timeIt(embed, curMorpho)
        timeIt(extract, curMorpho)

    for i in range(5000, 25000, 5000):
        timeIt(embed, curMorpho, i)
        timeIt(extract, curMorpho, i)


actions = {
    "build_table": build_table,
    "embed": embed,
    "extract": extract,
    "score": score
}


if __name__ == "__main__":
    argPar = ArgumentParser(formatter_class=RawTextHelpFormatter, description=open("README.md").read())
    argPar.add_argument('-t', metavar="texts-for-synonyms", action='store', default="data/texts.json",
                        help="""change texts-for-synonyms file (default data/texts.json)""")
    argPar.add_argument('-s', metavar="synonym-table-file", action='store', default="table.json",
                        help="""change synonym_table file (default table.json)""")
    argPar.add_argument('-p', metavar="pymorphy-file", action='store', default="data/ru.sqlite-json",
                        help="""change pymorphy file file (default data/ru.sqlite-json)""")
    argPar.add_argument('-c', metavar="container", action='store', default="data/container.txt",
                        help="""Container file secret (default: data/container.txt""")
    argPar.add_argument('-e', metavar="outpute file", action='store', default="embeded.txt",
                        help="""Container file secret (default: embeded.txt""")
    argPar.add_argument('-test', action='store_true',
                        help="""Enable test mode - replaced word will be UPPERCASE""")
    argPar.add_argument('-secret', metavar="secret", action='store', default=None,
                        help="""specify secret (default: None, will be generated""")
    argPar.add_argument('action', metavar="action", action='store', choices=actions.keys(),
                        help=", ".join(actions.keys()))

    args = argPar.parse_args()
    curMorpho = morpho(args.p)

    actions[args.action](curMorpho)
