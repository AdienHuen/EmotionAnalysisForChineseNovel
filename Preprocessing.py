# encoding:utf-8
import codecs
import os
def read_file(fileName = "Book/三国演义/1.txt"):
    f = codecs.open(fileName, encoding="utf-8")
    rows = f.readlines()
    f.close()
    return filter_tag(rows)

def filter_tag(rows = []):
    contents = []
    for row in rows:
        row = row.replace(u"\t", u"").replace(u"\r", u"").\
            replace(u"\n", u"").replace(u"    ", u"").\
            replace(u" ", u"")
        if row != u"":
            contents.append(row)
            # print row
    # print ""
    return contents

def get_files_num(path = "Book/三国演义"):
    files = os.listdir(path)
    return files.__len__()

def read_dict(path = "emotion/zhenyu1.txt"):
    emotion_dict = {}
    f = codecs.open(path)
    rows = f.readlines()
    terms = []
    for row in rows:
        if row.__contains__(" "):
            row = row.replace("\r","").replace("\n","")
            term = row.split(" ")
            terms.append(term)
            # print term
    for term in terms:
        if term[1] == "1":
            emotion_dict[term[0]] = 1
        if term[1] == "0":
            emotion_dict[term[0]] = -1
    # for key in emotion_dict.keys():
    #     print key,emotion_dict.get(key)
    return emotion_dict
read_dict()