import os
import json
from nltk.stem import WordNetLemmatizer
from collections import Counter, defaultdict
import math
import time
import numpy as np


class SearchEngine(object):
    def __init__(self, documentNum, path="./", opath="./", dpath="./"):
        start = time.time()
        self.path = path
        self.dpath = dpath
        self.opath = opath
        self.lemmatizer = WordNetLemmatizer()
        self.N = documentNum

        with open(os.path.join(self.dpath, "bookkeeping.json"), 'r') as f:
            self.book = json.load(f)
        with open(os.path.join(self.path, "postings.json"), 'r') as fp:
            self.invIndexDict = json.load(fp)
        with open(os.path.join(self.path, "tfidf.json"), 'r') as fp:
            self.doc_tfidf_dict = json.load(fp)

        self.word_id = {k: v for v, k in enumerate(self.invIndexDict)}
        print("Initialization Time: ", time.time() - start)

    def _tfidf(self, txt):
        # words = txt.split()
        word_count = Counter(txt)
        vector = {}
        for word in word_count.keys():
            if word not in self.word_id:
                continue
            id = str(self.word_id[word])
            tf = word_count[word]
            df = len(self.invIndexDict[word])
            vector[id] = (1 + math.log(tf, 10)) * math.log(self.N / df, 10)
        return vector

    def get_similarity(self, tf_idf_vec1, tf_idf_vec2):
        '''
        :param tf_idf_vec1:
        :param tf_idf_vec2:
        :return: Cosine similarity of two tf-idf vectors
        '''
        # print(tf_idf_str1)
        numerator = 0
        for id in tf_idf_vec1.keys():
            if id in tf_idf_vec2.keys():
                numerator += tf_idf_vec1[id] * tf_idf_vec2[id]
        norm1 = np.array(list(tf_idf_vec1.values()))
        norm1 = np.sqrt(np.sum(norm1 ** 2))
        norm2 = np.array(list(tf_idf_vec2.values()))
        norm2 = np.sqrt(np.sum(norm2 ** 2))
        return numerator / (norm1 * norm2)

    def get_grade(self, query, title_dict, doc_id):
        '''
        :param query:
        :param doc_txt:
        :param doc_id:
        :return: grade is the similarity between query and doc plus the title weight
        '''
        tf_idf_query = self._tfidf(txt=query)
        grade = self.get_similarity(tf_idf_query, self.doc_tfidf_dict[doc_id])
        grade += 0.01 * title_dict[doc_id]

        return grade

    def search(self, query, max_num = 20):
        query_words = list(map(lambda x: self.lemmatizer.lemmatize(x.lower()), query.split()))
        # query = ' '.join(query_words)
        set_list = []
        title_dict = defaultdict(int)
        for word in query_words:
            if word in self.invIndexDict.keys():
                curList = []
                for item in self.invIndexDict[word]:
                    curList.append(item[0])
                    if item[2]:
                        title_dict[item[0]] += 1

                set_list.append(set(curList))

                # set_list.append(set(list(map(lambda doc: doc[0], self.invIndexDict[word]))))

        if len(set_list) == 0:
            print("No Result Found!")
            return [], 0

        set_list.sort(key=lambda s: len(s))
        doc_set = set.intersection(*set_list)

        grade = {}
        for id in doc_set:
            grade[id] = self.get_grade(query_words, title_dict, id)
        # Sort grade
        sorted_docs = sorted(grade, key=lambda key: (-grade[key], key))
        count = 0
        res = []
        while count < len(sorted_docs):
            id = sorted_docs[count].split("_")[0] + "/" + sorted_docs[count].split("_")[1]
            res.append(self.book[id])
            count += 1

        return res, count
