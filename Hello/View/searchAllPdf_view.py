# -*- coding: utf-8 -*-

from django.contrib import messages
from django.shortcuts import render, redirect
import pdfplumber
from Hello.Entity.WORD.word import Word
import jieba
import pandas as pd

'''
跳转到全文搜索界面
'''
def toSearchAllPdf(request):
    username = request.session.get('username')
    if username is None:
        return render(request, 'login.html')

    return render(request, "searchAllPdf.html")



def PDFreader(filename):
    # 读取PDF文档并分词
    name = Word()
    name.setWord(filename)
    wordlist = list()
    wordlist.append(name)
    #jieba.load_userdict(r"C:/Users/刘珂/Desktop/pyproject/untitled/dic/hkbk.dic")
    pdfReader = pdfplumber.open(filename)
    for i in range(pdfReader.pages.__len__()):
        page_text = pdfReader.pages[i]
        page_content = page_text.extract_text()
        seg_list = jieba.lcut_for_search(page_content, HMM=False)
        for j in range(seg_list.__len__()):
            tem_word = Word()
            tem_word.setWord(seg_list[j])
            tem_word.setPageNo(i+1)
            wordlist.append(tem_word)
    return wordlist


def PDFsearch(key, words):
    # 搜索关键词
    Tem_PageNo = list()
    for i in range(words.__len__()):
        if(key == words[i].getWord()):
            Tem_PageNo.append(words[i].getPageNo())
    PageNo = list()
    for i in range(Tem_PageNo.__len__()):
        if Tem_PageNo[i] not in PageNo:
            PageNo.append(Tem_PageNo[i])
    return PageNo

def searchAllPdf(request):
    # filename = "D:/desk/开题相关论文\开题报告.pdf"

    '''
    dlg = win32ui.CreateFileDialog(1)  # 1表示打开文件对话框
    dlg.SetOFNInitialDir('D:')  # 设置打开文件对话框中的初始显示目录
    dlg.DoModal()
    filename = dlg.GetPathName()  # 获取选择的文件名称
    '''


    key = request.POST.get("keywords")

    filename = "upload_file/pdf_test.pdf"
    words = PDFreader(filename)

    for i in range(len(words)):
        print(words[i].getWord())

    pages = PDFsearch(key, words)


    if pages.__len__() == 0:
        print(pages)
        messages.success(request, "抱歉！在文件中没有找到该关键字！")
        return redirect("/toSearchAllPdf")
    else:

        page_content = []

        for i in range(pages.__len__()):
            print(key + "在" + filename + "中出现的页码为" + str(pages[i]))
            pdfReader = pdfplumber.open(filename)
            page_text = pdfReader.pages[i]

            page_content.append(page_text.extract_text())

        content_dict = dict(zip(pages, page_content))
        print(content_dict)
        return render(request, 'searchAllPdf.html',{'content_dict': content_dict})



