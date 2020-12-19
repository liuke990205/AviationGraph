# -*- coding: utf-8 -*-
import random

import pymysql
from django.contrib import messages
from django.shortcuts import render, redirect
import xlrd
from Hello.toolkit.pre_load import neo4jconn
from Hello.models import Dictionary

# 跳转到excel界面
def toExcel(request):
    username = request.session.get('username')
    if username is None:
        return render(request, 'login.html')
    return render(request, 'excel.html')

def upload_excel(request):
    if request.method == 'POST':
        # 获取文件名
        file = request.FILES.get('file')
        if file:
            # 下面代码作用：获取到excel中的字段和数据
            excel = xlrd.open_workbook(file.name)
            sheet = excel.sheet_by_index(0)
            row_number = sheet.nrows
            column_number = sheet.ncols
            field_list = sheet.row_values(0)
            data_list = []
            for i in range(1, row_number):
                data_list.append(sheet.row_values(i))
            # 下面代码作用：根据字段创建表，根据数据执行插入语句
            conn = pymysql.connect(host='123.56.52.53', port=3306, user='root', password='root',
                                   database='source')
            cursor = conn.cursor()
            drop_sql = "drop table if exists {}".format('name')
            cursor.execute(drop_sql)
            create_sql = "create table {}(".format('name')
            for field in field_list[:-1]:
                create_sql += "{} varchar(50),".format(field)
            create_sql += "{} varchar(50))".format(field_list[-1])
            cursor.execute(create_sql)
            for data in data_list:
                new_data = ["'{}'".format(i) for i in data]
                insert_sql = "insert into {} values({})".format('name', ','.join(new_data))
                cursor.execute(insert_sql)

            sql = "select COLUMN_NAME from information_schema.COLUMNS where table_name = '%s'" % ('name')
            count = cursor.execute(sql)
            name_list = list()
            for i in range(count):
                rr = cursor.fetchone()[0]
                if rr not in name_list:
                    name_list.append(rr)
            conn.commit()

            request.session['name_list'] = name_list

            '''
            将上传的表中的字段名和  数据库中的规则进行匹配   tableData存储匹配之后的list
            '''
            conn = pymysql.connect(host='123.56.52.53', port=3306, user='root', password='root',
                                   database='source')
            cursor = conn.cursor()

            sql = "select * from excel_relation "
            cnt = cursor.execute(sql)
            tableData = [] #存储匹配之后得到的规则

            for i in range(cnt):
                result = cursor.fetchone()
                temp_list = []
                for a in result:
                    temp_list.append(a)
                #for data in temp_list:
                if flag(temp_list[0], name_list) and flag(temp_list[2], name_list):
                    tableData.append(temp_list)

            #将预加载的规则存到session
            request.session['tableData'] = tableData
            conn.close()
            return render(request, 'excel.html', {'name_list': name_list, 'tableData': tableData})
    return redirect('/toExcel/')

def flag(string, name_list) -> bool:
    for data in name_list:
        if string == data:
            return True
    return False

def commit_properties(request):
    if request.method == 'POST':
        '''
        后期在前端限定   实体名只能选择一个
        '''
        # 获取到前端选择的字段
        head_entity_list = request.POST.getlist('select2')
        head_property_list = request.POST.getlist('select3')
        tail_entity_list = request.POST.getlist('select22')
        tail_property_list = request.POST.getlist('select33')

        tableData = request.session.get('tableData')
        name_list = request.session.get('name_list')

        if len(head_entity_list) > 1 or len(tail_entity_list) > 1:
            messages.success(request, '选择的头实体个数或者尾实体个数大于1！')
            return render(request, 'excel.html', {'name_list': name_list, 'tableData': tableData})
        '''
        if len(head_entity_list) == 0 or len(head_property_list) == 0 or len(tail_entity_list) or len(tail_property_list) == 0:      
            messages.success(request, "亲，您现在啥也没选择呢！")
            return render(request, "excel.html", {'name_list': name_list, 'tableData': tableData})     
        '''

        head_property_list = ','.join(head_property_list)
        tail_property_list = ','.join(tail_property_list)
        id =random.randint(20, 200000)

        temp = [head_entity_list[0], head_property_list, tail_entity_list[0], tail_property_list, id]

        '''
        将新的规则插入到规则表中  将属性列表转换成  A,B,C 格式进行存储
        '''
        #连接数据库
        conn = pymysql.connect(host='123.56.52.53', port=3306, user='root', password='root',
                               database='source')
        cursor = conn.cursor()
        sql = "INSERT INTO excel_relation VALUES('%s','%s','%s','%s','%s')" % (head_entity_list[0], head_property_list, tail_entity_list[0], tail_property_list, id)
        cursor.execute(sql)
        conn.commit()

        tableData.append(temp)
        request.session['tableData'] = tableData

        return render(request, 'excel.html', {'name_list': name_list, 'tableData': tableData})

