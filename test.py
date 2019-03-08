import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
mycol = mydb["customers"]

myquery = {"address":"happy"}
#newvalues = { "$set": { "address": "happy","value": "123","test":[(1,2),(3,4)] } }
#mycol.update_one(filter=myquery, update=newvalues,upsert=True)

mydoc = mycol.find_one(myquery)


print(len({}))