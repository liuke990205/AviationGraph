# -*- coding: utf-8 -*-
import docx
import jieba
from django.contrib import messages
from django.shortcuts import render, redirect
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


def jieba_tokenize(text):
    return jieba.lcut(text)


# 跳转到分类界面
def toClassification(request):
    username = request.session.get('username')
    if username is None:
        return render(request, 'login.html')
    return render(request, 'classification.html')


def upload_classification_file(request):
    if request.method == 'POST':
        # 获取文件名
        path = request.FILES.get('file')
        if path:
            with open('upload_file/classication_word.docx', 'wb+') as destination:
                for chunk in path.chunks():
                    destination.write(chunk)
            messages.success(request, "上传成功！")
            return render(request, 'classification.html')
        else:
            messages.success(request, "文件为空！")
            return redirect('/toClassification/')


def display_classification(request):
    # 读取文件内容
    file = docx.Document("upload_file/classication_word.docx")

    k_value = request.POST.get('k_value')
    if k_value is None:
        k_value = request.session.get('k_value')
    else:
        request.session['k_value'] = k_value

    text_list = []
    for p in file.paragraphs:
        i = p.text.strip('\n')
        text_list.append(i)
    '''
    tokenizer: 指定分词函数
    lowercase: 在分词之前将所有的文本转换成小写，因为涉及到中文文本处理，所以最好是False
    '''
    tfidf_vectorizer = TfidfVectorizer(tokenizer=jieba_tokenize, lowercase=False)

    # 需要进行聚类的文本集
    tfidf_matrix = tfidf_vectorizer.fit_transform(text_list)
    '''
    n_clusters: 指定K的值
    max_iter: 对于单次初始值计算的最大迭代次数
    n_init: 重新选择初始值的次数
    init: 制定初始值选择的算法
    n_jobs: 进程个数，为-1的时候是指默认跑满CPU
    注意，这个对于单个初始值的计算始终只会使用单进程计算，
    并行计算只是针对与不同初始值的计算。比如n_init=10，n_jobs=40, 
    服务器上面有20个CPU可以开40个进程，最终只会开10个进程
    '''
    num_clusters = int(k_value)
    km_cluster = KMeans(n_clusters=num_clusters, max_iter=300, n_init=1, init='k-means++', n_jobs=1)

    # 返回各自文本的所被分配到的类索引
    result_list = km_cluster.fit_predict(tfidf_matrix)
    # 将原文本和分类结果封装到字典里面
    result_dict = dict(zip(text_list, result_list))

    resultList_classification = []
    # 按照字典的值进行排序
    for k in sorted(result_dict, key=result_dict.__getitem__):
        temp = []
        temp.append(k)
        temp.append(result_dict[k])
        resultList_classification.append(temp)
    return render(request, 'classification.html', {'resultList_classification': resultList_classification})
