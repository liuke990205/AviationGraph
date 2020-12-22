from django.shortcuts import render
import pymysql
import pandas as pd
import os
# Create your views here.

# Create your views here.
from django.http import HttpResponse

from django.shortcuts import HttpResponse #导入HttpResponse模块
from Hello.answer.kbqa import kbqans
from Hello.answer.bm25data import similarity
from Hello.models import Fault


def simqa(question):
    arr = []
    list = similarity.initbm(question)
    l = list[0].strip()

    sql = 'select * from fault where phenomenon= %s'
    result = Fault.objects.raw(sql, [l])
    for i in result:
        arr.append(i.reason)
    arr = set(arr)
    return list,arr


def toAnswer(request):
    return render(request, "answer.html")


def answer_question(request):
    arr = []
    qlist = []
    if request.POST:
        question = request.POST.get('question', None)
        if question:
            #dp = kbqans.entity_ner(question)
            #print(dp)
            qlist,bm25 = simqa(question)
            '''
                        if dp!="":
                arr.append(dp)
            else:
                arr = bm25
            '''
            arr = bm25
    return render(request, 'answer.html', {'answer':arr,'qlist': qlist})