import search
import time

if __name__ == "__main__":
    N = 32044
    search_engine = search.SearchEngine(N, path="data/INVINDEX", opath="data/WEBPAGES",
                                        dpath="data/WEBPAGES_RAW")

    query = input("Enter your query: ")
    while query != "exit":
        start = time.time()
        res, count = search_engine.search(query)
        print("Elapsed Time: ", time.time() - start)
        print("Total result count: ", count)

        i = 0
        command = ""
        while command == "" and i < count:
            j = 0
            while j < 20 and i < count:
                print(i + 1, ":", res[i])
                j += 1
                i += 1
            command = input(":")

        query = input("Enter your query: ")
