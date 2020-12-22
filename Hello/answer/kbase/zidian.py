import jieba
import pandas as pd


def preprocess(path):
    text = ""
    fenci = open(path, "r", encoding="utf-8").read()
    jieba.load_userdict("C:/Users/idmin/Desktop/dict.txt")
    fenci = jieba.cut(fenci)
    #fenci = "/".join(fenci)
    for word in fenci:
        text=text+word
    return text
print(preprocess('C:/Users/idmin/Desktop/one.txt'))
