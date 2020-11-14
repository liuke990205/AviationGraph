# -*- coding: utf-8 -*-

from django.contrib import messages
from django.shortcuts import render, redirect
import docx
import csv
import json
'''
跳转到基于规则的word知识提取
'''
def toWord(request):
    username = request.session.get('username')
    if username is None:
        return render(request, 'login.html')
    return render(request, "word.html")

'''
关系：【组成关系】
对表格进行解析
'''
def table(line: str) -> list:
    result_list = []
    data = line.split()
    for i in range(len(data) - 1):
        temp_list = [data[i], "组成关系", data[i + 1], line.replace("\n", "")]
        result_list.append(temp_list)
    return result_list

'''
关系：【组成关系】
由...组成、由...构成
sring = 组成 | 构成
'''
def made_of_1(string: str,line: str) -> list:
    start0 = line.find("，")
    start1 = line.find("由")
    start2 = line.find(string)
    result_list = []
    if start1 != -1 and start2 != -1 and start2 > start1:
        list1 = line[start1 + 1:start2]
        for data in list1.split("、"):
            temp_list = [line[start0 + 1:start1], "组成关系", data, line.replace("\n", "")]
            result_list.append(temp_list)
    return result_list

'''
关系：【组成关系】
string = 主要包括|分为
'''
def made_of_2(string: str, line: str) -> list:
    start1 = line.find(string)
    end1 = line.find("。")
    list1 = line[start1 + len(string):end1]
    print(line[start1 + len(string):end1], 222)
    result_list = []
    if list1.find("、") != -1:
        for data in list1.split("、"):
            if data[-1] == "等":
                temp_list = [line[0:start1], "组成关系", data[0:-1], line.replace("\n", "")]
                result_list.append(temp_list)
            else:
                temp_list = [line[0:start1], "组成关系", data, line.replace("\n", "")]
                result_list.append(temp_list)

    start = line.find(string)
    end = line.find("等")
    headEntity = line[0:start]
    print(headEntity) #客车

    list = line[start + len(string) + 1:end]
    print(list)#a） 小型客车（1辆）；b） 中型客车（1辆）；c） 大型客车（3辆），分为铰接式客车，双层客车和多层客车

    for data in list.split("；"):
        index = data.find('）')
        if index != -1:
            data2 = data[index+1:] #大型客车（3辆），分为铰接式客车，双层客车和多层客车
            print(data2, 222)
            for i in range(1, 1000):
                if data2.find(chr(i)) != -1:
                    beg_index = data2.find('（')
                    end_index = data2.find('）')
                    tailEntity = data2[0:beg_index] #大型客车
                    in_entity = data2[beg_index + 1:end_index]
                    temp_list =[tailEntity, "数量关系", in_entity]
                    result_list.append(temp_list)

                    temp_list1 = [headEntity, "组成关系", tailEntity]  #, line.replace("\n", "")
                    result_list.append(temp_list1)
                    break
    return result_list

'''
关系：【位置关系】
string  = 位于......
'''
def local(string :str, line: str) -> list:
    #获取关键字位置
    start = line.find(string)
    #获取结束位置
    end = line.find("。")
    temp_list = [line[0:start], "位置关系", line[start + len(string):end], line.replace("\n", "")] #注意删除换行符
    #print(temp_list)
    return temp_list

'''
关系：【使用关系】
string = 采用|使用
'''
def use(string: str, line: str) -> list:
    # 获取关键字位置
    start = line.find(string)
    # 获取结束位置
    end = line.find("，")
    temp_list = []
    if start != -1:
        if end == -1:
            end = line.find("。")
        temp_list = [line[0:start], "使用关系", line[start + len(string):end], line.replace("\n", "")]
    return temp_list


