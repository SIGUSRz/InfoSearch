import search
import time

if __name__ == "__main__":
    N = 32044
    search_engine = search.SearchEngine(N, path="data/INVINDEX", opath="data/WEBPAGES",
                                        dpath="data/WEBPAGES_RAW")
    while True:
        query = input("Enter your query:")
        start = time.time()
        res = search_engine.search(query)
        print(res)
        print("Elapsed Time: ", time.time() - start)
