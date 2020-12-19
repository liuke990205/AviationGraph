# -*- coding: utf-8 -*-
from django.contrib import messages
from django.shortcuts import render, redirect
import pdfplumber
from Hello.Entity.WORD.word import Word
import jieba
from PyPDF2 import PdfFileReader

'''
跳转到全文搜索界面
'''
def toSearchAllPdf(request):
    username = request.session.get('username')
    if username is None:
        return render(request, 'login.html')
    return render(request, "searchAllPdf.html")

def upload_pdf(request):
    if request.method == 'POST':
        # 获取文件名
        path = request.FILES.get('file')
        if path:
            with open('upload_file/pdf_test.pdf', 'wb+') as destination:
                for chunk in path.chunks():
                    destination.write(chunk)
            messages.success(request, "上传成功！")
            return redirect('/toSearchAllPdf/')
        else:
            messages.success(request, "文件为空！")
            return redirect('/toSearchAllPdf/')


def PDFreader(filename):
    # 读取PDF文档并分词
    name = Word()
    name.setWord(filename)
    wordlist = list()
    wordlist.append(name)
    jieba.load_userdict("upload_file/hkbk.dic")
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


def PDFreader_title(pdf):
    pg_id_to_num = {}
    wordlist = list()
    jieba.load_userdict("upload_file/hkbk.dic")
    for pg_num in range(0, pdf.getNumPages()):
        pg_id_to_num[pdf.getPage(pg_num).indirectRef.idnum] = pg_num

    def title_split(bookmarks, lvl=0):
        for b in bookmarks:
            if type(b) == list:
                title_split(b, lvl + 4)
                continue
            pg_num = pg_id_to_num[b.page.idnum] + 1
            seg_list = jieba.lcut_for_search(b.title, HMM=False)
            for j in range(len(seg_list)):
                tem_word = Word()
                tem_word.setWord(seg_list[j])
                tem_word.setPageNo(pg_num)
                wordlist.append(tem_word)
    title_split(pdf.getOutlines())
    return wordlist


def PDFsearch_title(key, filename):
    with open(filename, "rb") as f:
        pdf = PdfFileReader(f)
        words = PDFreader_title(pdf)
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
    key = request.POST.get("keywords")
    filename = "upload_file/Python.pdf"
    print(filename)
    words = PDFreader(filename)

    for i in range(len(words)):
        print(words[i].getWord())

    pages = PDFsearch_title(key, filename)
    pages_content = PDFsearch(key, words)

    for i in range(pages_content.__len__()):
        if pages_content[i] not in pages:
            pages.append(pages_content[i])
    print(pages)
    if pages.__len__() == 0:
        print(pages)
        messages.success(request, "抱歉！在文件中没有找到该关键字！")
        return redirect("/toSearchAllPdf")
    else:
        page_content = []
        for i in range(pages.__len__()):
            print(key + "在" + filename + "中出现的页码为" + str(pages[i]))
            pdfReader = pdfplumber.open(filename)
            page_text = pdfReader.pages[ pages[i] - 1]
            page_content.append(page_text.extract_text())

        content_dict = dict(zip(pages, page_content))
        return render(request, 'searchAllPdf.html',{'content_dict': content_dict})