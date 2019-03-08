import pymongo
import os
import json
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["search_engine_database"]

DPATH = "data/WEBPAGES_RAW"
OPATH = "data/WEBPAGES"
PATH = "data/INVINDEX"

def create_database():
    with open(os.path.join(DPATH, "bookkeeping.json"), 'r') as f:
        mybook = json.load(f)
    with open(os.path.join(PATH, "postings.json"), 'r') as fp:
        myinvIndexDict = json.load(fp)
    inv_index = mydb["inv_index"]
    book = mydb["book"]
    for key in mybook.keys():
        print("Now processing id: " + key + " url: " + mybook[key] + '\n')
        query = {"id":key, "url":mybook[key]}
        newvalues = {"$set": {"id":key, "url":mybook[key]}}
        book.update_one(query,newvalues,upsert=True)
    for key in myinvIndexDict.keys():
        print("Now processing word: " + key)
        query = {"word":key, "postings":myinvIndexDict[key]}
        inv_index.update_one(query,newvalues,upsert=True)

if __name__ == '__main__':
    create_database()



