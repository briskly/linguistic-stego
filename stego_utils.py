
## -*- coding: utf-8 -*-
import requests
import re
from bs4 import BeautifulSoup
from pymorphy import get_morph
import json


class wikiSynGetter:
    base_uri = u"http://ru.wiktionary.org/wiki/"
    synTable = None

    def __init__(self):
        self.synTable = {}
        try:
            with open("data/synCash") as f:
                self.synTable = json.load(f)
        except:
            pass

    def find_syns(self, word):
        if word in self.synTable:
            return self.synTable[word]
        word = word.lower()
        html_doc = requests.get(self.base_uri+word).content
        t = BeautifulSoup(html_doc)
        synonyms = []
        for el in t.find_all("span", {'class': 'mw-headline'}):
            if u"Синонимы" in el.text:
                neededTags = el.find_parent().find_next_sibling().find_all("a")
                synonyms = [t.text.replace(u"ё", u"е") for t in neededTags if not t.has_attr("class")]
        if u"править" not in synonyms:
            answer = synonyms
        else:
            answer = []
        self.synTable[word] = answer
        return answer

    def __del__(self):
        with open("data/synCash", "w") as f:
            json.dump(self.synTable, f)


class tableMaker:
    def __init__(self, texts, morpho):
        self.table = {}
        self.processedTable = {}
        self.morpho = morpho
        self.synGetter = wikiSynGetter()
        self.loadTexts(texts)
        self.calcTable()

    def loadTexts(self, texts):
        for textNum, cur_Text in enumerate(texts):
            basePoint = self.morpho.getBaseWords(cur_Text, studing=True)
            for point in basePoint:
                self.table.setdefault(point.get("word").get("norm").lower(), 0)
                self.table[point.get("word").get("norm").lower()] += 1

    def calcTable(self):
        sortedTable = [w[0] for w in sorted(self.table.iteritems(), key=lambda x:x[1], reverse=True)]
        usedWords = set()
        for wNum, w in enumerate(sortedTable):
            if w in usedWords:
                continue
            syns = self.synGetter.find_syns(w)
            bestSyn = self.getBestSyn(syns, usedWords)
            if not bestSyn:
                continue
            usedWords.add(bestSyn)
            usedWords.add(w)
            self.processedTable[w] = [w, bestSyn]
            self.processedTable[bestSyn] = [w, bestSyn]

    def getBestSyn(self, syns, restricted):
        availible_syns = []
        for curSyn in syns:
            if curSyn in restricted:
                continue
            for norms in self.morpho.getWordInfo(curSyn.upper()):
                if norms.get("norm").lower() in restricted:
                    continue
                if norms.get("class") in self.morpho.PoS:
                    availible_syns.append(curSyn)
        if not availible_syns:
            return None
        bestFreqSyn = max(availible_syns, key=lambda x: self.table.get(x, 0))
        if bestFreqSyn:
            return bestFreqSyn
        else:
            return availible_syns[0]

    def dump(self, fileHandler):
        json.dump(self.processedTable, fileHandler, indent=4, sort_keys=True)

    def dumps(self):
        json.dumps(self.processedTable)


class morpho:
    alph = u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    wordFindRegEx = re.compile(ur"\s?([%s]+)[\s.,!?]" % alph)
    PoS = [u"П"]
    restrictedModifiers = set([u"сравн"])
    restrictedWords = [u"ближний", u"близкий"]

    def __init__(self, path):
        self.morph = get_morph(path)

    def getBaseWords(self, text, processedTable={}, studing=False):
        replaces = []
        for regObj in self.wordFindRegEx.finditer(text):
            curWord = regObj.group(1)
            normWord = self.morph.get_graminfo(curWord.upper().replace(u"ё", u"е"))
            if normWord:
                for w in normWord:
                    if w.get("class") in self.PoS and len(curWord) > 3 and not (set(w.get("info").split(",")) & self.restrictedModifiers):
                        if w.get("norm").lower() in self.restrictedWords:
                            continue
                        elif studing:
                            replaces.append({"start": regObj.start(1), "end": regObj.end(1), "word": w})
                            break
                        elif w.get("norm").lower() in processedTable:
                            replaces.append({"start": regObj.start(1), "end": regObj.end(1), "word": w})
                            break
        return replaces

    def makeSame(self, templateStr, rawStr):
        if len(templateStr) < 2 or len(rawStr) < 2:
            return rawStr
        if templateStr[0].islower():
            newStr = rawStr[0].lower()
        else:
            newStr = rawStr[0].upper()
        if templateStr[1:].isupper():
            newStr += rawStr[1:].upper()
        else:
            newStr += rawStr[1:].lower()
        return newStr

    def putInForm(self, word, form, PoS, upper):
        w = self.morph.inflect_ru(word.upper(), form, PoS)
        return w.upper() if upper else self.makeSame(word, w)

    def getWordInfo(self, word):
        return self.morph.get_graminfo(word.upper())


class replacer:
    def __init__(self, processedTable, morpho):
        self.table = {}
        self.processedTable = processedTable
        self.morpho = morpho

    def embed(self, text, msg, test=False):
        replaces = self.morpho.getBaseWords(text, self.processedTable)
        new_text = ""
        lastEnd = 0
        for i, curRep in enumerate(replaces):
            wordToPaste = self.processedTable.get(curRep.get("word", {}).get("norm", "").lower())[msg[i]]
            wordToPaste = self.morpho.putInForm(wordToPaste, curRep.get("word").get("info"), curRep.get("word").get("class"), test)
            new_text += text[lastEnd:curRep["start"]] + wordToPaste
            lastEnd = curRep["end"]

        new_text += text[lastEnd:]
        return new_text, len(replaces)

    def extract(self, text):
        replaces = self.morpho.getBaseWords(text, self.processedTable)
        msg = []
        for i, curRep in enumerate(replaces):
            word = curRep.get("word", {}).get("norm", "").lower()
            msg.append(self.processedTable.get(word).index(word))
        return msg
