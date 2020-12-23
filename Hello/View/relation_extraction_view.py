import csv
import os
import re
import random
import docx
import jieba
from django.contrib import messages
from django.shortcuts import render, redirect

from Hello.models import Relation, Temp, User, Annotation
# from Hello.toolkit.deepke import predict1

# 跳转到关系抽取页面
def toRelation(request):
    username = request.session.get('username')
    if username is None:
        return render(request, 'login.html')
    return render(request, 'relation_extract.html')


def upload3(request):
    if request.method == 'POST':
        # 获取文件名
        path = request.FILES.get('file')
        if path:
            with open('upload_file/relation_extraction_word.docx', 'wb+') as destination:
                for chunk in path.chunks():
                    destination.write(chunk)

            new_data = []
            # 读取文件内容，并且插入到数据库中

            # with open(file.name, "r") as lines:
            #    dataList = lines.readlines()
            #   print(dataList)
            # for data in dataList:
            file = docx.Document("upload_file/relation_extraction_word.docx")
            for p in file.paragraphs:
                data = p.text.strip('\n')
                new_data.append(data)
            messages.success(request, "上传成功！")

            request.session['new_data'] = new_data
            a = []
            for data in new_data:
                a.append(data)
            str = ""

            str = ''.join(a)
            return render(request, 'relation_extract.html', {'str': str})
        else:
            messages.success(request, "文件为空！")
            return redirect('/toRelation/')


# 读取待识别文本并转化成所要形式
def re_text(request):
    if request.POST:
        text = request.POST['user_text']
        print(text)
        # 获取输入文本
        sen_list = []

        relation_list = []

        result = re.split(r'[。\n]', text)
        if "\n" in result:
            result.remove("\n")
        for i in range(len(result)):
            sen = str((result[i]).replace('\n', '').replace('\r', '') + "。\n")
            sen_list.append(sen)

        dic_dir = "Hello/toolkit/dic.txt"
        temp_file_dir = "Hello/toolkit/rel_data.csv"

        jieba.load_userdict(dic_dir)

        f = open(temp_file_dir, 'w')
        f.truncate()


        f1 = open(dic_dir, 'r', encoding='utf-8')
        f2 = open(temp_file_dir, 'a')

        dic_entity = []
        dic_entity_type_ori = []
        dic_entity_type = []
        sen_entity = []
        entity_type = []

        for w in f1.readlines():  # 读取词典中的实体
            w_array = w.split(" ")
            dic_entity.append(w_array[0])
            dic_entity_type_ori.append(w_array[2].replace("\n", ""))
        print(dic_entity)

        for type in dic_entity_type_ori:
            if type == "hkq":
                dic_entity_type.append("航空器")
                continue
            if type == "wq":
                dic_entity_type.append("武器")
                continue
            if type == "sxmx":
                dic_entity_type.append("数学模型")
                continue
            if type == "ckwd":
                dic_entity_type.append("参考文档")
                continue
            if type == "xt":
                dic_entity_type.append("系统")
                continue
            if type == "xnzb":
                dic_entity_type.append("性能指标")
                continue
            if type == "csz":
                dic_entity_type.append("参数值")
                continue

        for i in range(len(sen_list)):

            seg1 = jieba.cut(sen_list[i])
            seg2 = "/".join(seg1)
            seg_list = seg2.split("/")  # 分词

            for j in range(len(seg_list)):
                for k in range(len(dic_entity)):
                    if seg_list[j] == dic_entity[k]:
                        # print(seg_list[j])
                        sen_entity.append(dic_entity[k])
                        entity_type.append(dic_entity_type[k].replace("\n", ""))  # 去除迷之换行

            if len(sen_entity) == 2 and sen_entity[0] != sen_entity[1]:
                flag = relation_schema(entity_type[0], entity_type[1])  # 利用schema提供约束
                if (flag == 1):
                    sentence = sen_list[i].replace("\n", "")
                    s = str(sentence) + "," + str(sen_entity[0]) + "," + str(entity_type[0]) + "," + str(
                        sen_entity[1]) + "," + str(entity_type[1]) + "\n"  #
                    f2.write(s)
                    relation_list.append([str(sentence), str(sen_entity[0]), str(entity_type[0]), str(sen_entity[1]),
                                          str(entity_type[1])])

                if (flag == 2):
                    sentence = sen_list[i].replace("\n", "")
                    entity_type[0], entity_type[1] = entity_type[1], entity_type[0]
                    relation_list.append([str(sentence), str(sen_entity[0]), str(entity_type[1]), str(sen_entity[1]),
                                          str(entity_type[0])])
                    s = str(sentence) + "," + str(sen_entity[0]) + "," + str(entity_type[1]) + "," + str(
                        sen_entity[1]) + "," + str(entity_type[0]) + "\n"  #
                    f2.write(s)

            if len(sen_entity) > 2:
                for j in range(len(sen_entity)):
                    for k in range(len(sen_entity) - j - 1):  # 每个实体及其后的单词两两配对
                        if sen_entity[j] != sen_entity[j + k + 1]:
                            flag = relation_schema(entity_type[j], entity_type[k + j + 1])  # 利用schema提供约束
                            # print(flag)
                            if (flag == 1):
                                sentence = sen_list[i].replace("\n", "")
                                relation_list.append(
                                    [str(sentence), str(sen_entity[j]), str(entity_type[j]), str(sen_entity[j + k + 1]),
                                     str(entity_type[j + k + 1])])
                                s = str(sentence) + "," + str(sen_entity[j]) + "," + str(entity_type[j]) + "," + str(
                                    sen_entity[j + k + 1]) + "," + str(entity_type[j + k + 1]) + "\n"  #
                                f2.write(s)
                            if (flag == 2):
                                sentence = sen_list[i].replace("\n", "")
                                relation_list.append(
                                    [str(sentence), str(sen_entity[j + k + 1]), str(entity_type[k + j + 1]),
                                     str(sen_entity[j]),
                                     str(entity_type[j])])
                                s = str(sentence) + "," + str(sen_entity[j + k + 1]) + "," + str(
                                    entity_type[k + j + 1]) + "," + str(
                                    sen_entity[j]) + "," + str(entity_type[j]) + "\n"  # 调换一下
                                f2.write(s)
            sen_entity = []
            entity_type = []
        f2.close()
        os.system("python Hello/toolkit/deepke/predict1.py")
        #predict1.main()
        textfile = open(temp_file_dir, 'r')
        # 获取当前用户的ID
        username = request.session.get('username')
        user = User.objects.get(username=username)
        user_id = user.user_id

        reader = csv.reader(textfile)

        #将session域初始化
        request.session['resultList'] = []

        resultList = []
        for rel in reader:
            temp_list = []
            if len(rel) == 6:
                text = rel[0]
                headEntity = rel[1]
                headEntityType = rel[2]
                tailEntity = rel[3]
                tailEntityType = rel[4]
                relationshipCategory = rel[5]
                '''
                将文本添加到Annotation中
                '''
                ann = Annotation(content=text, flag=1, file_name="", user_id_id=user_id)
                ann.save()

                random_num = random.randint(10000, 90000)
                temp_list = [ann.annotation_id, headEntity, headEntityType, tailEntity, tailEntityType,
                             relationshipCategory, user_id, "", random_num]

                resultList.append(temp_list)
    print(resultList)
    request.session['resultList'] = resultList
    return render(request, 'relation_extract.html', {'resultList': resultList})


