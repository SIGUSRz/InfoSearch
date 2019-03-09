from nltk.tokenize import RegexpTokenizer
from collections import Counter, defaultdict
import os
import json
import math

DPATH = "data/WEBPAGES_RAW"
OPATH = "data/WEBPAGES"
PATH = "data/INVINDEX"


class TFIDF_Vectorizer(object):
    def __init__(self, invIndexDict, N):
        self.invIndexDict = invIndexDict
        self.word_id = {k: v for v, k in enumerate(self.invIndexDict)}
        self.N = N

    def tfidf(self, txt):
        words = txt.split()
        word_count = Counter(words)
        vector = {}
        for word in word_count.keys():
            if word not in self.word_id:
                continue
            id = str(self.word_id[word])
            tf = word_count[word]
            df = len(self.invIndexDict[word])
            vector[id] = (1 + math.log(tf, 10)) * math.log(self.N / df, 10)
        return vector


def checkTitle(firstLine, appearTitle):
    tokenizer = RegexpTokenizer('[a-zA-Z]+')
    words = tokenizer.tokenize(firstLine)
    for word in words:
        appearTitle[word] = True


# Tokenize the string and count the valid words
def tokenAndCount(s, wordCounter):
    tokenizer = RegexpTokenizer('[a-zA-Z]+')
    words = tokenizer.tokenize(s)
    wordCounter.update(words)


def createInvIndex(wordCounter, appearTitle, invIndexDict, fileId):
    for element in wordCounter:
        invIndexDict[element].append((fileId, wordCounter[element], appearTitle[element]))


def sort(invIndexDict):
    sortCount = sorted(invIndexDict.items())

    return sortCount


def writeTxt(invIndexDict):
    with open(os.path.join(PATH, "vocab.txt"), 'w') as fp:
        fp.write('\n'.join([str(word[0]) for word in invIndexDict]))

    with open(os.path.join(PATH, "postings.txt"), 'w') as fp:
        fp.write('\n'.join([str(postings) for postings in invIndexDict]))


def writeJson(invIndexDict):
    with open(os.path.join(PATH, "postings.json"), 'w') as fp:
        json.dump(invIndexDict, fp)


def tfidf_all_doc(invIndexDict, N):
    doc_tfidf_dict = {}
    with open(os.path.join(OPATH, "bookkeeping.json"), 'r') as f:
        book = json.load(f)
    vectorizer = TFIDF_Vectorizer(invIndexDict, N)
    for info in list(book.keys()):
        i = info.split('/')
        dir_id = i[0]
        doc_id = i[1]
        with open(OPATH + "/" + dir_id + "/" + doc_id + ".txt", 'r') as file:
            doc_txt = file.read()
        doc_tfidf_dict[dir_id + "_" + doc_id] = vectorizer.tfidf(doc_txt)
    with open(os.path.join(PATH, "tfidf.json"), 'w') as f:
        json.dump(doc_tfidf_dict, f)


def main():
    os.system("rm -rf %s" % PATH)
    os.makedirs(PATH)

    invIndexDict = defaultdict(list)

    counter = 0
    for n, d, fs in os.walk(OPATH):
        for directs in d:
            for name, subdirects, files in os.walk(os.path.join(OPATH, directs)):
                for fname in files:

                    fileDir = os.path.join(directs, fname)
                    fileId = directs + '_' + fname.rstrip('.txt')

                    with open(os.path.join(OPATH, fileDir), 'r') as fp:

                        appearTitle = defaultdict(bool)
                        firstLine = fp.readline()
                        checkTitle(firstLine, appearTitle)

                        fp.seek(0)

                        wordCounter = Counter()
                        for line in fp:  # Read line by line
                            tokenAndCount(line, wordCounter)

                        createInvIndex(wordCounter, appearTitle, invIndexDict, fileId)
                        counter += 1

                    print("Complete:", fileId)

    tfidf_all_doc(invIndexDict, counter)
    writeJson(invIndexDict)


if __name__ == '__main__':
    main()
