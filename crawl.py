from lxml import etree
from lxml import html
from urllib.parse import *
from nltk.stem import WordNetLemmatizer
import re
import os
import json

DPATH = "data/WEBPAGES_RAW"
OPATH = "data/WEBPAGES"
lemmatizer = WordNetLemmatizer()


def is_valid(url):
    parsed = urlparse(url)
    # print(parsed)
    # if parsed.path not in {"http", "https", "www"}:
    #     return False
    try:
        return ".ics.uci.edu" in parsed.path \
               and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico"
                                + "|png|tiff?|mid|mp2|mp3|mp4"
                                + "|txt"
                                + "|h|php|bib|py|out"
                                + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                                + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|"
                                + "exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1"
                                + "|thmx|mso|arff|rtf|jar|csv"
                                + "|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        return False


def ul_handler(el):
    yield list(itertext(el, with_tail=False))
    if el.tail:
        yield el.tail


def joinadj(iterable, join=' '.join):
    adj = []
    for item in iterable:
        if isinstance(item, str):
            adj.append(item)  # save for later
        else:
            if adj:  # yield items accumulated so far
                yield join(adj)
                del adj[:]  # remove yielded items
            yield item  # not a string, yield as is

    if adj:  # yield the rest
        yield join(adj)


def _get(handlers, el):
    for i in handlers.get(el.tag, itertext)(el):
        yield i


def itertext(root, with_tail=True):
    handlers = dict(ul=ul_handler)
    if root is None:
        yield None
    else:
        if root.text:
            yield root.text
        for el in root:
            if el.tag is etree.Comment or \
                    el.tag == "script" or \
                    el.tag == "style" or \
                    el.tag == "title":
                continue
            # yield from handlers.get(el.tag, itertext)(el)
            yield _get(handlers, el)
        if with_tail and root.tail:
            yield root.tail


def identify(string):
    return not re.match(".*\.(css|js|bmp|gif|jpe?g|ico"
                        + "|png|tiff?|mid|mp2|mp3|mp4"
                        + "|txt"
                        + "|h|php|bib|py|out"
                        + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                        + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|"
                        + "exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1"
                        + "|thmx|mso|arff|rtf|jar|csv"
                        + "|rm|smil|wmv|swf|wma|zip|rar|gz)", string.lower())


def normalize(text):
    if not text:
        return ''
    if isinstance(text, str):
        text = text.split(' ')
        text = list(filter(None, text))
        text = list(filter(lambda x: not re.search(r':\/\/', x), text))
        text = list(filter(lambda x: identify(x), text))
        text = list(map(lambda x: re.sub('[0-9]', '', x), text))
        text = list(map(lambda x: re.sub('[^a-zA-z]+', ' ', x), text))
        text = list(filter(lambda x: x != ' ' and x != '', text))
        if len(text) == 0:
            return ''
        text = ' '.join(text)
        text = text.split(' ')
        text = list(filter(lambda x: x != ' ' and x != '', text))
        text = list(map(lambda x: lemmatizer.lemmatize(x.lower()), text))
        text = ' '.join(text)
        return text
    else:
        text = list(map(lambda x: normalize(x), text))
        text = list(filter(lambda x: x != ' ' and x != '', text))
        return ' '.join(text)


if __name__ == "__main__":
    with open(os.path.join(DPATH, "bookkeeping.json"), 'r') as f:
        book = json.load(f)
    os.system("rm -rf %s" % OPATH)
    counter = 0
    for n, d, fs in os.walk(DPATH):
        for directs in d:
            # for directs in ["7"]:
            for name, subdirects, files in os.walk(os.path.join(DPATH, directs)):
                os.makedirs(os.path.join(OPATH, directs))
                for f in files:
                    # for f in ["410"]:
                    book_key = os.path.join(directs, f)
                    if not is_valid(book[book_key]):
                        continue
                    path = os.path.join(DPATH, book_key)
                    print("Processing %s %s" % (path, book[book_key]))
                    tree = html.parse(path)
                    content = list(joinadj(itertext(tree.getroot())))
                    if content[0] is None:
                        continue
                    content = normalize(content)
                    title = tree.find('.//title')
                    if title is not None:
                        title = normalize(title.text)
                    else:
                        title = ''
                    content = title + '\n' + content
                    if content != '\n':
                        counter += 1
                        with open(os.path.join(OPATH, book_key + ".txt"), 'w') as fp:
                            fp.write(content)
                        print("Done %s" % path)
    print("Done all %d" % counter)
