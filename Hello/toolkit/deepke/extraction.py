#coding=utf-8

#读取文本文件
#清洗&整理
#基于词典的实体识别（暂定）
#本体约束
#生成待抽取csv
#格式转换并传入relationlist

import jieba
import re


def readfile(text):
    sen_list = []

    result = re.split("。", text)
    if "\n" in result:
        result.remove("\n")
    for i in range(len(result)):
        sen = str((result[i]).replace('\n', '').replace('\r', '') + "。\n")
        sen_list.append(sen)
    print("ok")

    #readfile(test_dir)

    dir1 = "/dic.txt"
    dir2 = "/testfile2121.csv"

    jieba.load_userdict(dir1)

    f1 = open(dir1, 'r')
    f2 = open(dir2, 'a')
    dic_entity = []
    dic_entity_type_ori = []
    dic_entity_type = []
    sen_entity = []
    entity_type = []

    for w in f1.readlines():            #读取词典中的实体
        w_array = w.split(" ")
        dic_entity.append(w_array[0])
        dic_entity_type_ori.append(w_array[2].replace("\n",""))
    #print(dic_entity)

    for type in dic_entity_type_ori:
        if type == "hkq":
            dic_entity_type.append("航空器")
            continue
        if type == "wq":
            dic_entity_type.append("武器")
            continue
        if type == "sxmx":
            dic_entity_type.append("数学模型")
            continue
        if type == "ckwd":
            dic_entity_type.append("参考文档")
            continue
        if type == "xt":
            dic_entity_type.append("系统")
            continue
        if type == "xnzb":
            dic_entity_type.append("性能指标")
            continue
        if type == "csz":
            dic_entity_type.append("参数值")
            continue



    for i in range(len(sen_list)):

         seg1 = jieba.cut(sen_list[i])
         seg2 = "/".join(seg1)
         seg_list = seg2.split("/")               #分词

         for j in range(len(seg_list)):
             for k in range(len(dic_entity)):
                if seg_list[j] == dic_entity[k]:
                    #print(seg_list[j])
                    sen_entity.append(dic_entity[k])
                    entity_type.append(dic_entity_type[k].replace("\n",""))  #去除迷之换行

         if len(sen_entity) == 2 and sen_entity[0] != sen_entity[1]:
             print(sen_entity)
             flag = _relation_schema(entity_type[0],entity_type[1])  #利用schema提供约束
             if(flag == 1):
                sentence = sen_list[i].replace("\n","")
                s =str(sentence) +  "," + str(sen_entity[0]) + ","  + str(entity_type[0]) + "," + str(sen_entity[1]) +  ","  + str(entity_type[1]) +"\n"  #
                f2.write(s)

             if(flag == 2):
                 sentence = sen_list[i].replace("\n", "")
                 entity_type[0],entity_type[1] = entity_type[1],entity_type[0]
                 s =str(sentence) +  "," + str(sen_entity[0]) + ","  + str(entity_type[0]) + "," + str(sen_entity[1]) +  ","  + str(entity_type[1]) +"\n" #
                 f2.write(s)

         if len(sen_entity) > 2 :
             for j in range(len(sen_entity)):
                 for k in range(len(sen_entity)-j-1):  #每个实体及其后的单词两两配对
                     if sen_entity[j] != sen_entity[j+k+1]:
                        #print(sen_entity[j],sen_entity[j+k+1])
                        #print(sen_entity[j], sen_entity[k+j+1])
                        flag = _relation_schema(entity_type[j], entity_type[k+j+1])  #利用schema提供约束
                        #print(flag)
                        if (flag == 1):
                            sentence = sen_list[i].replace("\n","")
                            s = str(sentence) + "," + str(sen_entity[j]) + "," + str(entity_type[j]) + "," + str(
                                sen_entity[j + k + 1]) + "," + str(entity_type[j + k + 1]) +"\n" #
                            f2.write(s)
                        if (flag == 2):
                            sentence = sen_list[i].replace("\n","")
                            s = str(sentence) + "," + str(sen_entity[j + k + 1]) + "," + str(entity_type[k + j + 1]) + "," + str(
                                sen_entity[j]) + "," + str(entity_type[j]) +"\n"   #调换一下
                            f2.write(s)


         sen_entity = []
         entity_type = []


         #words = pseg.cut([i])
         #for w in words :
         #   print(w.word,w.flag)

def _relation_schema(type1,type2):

    schemafile = open("/schema.txt", 'r')
    schema_type1 = []
    schema_type2 = []

    for w in schemafile.readlines():
        w_array = w.split(" ")
        schema_type1.append(w_array[0])
        schema_type2.append(w_array[1])

    for i in range(len(schema_type1)):
        if type1 == schema_type1[i] and type2 == schema_type2[i]:
            return 1

    for i in range(len(schema_type1)):
        if type2 == schema_type1[i] and type1 == schema_type2[i]:
            #print(type1,type2)
            #print("OK")
            return 2

    return 0