def main(infile) -> list:
    infopen = open(infile, 'r', encoding="utf-8")
    #加载json格式的配置文件 => 字典
    with open("configurateFile/rules.json", 'r', encoding='UTF-8') as f:
        load_dict = json.load(f)

    #后期读取配置文件或者前端列表
    ###relation = ["位于", "使用", "采用", "主要包括", "分为", "\t", "组成", "构成"]
    relation = ["\t"]
    for k, v in load_dict.items():
        for listData in v:
            relation.append(listData)
    result_list = []

    #读取格式化之后的文件
    lines1 = infopen.readlines()
    for line in lines1:
        print(line)
        for r in relation:
            if line.find(r) != -1:
                if r == "\t":
                    # print(table(line))
                    temp_list = table(line)
                    for data in temp_list:
                        result_list.append(data)

                for k, v in load_dict.items():
                    for listData in v:
                        if r == listData:
                            if k == "使用关系":
                                temp_list = use(r, line)
                                #for data in temp_list:
                                result_list.append(temp_list)
                                #print(use(r, line))
                            if k == "位置关系":
                                #print(local(r, line))
                                temp_list = local(r, line)
                                #for data in temp_list:
                                result_list.append(temp_list)
                            if k == "组成关系1":
                                #print(made_of_2(r, line))
                                temp_list = made_of_2(r, line)
                                for data in temp_list:
                                    result_list.append(data)
                            if k == "组成关系2":
                                if line.find("由") != -1:
                                    # print(made_of_1(r, line))
                                    temp_list = made_of_1(r, line)
                                    for data in temp_list:
                                        result_list.append(data)
    resultList = []
    for data in result_list:
        temp = ["", "", "", "", ""]
        temp[0] = data[0]
        temp[2] = data[1]
        temp[3] = data[2]
        if data[0].find("飞机") != -1:
            temp[1] = "飞机"
        if data[0].find("系统") != -1:
            temp[1] = "系统"
        if data[0].find("框") != -1:
            temp[1] = "框"

        if data[2].find("飞机") != -1:
            temp[4] = "飞机"
        if data[2].find("系统") != -1:
            temp[4] = "系统"
        if data[2].find("框") != -1:
            temp[4] = "框"

        if data[1] == "使用关系":
            temp[1] = "部附件"
            temp[4] = "结构"
        if data[1] == "组成关系" and data[0].find("系统") != -1 and data[2].find("系统") == -1:
            temp[4] = "部附件"
        if data[1] == "组成关系" and data[0].find("飞机") != -1 and data[2].find("系统") == -1:
            temp[4] = "结构"
        if data[1] == "数量关系":
            temp[1] = "部附件"
            temp[4] = "数量"

        if data[1] == "位置关系":
            temp[1] = "结构"
            if temp[4] != "框":
                temp[4] = "位置"
        resultList.append(temp)

    infopen.close()



    return resultList


'''
格式化待处理文件
1.去掉空行
2.去掉数字开头的行
3.将列表形式处理成一行（未完成）
'''
def format_file(infile) -> list:
    outfile = "upload_file/temp.txt"

    infopen = open(infile, 'r', encoding="utf-8")
    outfopen = open(outfile, 'w+', encoding="utf-8")

    lines = infopen.readlines()

    t_list = []
    for j in range(len(lines)):
        if lines[j].split():
            if lines[j].find("主要包括") != -1:
                for i in range(ord("a"), ord("z") + 1):
                    if lines[j+1].startswith(chr(i)) == True:
                        t_list.append(lines[j].replace("\n", ""))
                        t_list.append(lines[j+1].replace("\n", ""))
                        for k in range(j+2, len(lines)):
                            for i in range(ord("a"), ord("z") + 1):
                                if lines[k].startswith(chr(i)) == True:
                                    t_list.append(lines[k].replace("\n", ""))
            list_str = ''.join(t_list)
            if list_str:
                #print(list_str)
                outfopen.writelines(list_str+"\n")
            t_list = []
            for i in range(9):
                if lines[j].startswith(str(i)) == True:
                    break
            if i == 8:
                outfopen.writelines(lines[j])
        else:
            outfopen.writelines("")
    infopen.close()
    outfopen.close()
    #调用主处理函数
    resultList = main(outfile)
    return resultList

def upload_word(request):

    # 上传文件，并且将数据保存到数据库中
    if request.method == 'POST':
        # 获取文件名
        path = request.FILES.get('file')
        if path:
            with open('upload_file/technical_file_word.docx', 'wb+') as destination:
                for chunk in path.chunks():
                    destination.write(chunk)

            file = docx.Document("upload_file/technical_file_word.docx")

            infile = "upload_file/temp1.txt"
            with open(infile, 'w+', encoding="utf-8") as outfopen:
                for p in file.paragraphs:
                    data = p.text.strip('\n')
                    print(data)
                    outfopen.writelines(data+"\n")
            resultList = format_file(infile)
            messages.success(request, "上传成功！")

            request.session['word_list'] = resultList

            return redirect('/display_word_result/')

            #return render(request, 'word.html', {'resultList': resultList})
        else:
            messages.success(request, "文件为空！")
            return redirect('/toWord/')

def display_word_result(request):
    resultList = request.session.get('word_list')
    print(resultList)
    return render(request, 'word.html', {'resultList': resultList})