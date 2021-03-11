# -*- coding: utf-8 -*-
import json

import pymysql
from django.contrib import messages
from django.shortcuts import render, redirect

from Hello.answer.bm25data import similarity
from Hello.answer.kbqa import kbqans
from Hello.models import Fault
from Hello.toolkit.pre_load import neo4jconn


def toAnswer(request):
    conn = pymysql.connect(host='123.56.52.53', port=3306, user='root', password='root',
                           database='source')
    cursor = conn.cursor()

    sql_select = "SELECT * FROM answer_info"
    cnt = cursor.execute(sql_select)
    conn.commit()
    score = 0
    for data in range(cnt):
        temp = cursor.fetchone()[2]
        score += float(temp)
    score = round(score, 3)
    accuracy_rate = round(score / cnt * 100, 2)

    return render(request, "answer.html", {'question_sum': cnt, "score": score, "accuracy_rate": accuracy_rate})

def simqa(question):
    arr = []
    list = similarity.initbm(question)
    l = list[0].strip()

    sql = 'select * from fault where phenomenon= %s'
    result = Fault.objects.raw(sql, [l])
    for i in result:
        arr.append(i.reason)
    arr = set(arr)
    return list, arr

def answer_question(request):
    # arr = []
    # qlist = []
    if request.POST:
        question = request.POST.get('question', None)

        print(question)
        if question:
            conn = pymysql.connect(host='123.56.52.53', port=3306, user='root', password='root',
                                   database='source')
            cursor = conn.cursor()

            insert_sql = "INSERT INTO answer_info(question, score) VALUES('%s',%s)" % (question, 1.0)
            cursor.execute(insert_sql)
            conn.commit()

            '''
            查询这个问题是否是原问题的推荐问题
            '''
            sql_select = "SELECT o_question, rank FROM origin_recomm_questions WHERE r_question = '%s'" % (question)
            cnt = cursor.execute(sql_select)
            conn.commit()
            # update_sql = ""
            print(cnt)
            if cnt > 0:
                result = cursor.fetchall()
                o_question = result[len(result)-1][0]
                rank = result[len(result)-1][1]
                update_sql = "update answer_info set score = '%s' WHERE question = '%s'" % (round(1 / rank, 3), o_question)
                cursor.execute(update_sql)
                conn.commit()
            '''
            第一种方法：利用neo4j数据库
            '''
            dp, result = kbqans.entity_ner(question.strip())

            '''
            第二种方法：利用bm25
            '''
            qlist, bm25 = simqa(question)

            bm25 = list(bm25)
            #存储bm25的前5条答案
            temp = []
            if len(bm25) > 5:
                for i in range(5):
                    temp.append(bm25[i])
            else:
                temp = bm25
            '''
            如果在neo4j数据库中搜索不到数据，输出bm25的前5条答案
            '''
            road = []
            if len(dp) == 0:
                arr = temp
            else:
                #将列表数据整合成neo4j数据格式
                arr = result
                db = neo4jconn
                for data in dp:
                    temp = db.findEntityRelation(data[0], data[1], data[2])
                    road.append(temp[0])
            qlist = list(qlist)

            res1 = []
            for i in range(len(arr)):
                temp = []
                temp.append(i)
                temp.append(arr[i])
                res1.append(temp)

            res2 = []
            for i in range(len(qlist)):
                temp = []
                temp.append(i)
                temp.append(qlist[i])
                res2.append(temp)

            for i in range(len(qlist)):
                string = qlist[i].replace("\n", "")
                string = string.replace("\r", "")
                num = i + 1
                insert_sql = "INSERT INTO origin_recomm_questions(o_question, r_question, rank) VALUES('%s','%s',%s)" % (question, string, num)
                print(insert_sql)
                cursor.execute(insert_sql)
                conn.commit()
            '''
            查询得分情况
            '''
            sql_select = "SELECT * FROM answer_info"
            cnt = cursor.execute(sql_select)
            conn.commit()
            score = 0
            for data in range(cnt):
                temp = cursor.fetchone()[2]
                score += float(temp)
            accuracy_rate = 0
            if cnt > 0:
                accuracy_rate = round(score / cnt * 100, 2)
            else:
                accuracy_rate = 0
            score = round(score, 3)
            return render(request, "answer.html", {'question_sum': cnt, "score": score, "accuracy_rate": accuracy_rate,
                                                   'answer': res1, 'qlist': res2, 'searchResult': json.dumps(road, ensure_ascii=False)})

        else:
            messages.success(request, "问题为空！")
            return redirect('/toAnswer/')

def answer_feedback(request):
    if request.POST:
        pass