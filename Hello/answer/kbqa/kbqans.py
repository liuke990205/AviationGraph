# -*- coding: utf-8 -*-
from Hello.answer.kbqa import entity
from Hello.answer.kbqa import sim
from Hello.toolkit.pre_load import neo4jconn

from py2neo import Graph, Node, Relationship

# 连接neo4j数据库，输入地址、用户名、密码
graph = Graph("http://123.56.52.53:7474", username="neo4j", password='root')
tx = graph.begin()

def entity_ner(question):
    # 候选实体
    entity_list = entity.entity_seq(question)
    # 候选关系
    # 编辑距离 score1 = levenshtein(sentence, s)
    # 余弦相似度 score2 = compute_cosine(sentence, s)

    '''
    将neo4j数据格式化成三元组
    '''
    def Screen(searchResult, num):
        tableData = []
        for i in range(0, len(searchResult)):
            tableData.append(searchResult[i][num])
        return tableData
    '''
    第二跳数据查询
    '''
    def second_serarch(rel):
        db = neo4jconn
        # string = "match(x:现象{name:'" + rel + "'})-[jx:`原因`]->(y) return y.name"
        # reason1 = tx.run(string)
        reason1 = db.findWeiEntity(rel)

        for r in reason1:
            reason2.append(r)
        result2 = Screen(reason2, 'y.name')
        return result2
    # 1.对每一个候选实体，首先找出和他相连的第一跳所有邻居，即，部件（实体）———现象————故障现象，也就是所有的故障现象
    # 2.找到故障现象相似度评分最高的，保留分数和故障现象，通过二跳，查询到故障原因
    # 3.执行1，2，和当前score对比，如果分数高，则保留分高的，若分数相等，也保留

    reason2 = []
    # 寻找最小值，全局分数要赋一个极大数
    scoreall = 10000

    #存储第一跳的结果
    result1 = []
    #存储第二跳的结果
    result2 = []

    '''
    存储最终的结果   
    例如：[['系统', '现象', '电脑蓝屏'],['电脑蓝屏', '原因',  '重启电脑']]
    '''
    end_result = []

    # 对于每一个候选实体
    for e in entity_list:
        # 查询所有一跳邻居，放在relation中
        # string = "match(x:" + e + "{name:'" + e + "'})-[jx:`现象`]->(y) return y.name"
        # relation1 = tx.run(string)

        db = neo4jconn
        relation1 = db.findWeiEntity2(e)
        print(relation1)

        #存储第一跳查询到的结果
        res1 = []
        for r in relation1:
            res1.append(r)
        relation = Screen(res1, 'y.name')
        print(relation)
        if len(relation) == 0:
            break
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

        '''
        将关系按照分值高低排序
        '''
        res = sorted(result.items(), key=lambda kv: kv[1], reverse=False)
        print(res)

        '''
        重新遍历列表，有可能出现最小值出现多个的情况
        '''
        for i in range(len(res)):
            scorecur = res[i][1]
            if scorecur <= scoreall:
                scoreall = scorecur
                rel = res[i][0]
                result2 = second_serarch(rel)
        '''
        根据第二跳的结果，筛选第一跳的数据，用result1列表来存储
        '''
        for i in range(len(result2)):
            result1.append(res[i][0])
    '''
    整合到最终列表中
    '''
    for j in range(len(result1)):
        temp1 = []
        temp1.append(e)
        temp1.append('现象')
        temp1.append(result1[j])
        temp2 = []
        temp2.append(result1[j])
        temp2.append('原因')
        temp2.append(result2[j])
        end_result.append(temp2)
        end_result.append(temp1)
    print(end_result, ":end_result")
    return end_result, result2