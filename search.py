import os
import json
from nltk.stem import WordNetLemmatizer

class TFIDFVector(object):
    def __init__(self, txt, N, invIndexDict, word_id):
        '''
        :param str: Orginal String
        :param N: The number of total document, a constant
        :param invIndexDict: the length of the value for each key is df
        :param word_id: vocabulary, given a word, return the id of this word
        '''
        from collections import defaultdict
        import math
        lemmatizer = WordNetLemmatizer()
        self.original_str = txt
        self.vector = {}
        word_count = defaultdict(int)
        words = txt.split()
        for word in words:
            word = lemmatizer.lemmatize(word.lower())
            word_count[word] += 1
        for word in word_count.keys():
            #The vocabular don't have this word
            if word not in word_id:
                continue
            id = word_id[word]
            tf = word_count[word]
            df = len(invIndexDict[word])
            self.vector[id] = (1 + math.log(tf,10)) * math.log(N/df,10)



class SearchEngine(object):
    def __init__(self, document_num, path="./", dpath="./", opath="./"):
        self.path = path
        self.dpath = dpath
        self.opath = opath
        self.lemmatizer = WordNetLemmatizer()
        self.doc_tfidf_dict = {}
        with open(os.path.join(self.dpath, "bookkeeping.json"), 'r') as f:
            self.book = json.load(f)
        with open(os.path.join(self.path, "postings.json"), 'r') as fp:
            self.invIndexDict = json.load(fp)
        self.N = document_num
        self.word_id = {k: v for v, k in enumerate(self.invIndexDict)}


    def get_similarity(self, tf_idf_str1, tf_idf_str2):
        '''
        :param tf_idf_str1:
        :param tf_idf_str2:
        :return: Cosine similarity of two tf-idf vectors
        '''
        import math
        numerator = 0
        for id in tf_idf_str1.vector.keys():
            if id in tf_idf_str2.vector.keys():
                numerator += tf_idf_str1.vector[id] * tf_idf_str2.vector[id]
        norm1 = 0
        for id in tf_idf_str1.vector.keys():
            norm1 += tf_idf_str1.vector[id]**2
        norm1 = math.sqrt(norm1)
        norm2 = 0
        for id in tf_idf_str2.vector.keys():
            norm2 += tf_idf_str2.vector[id]**2
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
        tf_idf_query = TFIDFVector(txt=query, N=self.N, invIndexDict=self.invIndexDict, word_id=self.word_id)
        tf_idf_doc = None
        if id in self.doc_tfidf_dict:
            tf_idf_doc = self.doc_tfidf_dict[id]
        else:
            tf_idf_doc = TFIDFVector(doc_txt,self.N,self.invIndexDict,self.word_id)
            self.doc_tfidf_dict[id] = tf_idf_doc

        grade = self.get_similarity(tf_idf_query, tf_idf_doc)
        return grade


    def search(self, query, max_num=10):
        #query = lemmatizer.lemmatize(query.lower())
        query_words = query.split()
        doc_set = set()
        for word in query_words:
            word = self.lemmatizer.lemmatize(word.lower())
            cur_set = set()
            for each in self.invIndexDict[word]:
                cur_set.add(each[0])
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
            grade[id] = self.get_grade(query, doc_txt,id)
        #Sort grade
        sorted_docs = sorted(grade, key=lambda key: (-grade[key], key))
        count = 0
        res = []
        while count < max_num and count < len(sorted_docs):
            id = sorted_docs[count].split("_")[0] + "/" + sorted_docs[count].split("_")[1]
            res.append(self.book[id])
            count += 1
        return res