def relation_schema(type1, type2):
    schema_type1 = Relation.objects.values_list("head_entity", flat=True)
    schema_type2 = Relation.objects.values_list("tail_entity", flat=True)

    for i in range(len(schema_type1)):
        if type1 == schema_type1[i] and type2 == schema_type2[i]:
            return 1

    for i in range(len(schema_type1)):
        if type2 == schema_type1[i] and type1 == schema_type2[i]:
            return 2
    return 0


# 删除选中的Rel
def deleteRel(request):
    # 获取前端传过来的rel_id
    id = request.GET.get('rel_id')
    print(id)

    resultList = request.session.get('resultList')
    for data in resultList:
        if data[8] == int(id): ##注意强制类型转换
            #删除列表元素
            resultList.remove(data)
    #更新session域的内容
    request.session['resultList'] = resultList
    return render(request, 'relation_extract.html', {'resultList': resultList})

# 修改Rel信息
def modifyRel(request):
    rel_id = request.POST.get('rel_id')
    new_headEntity = request.POST.get('headEntity')
    new_headEntityType = request.POST.get('headEntityType')
    new_tailEntity = request.POST.get('tailEntity')
    new_tailEntityType = request.POST.get('tailEntityType')
    new_relationshipCategory = request.POST.get('relationshipCategory')

    resultList = request.session.get('resultList')
    for data in resultList:
        if data[8] == int(rel_id):
            data[1] = new_headEntity
            data[2] = new_headEntityType
            data[3] = new_tailEntity
            data[4] = new_tailEntityType
            data[5] = new_relationshipCategory
    # 更新session域的内容
    request.session['resultList'] = resultList

    return render(request, 'relation_extract.html', {'resultList': resultList})

def saveRel(request):
    resultList = request.session.get('resultList')

    for list in resultList:
        rel = Temp(headEntity=list[1], headEntityType=list[2], tailEntity=list[3],
                   tailEntityType=list[4], relationshipCategory=list[5],
                   user_id=int(list[6]), filename="", annotation_id_id=list[0])
        rel.save()
    return render(request, 'relation_extract.html')
