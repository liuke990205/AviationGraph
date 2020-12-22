# encoding=utf-8

"""
基于命令行的在线预测方法
@Author: Macan (ma_cancan@163.com)
"""

import pandas as pd
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
#from global_config import Logger
from app.kbase import global_config
import numpy as np
import codecs
import pickle
from datetime import time, timedelta, datetime
# import terminal_predict
from app.kbase import terminal_predict

# from Data.load_dbdata import upload_data
from app.kbase.Data import load_dbdata
import pdb
# from run_similarity import BertSim
from app.kbase import run_similarity
# 模块导入 https://blog.csdn.net/xiongchengluo1129/article/details/80453599

# loginfo = Logger("recommend_articles.log", "info")
loginfo = global_config.Logger("recommend_articles.log", "info")

# bs = BertSim()
bs = run_similarity.BertSim()
bs.set_mode(tf.estimator.ModeKeys.PREDICT)

while True:
    print('input the test sentence:')
    question = input()
    ner = terminal_predict.predict_online(question)
    # print(ner)
    # case: entity Fuzzy Match
    # 找出所有包含这些实体的三元组
    sql_e0_a1 = "select * from nlpccQA where entity like '%" + ner + "%' order by length(entity) asc limit 20"
    # sql查出来的是tuple，要转换成list才不会报错
    result_e0_a1 = list(load_dbdata.upload_data(sql_e0_a1))


    if len(result_e0_a1) > 0:
        flag_fuzzy = True
        # 非语义匹配，加快速度
        # l1[0]: entity
        # l1[1]: attribute
        # l1[2]: answer
        flag_ambiguity = True
        for l in result_e0_a1:
            if l[1] in question or l[1].lower() in question or l[1].upper() in question:
                flag_fuzzy = False
                print(l[2])
                flag_ambiguity = False
        # 非语义匹配成功，继续下一次

        # 语义匹配
        if flag_ambiguity==True:
            result_df = pd.DataFrame(result_e0_a1, columns=['entity', 'attribute', 'value'])
            # loginfo.logger.info(result_df.head(100))

            attribute_candicate_sim = [(k, bs.predict(question, k)[0][1]) for k in result_df['attribute'].tolist()]
            attribute_candicate_sort = sorted(attribute_candicate_sim, key=lambda candicate: candicate[1], reverse=True)
            #loginfo.logger.info("\n".join([str(k)+" "+str(v) for (k, v) in attribute_candicate_sort]))

            answer_candicate_df = result_df[result_df["attribute"] == attribute_candicate_sort[0][0]]
            # answer_candicate_df 答案三元组
            for row in answer_candicate_df.index:
                print(answer_candicate_df.loc[row, "value"])
'''
    for row in answer_candicate_df.index:
        if estimate_answer(answer_candicate_df.loc[row, "value"], answer):
            correct += 1
        else:
            loginfo.logger.info("\t".join(answer_candicate_df.loc[row].tolist()))   
'''