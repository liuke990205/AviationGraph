from Hello.answer.kbqa import entity
import math
import re
import datetime
import time


# 句子去掉实体后剩余的部分
def left(sentence):
    entity_res = entity.entity_seq(sentence)
    print(entity_res)
    similar_left = []
    for e in entity_res:
        sen = sentence.split(e)
        # 实体在中间，取后面部分
        if len(sen) > 1:
            similar_left.append(sen[1])
        else:
            similar_left.append(sen)
    return similar_left


# 编辑距离
def levenshtein(first, second):
    ''' 编辑距离算法（LevD）
        Args: 两个字符串
        returns: 两个字符串的编辑距离 int
    '''
    if len(first) > len(second):
        first, second = second, first
    if len(first) == 0:
        return len(second)
    if len(second) == 0:
        return len(first)
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = [list(range(second_length)) for x in range(first_length)]
    # print distance_matrix
    for i in range(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i - 1][j] + 1
            insertion = distance_matrix[i][j - 1] + 1
            substitution = distance_matrix[i - 1][j - 1]
            if first[i - 1] != second[j - 1]:
                substitution += 1
            distance_matrix[i][j] = min(insertion, deletion, substitution)
            # print distance_matrix
    return distance_matrix[first_length - 1][second_length - 1]


def compute_cosine(text_a, text_b):
    # 找单词及词频
    words1 = text_a.split(' ')
    words2 = text_b.split(' ')
    # print(words1)
    words1_dict = {}
    words2_dict = {}
    for word in words1:
        # word = word.strip(",.?!;")
        word = re.sub('[^a-zA-Z]', '', word)
        word = word.lower()
        # print(word)
        if word != '' and word in words1_dict:  # 这里改动了
            num = words1_dict[word]
            words1_dict[word] = num + 1
        elif word != '':
            words1_dict[word] = 1
        else:
            continue
    for word in words2:
        # word = word.strip(",.?!;")
        word = re.sub('[^a-zA-Z]', '', word)
        word = word.lower()
        if word != '' and word in words2_dict:
            num = words2_dict[word]
            words2_dict[word] = num + 1
        elif word != '':
            words2_dict[word] = 1
        else:
            continue
    print(words1_dict)
    print(words2_dict)

    # 排序
    dic1 = sorted(words1_dict.items(), key=lambda asd: asd[1], reverse=True)
    dic2 = sorted(words2_dict.items(), key=lambda asd: asd[1], reverse=True)
    print(dic1)
    print(dic2)

    # 得到词向量
    words_key = []
    for i in range(len(dic1)):
        words_key.append(dic1[i][0])  # 向数组中添加元素
    for i in range(len(dic2)):
        if dic2[i][0] in words_key:
            # print 'has_key', dic2[i][0]
            pass
        else:  # 合并
            words_key.append(dic2[i][0])
    # print(words_key)
    vect1 = []
    vect2 = []
    for word in words_key:
        if word in words1_dict:
            vect1.append(words1_dict[word])
        else:
            vect1.append(0)
        if word in words2_dict:
            vect2.append(words2_dict[word])
        else:
            vect2.append(0)
    # print(vect1)

    # print(vect2)

    # 计算余弦相似度
    sum = 0
    sq1 = 0
    sq2 = 0
    for i in range(len(vect1)):
        sum += vect1[i] * vect2[i]
        sq1 += pow(vect1[i], 2)
        sq2 += pow(vect2[i], 2)
    try:
        result = round(float(sum) / (math.sqrt(sq1) * math.sqrt(sq2)), 2)
    except ZeroDivisionError:
        result = 0.0
    return result

'''
# 相似度评分
def sim(sentence, leftlist):
    # score_matrix = [[] for i in range(len(leftlist)+1)]
    score = []
    for s in leftlist:
        index = 0
        score1 = levenshtein(sentence, s)
        score2 = compute_cosine(sentence, s)
        score.append(score2)
    # print(score)
    result = dict(zip(leftlist, score))
    # print(result)
    res = (sorted(result.items(), key=lambda kv: kv[1], reverse=True))
    print(res)
    list = []
    for i in range(2):
        list.append(res[i][0])
    return list


if __name__ == '__main__':
    question = "研究生命起源意义是什么"
    lkeftlist = left(question)
    print(lkeftlist)
    res = sim(question, lkeftlist)
    print(res)
'''
