from Hello.answer.kbqa import entity
from Hello.answer.kbqa import sim
import math
import re
import datetime
import time
from py2neo import Graph, Node, Relationship

# 连接neo4j数据库，输入地址、用户名、密码
graph = Graph("http://localhost:7474", username="neo4j", password='root')


tx = graph.begin()

def entity_ner(question):
    # 答案列表
    result = []


    # 候选实体

    entity_list = entity.entity_seq(question)
    print(entity_list)

    # 候选关系
    # 编辑距离 score1 = levenshtein(sentence, s)
    # 余弦相似度 score2 = compute_cosine(sentence, s)

    # for e in entity_list:

    def Screen(searchResult,num):
        tableData = []
        for i in range(0, len(searchResult)):
            tableData.append(searchResult[i][num])
        return tableData

    # 1.对每一个候选实体，首先找出和他相连的第一跳所有邻居，即，部件（实体）———现象————故障现象，也就是所有的故障现象
    # 2.找到故障现象相似度评分最高的，保留分数和故障现象，通过二跳，查询到故障原因
    # 3.执行1，2，和当前score对比，如果分数高，则保留分高的，若分数相等，也保留

    # 全局评分
    scoreall = 0
    # 对于每一个候选实体
    for e in entity_list:
        # 查询所有一跳邻居，放在relation中
        string  = "match(n:entity{name:'" + e +  "'})-[r:`现象`]->(m) return m.name"
        relation = []
        relation1 = tx.run(string)
        relation2 = []
        for r in relation1:
            relation2.append(r)
        relation = Screen(relation2,'m.name')
        print(relation)
        # score_matrix = [[] for i in range(len(leftlist)+1)]

        # 对该实体相连的每一个故障现象和问题（去掉实体后剩余部分）进行相似度评分
        # 句子去掉实体后剩余的部分

        sen = question.split(e)
        # 实体在中间，取后面部分
        if len(sen) > 1:
            sentence = sen[1]
        else:
            sentence = sen
        print(sentence)

        score = []
        for r in relation:
            index = 0
            # 编辑距离
            score1 = sim.levenshtein(sentence, r)
            # 余弦相似度
            score2 = sim.compute_cosine(sentence, r)
            score.append(score1)
        print(score)

        # 关系和评分对应相连
        result = dict(zip(relation, score))
        # print(result)

        # 将关系按照分值高低排序
        res = (sorted(result.items(), key=lambda kv: kv[1], reverse=False))
        # print(res)


        for i in range(1):
            scorecur = res[i][1]
            print(scorecur)
            # rel = res[i][0]
            if scorecur > scoreall:
                scoreall = scorecur
                rel = res[i][0]
                string = "match(n:entity{name:'" + e + "'})-[r:`现象`]->(m:pxx{name:'" + rel+"'})-[r1:原因]->(res) return res.name"
                reason = []
                reason1 = tx.run(string)
                reason2 = []
                for r in reason1:
                    reason2.append(r)
                reason = Screen(reason2,'res.name')
            else:
                if scorecur == scoreall:
                    rel = res[i][0]
                    string = "match(n:entity{name:'" + e + "'})-[r:`现象`]->(m:pxx{name:'" + rel + "'})-[r1:原因]->(res) return res.name"
                    reason1 = tx.run(string)
                    reason2 = []
                    for r in reason1:
                        reason2.append(r)
                    reason.append(Screen(reason2))
    return reason

'''
if __name__ == '__main__':
    question = "系统死机了不工作了"
    res = entity_ner(question)
    print(res)
'''

