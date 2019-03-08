import os
import json
from nltk.stem import WordNetLemmatizer
from collections import Counter
import math
import numpy as np


class TFIDFVector(object):
    def __init__(self, txt, N, invIndexDict, word_id):
        '''
        :param str: Orginal String
        :param N: The number of total document, a constant
        :param invIndexDict: the length of the value for each key is df
        :param word_id: vocabulary, given a word, return the id of this word
        '''
        self.original_str = txt
        self.vector = {}
        words = txt.split()
        word_count = Counter(words)
        for word in word_count.keys():
            if word not in word_id.keys():
                continue
            id = str(word_id[word])
            tf = word_count[word]
            df = len(invIndexDict[word])
            self.vector[id] = (1 + math.log(tf, 10)) * math.log(N / df, 10)


class SearchEngine(object):
    def __init__(self, document_num, path="./", dpath="./", opath="./"):
        self.path = path
        self.dpath = dpath
        self.opath = opath
        self.lemmatizer = WordNetLemmatizer()
        self.doc_tfidf_dict = {}
        with open(os.path.join(self.opath, "bookkeeping.json"), 'r') as f:
            self.book = json.load(f)
        with open(os.path.join(self.path, "postings.json"), 'r') as fp:
            self.invIndexDict = json.load(fp)
        self.N = document_num
        self.word_id = {k: v for v, k in enumerate(self.invIndexDict)}
        self._tfidf_init()

    def _tfidf_init(self):
        for info in list(self.book.keys()):
            i = info.split('/')
            dir_id = i[0]
            doc_id = i[1]
            with open(self.opath + "/" + dir_id + "/" + doc_id + ".txt", 'r') as file:
                doc_txt = file.read()
            self.doc_tfidf_dict[dir_id + "_" + doc_id] = TFIDFVector(doc_txt, self.N,
                                                    self.invIndexDict, self.word_id)


    def get_similarity(self, tf_idf_str1, tf_idf_str2):
        '''
        :param tf_idf_str1:
        :param tf_idf_str2:
        :return: Cosine similarity of two tf-idf vectors
        '''
        # print(tf_idf_str1)
        numerator = 0
        for id in tf_idf_str1.vector.keys():
            if id in tf_idf_str2.vector.keys():
                # print(tf_idf_str1.vector[id])
                numerator += tf_idf_str1.vector[id] * tf_idf_str2.vector[id]
        norm1 = 0
        for id in tf_idf_str1.vector.keys():
            norm1 += tf_idf_str1.vector[id] ** 2
        norm1 = math.sqrt(norm1)
        norm2 = 0
        for id in tf_idf_str2.vector.keys():
            norm2 += tf_idf_str2.vector[id] ** 2
        norm2 = math.sqrt(norm2)
        return numerator / (norm1 * norm2)

    def get_grade(self, query, doc_txt, id):
        '''
        :param query:
        :param doc_txt:
        :param id:
        :return: grade deault is the similarity between query and doc
        If the vector of doc has already saved, retrieve it, else calculate it and save it
        '''
        tf_idf_query = TFIDFVector(txt=query, N=self.N, invIndexDict=self.invIndexDict,
                                   word_id=self.word_id)
        grade = self.get_similarity(tf_idf_query, self.doc_tfidf_dict[id])
        return grade

    def search(self, query, max_num=10):
        query_words = list(map(lambda x: self.lemmatizer.lemmatize(x.lower()), query.split()))
        query = ' '.join(query_words)
        doc_set = set()
        for word in query_words:
            cur_set = set(list(map(lambda doc: doc[0], self.invIndexDict[word])))
            if len(doc_set) == 0:
                doc_set = set(cur_set)
            else:
                doc_set = doc_set.intersection(cur_set)
        if len(doc_set) == 0:
            print("No Result Found!")
            return

        grade = {}
        for id in doc_set:
            dir_id = id.split("_")[0]
            doc_id = id.split("_")[1]
            file_dir = self.opath + "/" + dir_id + "/" + doc_id + ".txt"
            doc_txt = ""
            for line in open(file_dir, "r"):
                doc_txt += line
            grade[id] = self.get_grade(query, doc_txt, id)
        # Sort grade
        sorted_docs = sorted(grade, key=lambda key: (-grade[key], key))
        count = 0
        res = []
        while count < max_num and count < len(sorted_docs):
            id = sorted_docs[count].split("_")[0] + "/" + sorted_docs[count].split("_")[1]
            res.append(self.book[id])
            count += 1

        return res
