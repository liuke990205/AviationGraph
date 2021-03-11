import jieba
import codecs as cs
import numpy as np
import os
from itertools import combinations
import re

dictionary_path = "Hello/answer/kbqa/data/dictionary.txt"

with open(dictionary_path, "r", encoding="utf-8") as f:
    dic_list = f.read().splitlines()

max_length = len(sorted(dic_list, key=lambda x: len(x))[-1])

def entity_seq(question):
    entity_res = []
    ''' 1.jieba分词后，找到实体最长匹配'''
    def entity_dicjieba(question):
        sentence = question
        with cs.open(dictionary_path, 'r', 'utf-8') as fp:
            segment_dic = {}
            for line in fp:
                if line.strip():
                    segment_dic[line.strip()] = 0
        jieba.load_userdict(dictionary_path)
        # mentions = []
        tokens = jieba.lcut(sentence)
        # print(tokens)
        for t in tokens:
            if t in segment_dic:
                # mentions.append(t)
                entity_res.append(t)
        # return mentions

    # sentence="飞机动力系统引擎真牛逼呀哈付费" #待分词的句子
    ans_forward=[]  #存放正向匹配的结果
    ans_reverse=[]  #存放逆向匹配的结果，相当于栈
    # max_length=3    #分词字典中最大长度字符串的长度

    # 要是分词字典列表中最大长度字符串的长度一眼看不出来，可采用下一行的形式
    # max_length=len(sorted(dic_list, key=lambda x: len(x))[-1])
    '''2.正向最大匹配'''
    # 读取文本文档数据进词典dic_list
    def entity_forward(question,max_length):
        sentence = question
        len_row=len(sentence)  #len_orw为当前为划分句子的长度
        while len_row>0:       #当前待划分句子长度为0时，结束划分
            divide = sentence[0:max_length]    #从前向后截取长度为max_length的字符串
            while divide not in dic_list:      #当前截取的字符串不在分词字典中，则进循环
                if len(divide)==1:             #当前截取的字符串长度为1时，说明分词字典无匹配项
                    break                      #直接保留当前的一个字
                divide=divide[0:len(divide)-1] #当前截取的字符串长度减一
            if divide in dic_list:
                entity_res.append(divide)
            ans_forward.append(divide)         #记录下当前截取的字符串
            sentence = sentence[len(divide):]  #截取未分词的句子
            len_row = len(sentence)            #记录未分词的句子的长度
        print("\'正向最大匹配\'的分词结果为：",ans_forward)

    '''3.逆向最大匹配'''
    def entity_rev(question,max_length):
        sentence = question
        len_row=len(sentence)
        while len_row>0 :
            divide = sentence[-max_length:]
            while divide not in dic_list:
                if len(divide)==1:
                    break
                divide=divide[1:]   #注意这里缩短截取字符串是缩短前部分，保留后部分
            ans_reverse.append(divide)
            if divide in dic_list:
                entity_res.append(divide)
            sentence = sentence[0:len(sentence)-len(divide)]
            len_row = len(sentence)
        print("\'逆向最大匹配\'的分词结果为：",ans_reverse[::-1])#注意是倒序输出

    entity_dicjieba(question)
    entity_forward(question, max_length)
    entity_rev(question, max_length)

    res = list(set(entity_res))
    return res

# if __name__ == '__main__':
#     question = "研究生命起源"
#     res = entity_seq(question)
#     print(res)