def excel_delete(request):
    id = request.GET.get('id')
    tableData = request.session.get('tableData')
    name_list = request.session.get('name_list')
    for data in tableData:
        if data[4] == int(id):
            tableData.remove(data)
    request.session['tableData'] = tableData

    return render(request, 'excel.html', {'name_list': name_list, 'tableData': tableData})



def excel_extract(request):
    if request.method == 'POST':

        #获取session域中的tableData
        tableData = request.session.get('tableData')

        #对每个规则进行抽取
        for data in tableData:

            # 获取到前端选择的字段
            head_entity = data[0]
            head_property_list = data[1]
            tail_entity = data[2]
            tail_property_list = data[3]

            #根据表的字段名进行抽取
            create_relation(head_entity, head_property_list, tail_entity, tail_property_list)

    #获取session域中的name_list
    name_list = request.session.get('name_list')

    #抽取完之后将session置为空
    request.session['tableData'] = []

    return render(request, 'excel.html', {'name_list': name_list})

def create_relation(head_entity, head_property_list, tail_entity, tail_property_list):

    conn = pymysql.connect(host='123.56.52.53', port=3306, user='root', password='root',
                           database='source')
    cursor = conn.cursor()

    # ['故障件','故障件编号']
    head_property_list_last = head_property_list.split(',')
    tail_property_list_last = tail_property_list.split(',')

    # 获取头实体属性列表的个数
    head_property_num = len(head_property_list_last)

    #头实体类型名
    head_entity_typename = head_entity
    #尾实体类型名 / 关系名
    tail_entity_typename = tail_entity

    # 根据查询条件编写的查询语句
    sql = "select %s, %s,%s,%s from name" % (head_entity_typename, tail_entity_typename, head_property_list, tail_property_list)
    count = cursor.execute(sql)

    # 连接neo4j数据库
    db = neo4jconn

    # 循环来遍历游标指针
    for i in range(count):
        result = cursor.fetchone()
        # 将查询结果转换成列表存储
        result = list(result)
        # 查询出来的头实体名的value
        head_entity_value = result[0]
        # 查询出来的尾实体名的value
        tail_entity_value = result[1]
        print(head_entity_value)
        print(tail_entity_value)
        # 查询出来的头实体的属性列表的value
        head_property_list_value = result[2:head_property_num + 2]
        # 查询出来的尾实体的属性列表的value
        tail_property_list_value = result[head_property_num + 2:]
        # 存储头实体属性结果集（字典存储）
        head_property_dict = {}
        # 存储尾实体属性结果集（字典存储）
        tail_property_dict = {}

        #生成头实体属性字典 例如：{“故障件”：显示器}
        for k in range(len(head_property_list_last)):
            head_property_dict.update({head_property_list_last[k]: head_property_list_value[k]})
        # 生成尾实体属性字典 例如：{“故障件”：显示器}
        for j in range(len(tail_property_list_last)):
            tail_property_dict.update({tail_property_list_last[j]: tail_property_list_value[j]})

        # 根据头实体名来查找neo4j数据库是否已经存在实体
        select_head_entity = db.findEntity(head_entity_value)
        # 根据尾实体名来查找neo4j数据库是否已经存在实体
        select_tail_entity = db.findEntity(tail_entity_value)

        '''
            创建节点和关系【判断之前判断一下节点是否已经存在】
        '''
        #两个实体都不存在
        print(len(select_head_entity))
        if len(select_head_entity) == 0 and len(select_tail_entity) == 0:
            db.createNode(head_entity_value, head_entity_typename, head_property_dict)
            db.createNode(tail_entity_value, tail_entity_typename, tail_property_dict)
            db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename, tail_entity_typename)

        #头实体已经存在，只需要创建尾实体和关系即可
        elif len(select_head_entity) != 0 and len(select_tail_entity) == 0:
            db.createNode(tail_entity_value, tail_entity_typename, tail_property_dict)
            db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename, tail_entity_typename)
        #尾实体已经存在，只需要创建头实体和关系即可
        elif len(select_head_entity) == 0 and len(select_tail_entity) != 0:
            db.createNode(head_entity_value, head_entity_typename, head_property_dict)
            db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename, tail_entity_typename)

    cursor.close()  # 关闭游标
    conn.close()  # 关闭连接