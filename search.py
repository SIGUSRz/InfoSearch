import os
import json
from nltk.stem import WordNetLemmatizer

DPATH = "data/WEBPAGES_RAW"
OPATH = "data/WEBPAGES"
PATH = "data/INVINDEX"



def search(book, invIndexDict, query, maxNumResult):
    resultRaw = invIndexDict[query]
    count = 0
    searchResult = []
    for result in resultRaw:
        folder, fname = result[0].split('_')
        # print(folder, fname)
        book_key = os.path.join(folder, fname)      
        searchResult.append(book[book_key])

        count += 1

    if count > maxNumResult:
        countShown = maxNumResult
    else:
        countShown = count
        
    print('Total result count: {}, result shown: {}'.format(count, countShown))
    print('\n'.join(searchResult[:countShown]))


def main():
    lemmatizer = WordNetLemmatizer()
    
    with open(os.path.join(DPATH, "bookkeeping.json"), 'r') as f:
        book = json.load(f)

    with open(os.path.join(PATH, "postings.json"), 'r') as fp:
        invIndexDict = json.load(fp)

    maxNumResult = 20
    query = input("Enter your query: ")

    while query != 'exit':
        query = lemmatizer.lemmatize(query.lower())
        search(book, invIndexDict, query, maxNumResult)
        query = input("Enter your query: ")


if __name__ == "__main__":
    main()
