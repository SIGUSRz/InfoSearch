import os
import json
from nltk.stem import WordNetLemmatizer
import pymongo

class TFIDFVector(object):
    def __init__(self, txt, N, invIndexDict, word_id, vec={}):
        import copy
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
        self.vector = copy.copy(vec)
        if len(self.vector) != 0:
            return
        word_count = defaultdict(int)
        words = txt.split()
        for word in words:
            word = lemmatizer.lemmatize(word.lower())
            word_count[word] += 1
        for word in word_count.keys():
            #The vocabulary don't have this word
            if word not in word_id:
                continue
            id = str(word_id[word])
            tf = word_count[word]
            df = len(invIndexDict[word])
            self.vector[id] = (1 + math.log(tf,10)) * math.log(N/df,10)



class SearchEngine(object):
    def __init__(self, document_num, path="./", opath="./"):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.database = self.client["search_engine_database"]
        self.book = self.database["book"]
        self.doc_tfidf_dict_db = self.database["doc_tfidf"]
        self.doc_tfidf_dict = {}
        self.path = path
        self.opath = opath
        self.lemmatizer = WordNetLemmatizer()

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

    def get_grade(self, query, doc_id):
        '''
        :param query:
        :param doc_txt:
        :param id:
        :return: grade deault is the similarity between query and doc
        If the vector of doc has already saved, retrieve it, else calculate it and save it
        '''
        import bson

        tf_idf_query = TFIDFVector(txt=query, N=self.N, invIndexDict=self.invIndexDict, word_id=self.word_id)
        tf_idf_doc = None
        doc_query = {"id":doc_id}
        if doc_id in self.doc_tfidf_dict:
            tf_idf_doc = self.doc_tfidf_dict[doc_id]
        else:
            query_res = self.doc_tfidf_dict_db.find_one(doc_query)
            vec = bson.BSON.decode(query_res["tfidf_vec"])
            tf_idf_doc = TFIDFVector("", self.N, self.invIndexDict, self.word_id, vec=vec)
            self.doc_tfidf_dict[doc_id] = tf_idf_doc

        # if query_res != None:
        #     vec = bson.BSON.decode(query_res["tfidf_vec"])
        #     tf_idf_doc = TFIDFVector(doc_txt, self.N, self.invIndexDict, self.word_id, vec=vec)
        # else:
        #     tf_idf_doc = TFIDFVector(doc_txt, self.N, self.invIndexDict, self.word_id)
        #     vec = bson.BSON.encode(tf_idf_doc.vector)
        #     query = {"id": id, "tfidf_vec": vec}
        #     newvalues = {"$set": {"id": id, "tfidf_vec": vec}}
        #     self.doc_tfidf_dict_db.update(query,newvalues,upsert=True)

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
        for each_id in doc_set:
            # dir_id = each_id.split("_")[0]
            # doc_id = each_id.split("_")[1]
            # doc_txt = ""
            # file_dir = self.opath + "/" + dir_id + "/" + doc_id + ".txt"
            # doc_txt = ""
            # for line in open(file_dir, "r"):
            #     doc_txt += line
            grade[each_id] = self.get_grade(query, each_id)

        #Sort grade
        sorted_docs = sorted(grade, key=lambda key: (-grade[key], key))
        count = 0
        res = []
        while count < max_num and count < len(sorted_docs):
            id = sorted_docs[count].split("_")[0] + "/" + sorted_docs[count].split("_")[1]
            query = {"id":id}
            url = self.book.find_one(query)["url"]
            res.append(url)
            count += 1
        return res



if __name__ == '__main__':
    N = 32044
    search_engine = SearchEngine(N, path="data/INVINDEX",opath="data/WEBPAGES")
    while True:
        query = input("Enter your query:")
        res = search_engine.search(query)
        print(res)

    # path = "data/INVINDEX"
    # OPATH = "data/WEBPAGES"
    # import bson
    # count = 0
    # for n, d, fs in os.walk(OPATH):
    #     for directs in d:
    #         for name, subdirects, files in os.walk(os.path.join(OPATH, directs)):
    #             for fname in files:
    #
    #                 fileDir = os.path.join(directs, fname)
    #                 fileId = directs + '_' + fname.rstrip('.txt')
    #                 doc_txt = ""
    #                 for each_line in open(os.path.join(OPATH, fileDir), 'r'):
    #                     doc_txt += (each_line + " ")
    #
    #                 tf_idf_doc = TFIDFVector(doc_txt, search_engine.N, search_engine.invIndexDict, search_engine.word_id)
    #                 vec = bson.BSON.encode(tf_idf_doc.vector)
    #                 query = {"id": fileId, "tfidf_vec": vec}
    #                 newvalues = {"$set": {"id": fileId, "tfidf_vec": vec}}
    #                 search_engine.doc_tfidf_dict.update(query, newvalues, upsert=True)
    #                 count += 1
    #                 print("Complete: " + fileId + " The total complete: "+ str(count))