from nltk.tokenize import RegexpTokenizer
from collections import Counter, defaultdict
import os
import json

DPATH = "data/WEBPAGES_RAW"
OPATH = "data/WEBPAGES"
PATH = "data/INVINDEX"



# Tokenize the string and count the valid words
def tokenAndCount(s, wordCounter):
    tokenizer = RegexpTokenizer('[a-zA-Z]+')
    words = tokenizer.tokenize(s)
    wordCounter.update(words)


def createInvIndex(wordCounter, invIndexDict, fileId):
    for element in wordCounter:
        invIndexDict[element].append((fileId, wordCounter[element]))


# Sort the word count in decreasing order, and resolve ties alphabetically in ascending order
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


def main():
    os.system("rm -rf %s" % PATH)
    os.makedirs(PATH)

    invIndexDict = defaultdict(list)

    for n, d, fs in os.walk(OPATH):
        for directs in d:
            for name, subdirects, files in os.walk(os.path.join(OPATH, directs)):
                for fname in files:

                    fileDir = os.path.join(directs, fname)
                    fileId = directs + '_' + fname.rstrip('.txt')

                    with open(os.path.join(OPATH, fileDir), 'r') as fp:
                        wordCounter = Counter()
                        for line in fp:                     # Read line by line
                            tokenAndCount(line, wordCounter)
                        createInvIndex(wordCounter, invIndexDict, fileId)

                    print("Complete:", fileId)

    # invIndexDict = sort(invIndexDict)
    # writeTxt(invIndexDict)
    
    writeJson(invIndexDict)



if __name__ == '__main__':
    main()