# -*- coding: utf-8 -*-
import random

import pymysql
import xlrd
from django.contrib import messages
from django.shortcuts import render, redirect
from Hello.toolkit.pre_load import neo4jconn


# 跳转到excel界面
def toExcel(request):
    username = request.session.get('username')
    if username is None:
        return render(request, 'login.html')
    return render(request, 'excel.html')


def upload_excel(request):
    if request.method == 'POST':
        # 获取文件名
        file = request.FILES.get('excel_file')
        if file:
            with open('upload_file/excel_import.xlsx', 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # 下面代码作用：获取到excel中的字段和数据
            excel = xlrd.open_workbook("upload_file/excel_import.xlsx")
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
            drop_sql = "drop table if exists {}".format('excel_data')
            cursor.execute(drop_sql)
            conn.commit()
            create_sql = "create table {}(".format('excel_data')
            for field in field_list[:-1]:
                create_sql += "{} varchar(50),".format(field)
            create_sql += "{} varchar(50))".format(field_list[-1])
            cursor.execute(create_sql)
            conn.commit()
            for data in data_list:
                new_data = ["'{}'".format(i) for i in data]
                insert_sql = "insert into {} values({})".format('excel_data', ','.join(new_data))
                cursor.execute(insert_sql)

            sql = "select COLUMN_NAME from information_schema.COLUMNS where table_name = '%s'" % ('excel_data')
            count = cursor.execute(sql)
            conn.commit()
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
            tableData = []  # 存储匹配之后得到的规则

            for i in range(cnt):
                result = cursor.fetchone()
                temp_list = []
                for a in result:
                    temp_list.append(a)
                if flag(temp_list[0], name_list) and flag(temp_list[2], name_list):
                    tableData.append(temp_list)

            # 将预加载的规则存到session
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

        if len(head_entity_list) == 0 or len(tail_entity_list) == 0:
            messages.success(request, "规则为空，请重新添加规则！")
            return redirect('/toExcel/')
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
        id = random.randint(20, 200000)

        temp = [head_entity_list[0], head_property_list, tail_entity_list[0], tail_property_list, id]

        '''
        将新的规则插入到规则表中  将属性列表转换成  A,B,C 格式进行存储
        '''
        # 连接数据库
        conn = pymysql.connect(host='123.56.52.53', port=3306, user='root', password='root',
                               database='source')
        cursor = conn.cursor()
        sql = "INSERT INTO excel_relation VALUES('%s','%s','%s','%s','%s')" % (
        head_entity_list[0], head_property_list, tail_entity_list[0], tail_property_list, id)
        cursor.execute(sql)
        conn.commit()

        tableData.append(temp)
        request.session['tableData'] = tableData

        return render(request, 'excel.html', {'name_list': name_list, 'tableData': tableData})


def excel_delete(request):
    id = request.GET.get('id')
    tableData = request.session.get('tableData')
    name_list = request.session.get('name_list')
    # 连接数据库
    conn = pymysql.connect(host='123.56.52.53', port=3306, user='root', password='root',
                           database='source')
    cursor = conn.cursor()
    sql = "DELETE FROM excel_relation WHERE id = '%s'" % id
    cursor.execute(sql)
    conn.commit()

    for data in tableData:
        if data[4] == int(id):
            tableData.remove(data)
    request.session['tableData'] = tableData

    return render(request, 'excel.html', {'name_list': name_list, 'tableData': tableData})


def excel_extract(request):
    if request.method == 'POST':

        # 获取session域中的tableData
        tableData = request.session.get('tableData')

        # 对每个规则进行抽取
        for data in tableData:

            # 获取到前端选择的字段
            head_entity = data[0]
            head_property_list = data[1]
            tail_entity = data[2]
            tail_property_list = data[3]

            print(data)

            # 根据表的字段名进行抽取，判断头实体和尾实体的属性表是否为空
            if len(head_property_list) != 0 and len(tail_property_list) != 0:
                create_relation(head_entity, head_property_list, tail_entity, tail_property_list)
            elif len(head_property_list) == 0 and len(tail_property_list) != 0:
                create_relation1(head_entity, tail_entity, tail_property_list)
            elif len(head_property_list) != 0 and len(tail_property_list) == 0:
                create_relation2(head_entity, head_property_list, tail_entity)
            else:
                create_relation3(head_entity, tail_entity)

    # 获取session域中的name_list
    name_list = request.session.get('name_list')

    # 抽取完之后将session置为空
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

    # 头实体类型名
    head_entity_typename = head_entity
    # 尾实体类型名 / 关系名
    tail_entity_typename = tail_entity

    # 根据查询条件编写的查询语句
    sql = "select %s, %s,%s,%s from name" % (
    head_entity_typename, tail_entity_typename, head_property_list, tail_property_list)
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
        # 查询出来的头实体的属性列表的value
        head_property_list_value = result[2:head_property_num + 2]
        # 查询出来的尾实体的属性列表的value
        tail_property_list_value = result[head_property_num + 2:]
        # 存储头实体属性结果集（字典存储）
        head_property_dict = {}
        # 存储尾实体属性结果集（字典存储）
        tail_property_dict = {}

        # 生成头实体属性字典 例如：{“故障件”：显示器}
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
            创建并更新节点和关系【先判断两个节点是否相同，再判断一下节点是否已经存在】
        '''
        # 两个实体名不一样
        if head_entity_value != tail_entity_value:
            # 两个实体都不存在，创建节点和关系
            if len(select_head_entity) == 0 and len(select_tail_entity) == 0:
                db.createNode(head_entity_value, head_entity_typename, head_property_dict)
                db.createNode(tail_entity_value, tail_entity_typename, tail_property_dict)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 头实体已经存在，更新头实体属性，创建尾实体和关系
            elif len(select_head_entity) != 0 and len(select_tail_entity) == 0:
                db.updateNode(head_entity_value, head_property_dict)
                db.createNode(tail_entity_value, tail_entity_typename, tail_property_dict)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 尾实体已经存在，更新尾实体属性，创建头实体和关系
            elif len(select_head_entity) == 0 and len(select_tail_entity) != 0:
                db.createNode(head_entity_value, head_entity_typename, head_property_dict)
                db.updateNode(tail_entity_value, tail_property_dict)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 两个实体都已经存在，更新两个实体的属性
            else:
                db.updateNode(head_entity_value, head_property_dict)
                db.updateNode(tail_entity_value, tail_property_dict)
                # 判断两个实体间是否已存在关系，若不存在则创建关系
                if db.findRelationByEntities(head_entity_value, tail_entity_value) or db.findRelationByEntities(
                        tail_entity_value, head_entity_value):
                    continue
                else:
                    db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value,
                                           tail_entity_typename,
                                           tail_entity_typename)
        else:
            continue
    cursor.close()  # 关闭游标
    conn.close()  # 关闭连接


def create_relation1(head_entity, tail_entity, tail_property_list):
    conn = pymysql.connect(host='123.56.52.53', port=3306, user='root', password='root',
                           database='source')
    cursor = conn.cursor()

    # ['故障件','故障件编号']
    tail_property_list_last = tail_property_list.split(',')

    # 获取头实体属性列表的个数
    tail_property_num = len(tail_property_list_last)

    # 头实体类型名
    head_entity_typename = head_entity
    # 尾实体类型名 / 关系名
    tail_entity_typename = tail_entity

    # 根据查询条件编写的查询语句
    sql = "select %s, %s, %s from name" % (head_entity_typename, tail_entity_typename, tail_property_list)
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
        # 查询出来的尾实体的属性列表的value
        tail_property_list_value = result[2:tail_property_num + 2]
        # 存储尾实体属性结果集（字典存储）
        tail_property_dict = {}

        # 生成尾实体属性字典 例如：{“故障件”：显示器}
        for j in range(len(tail_property_list_last)):
            tail_property_dict.update({tail_property_list_last[j]: tail_property_list_value[j]})

        # 根据头实体名来查找neo4j数据库是否已经存在实体
        select_head_entity = db.findEntity(head_entity_value)
        # 根据尾实体名来查找neo4j数据库是否已经存在实体
        select_tail_entity = db.findEntity(tail_entity_value)

        '''
            创建并更新节点和关系【先判断两个节点是否相同，再判断一下节点是否已经存在】
        '''
        # 两个实体名不一样
        if head_entity_value != tail_entity_value:
            # 两个实体都不存在，创建节点和关系
            if len(select_head_entity) == 0 and len(select_tail_entity) == 0:
                db.createNode2(head_entity_value, head_entity_typename)
                db.createNode(tail_entity_value, tail_entity_typename, tail_property_dict)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 头实体已经存在，创建尾实体和关系
            elif len(select_head_entity) != 0 and len(select_tail_entity) == 0:
                db.createNode(tail_entity_value, tail_entity_typename, tail_property_dict)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 尾实体已经存在，更新尾实体属性，创建头实体和关系
            elif len(select_head_entity) == 0 and len(select_tail_entity) != 0:
                db.createNode2(head_entity_value, head_entity_typename)
                db.updateNode(tail_entity_value, tail_property_dict)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 两个实体都已经存在，更新尾实体的属性
            else:
                db.updateNode(tail_entity_value, tail_property_dict)
                # 判断两个实体间是否已存在关系，若不存在则创建关系
                if db.findRelationByEntities(head_entity_value, tail_entity_value) or db.findRelationByEntities(
                        tail_entity_value, head_entity_value):
                    continue
                else:
                    db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value,
                                           tail_entity_typename,
                                           tail_entity_typename)
        else:
            continue
    cursor.close()  # 关闭游标
    conn.close()  # 关闭连接


def create_relation2(head_entity, head_property_list, tail_entity):
    conn = pymysql.connect(host='123.56.52.53', port=3306, user='root', password='root',
                           database='source')
    cursor = conn.cursor()

    # ['故障件','故障件编号']
    head_property_list_last = head_property_list.split(',')

    # 获取头实体属性列表的个数
    head_property_num = len(head_property_list_last)

    # 头实体类型名
    head_entity_typename = head_entity
    # 尾实体类型名 / 关系名
    tail_entity_typename = tail_entity

    # 根据查询条件编写的查询语句
    sql = "select %s, %s, %s from name" % (head_entity_typename, tail_entity_typename, head_property_list)
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
        # 查询出来的头实体的属性列表的value
        head_property_list_value = result[2:head_property_num + 2]
        # 存储头实体属性结果集（字典存储）
        head_property_dict = {}

        # 生成头实体属性字典 例如：{“故障件”：显示器}
        for k in range(len(head_property_list_last)):
            head_property_dict.update({head_property_list_last[k]: head_property_list_value[k]})

        # 根据头实体名来查找neo4j数据库是否已经存在实体
        select_head_entity = db.findEntity(head_entity_value)
        # 根据尾实体名来查找neo4j数据库是否已经存在实体
        select_tail_entity = db.findEntity(tail_entity_value)

        '''
            创建并更新节点和关系【先判断两个节点是否相同，再判断一下节点是否已经存在】
        '''
        # 两个实体名不一样
        if head_entity_value != tail_entity_value:
            # 两个实体都不存在，创建节点和关系
            if len(select_head_entity) == 0 and len(select_tail_entity) == 0:
                db.createNode(head_entity_value, head_entity_typename, head_property_dict)
                db.createNode2(tail_entity_value, tail_entity_typename)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 头实体已经存在，更新头实体属性，创建尾实体和关系
            elif len(select_head_entity) != 0 and len(select_tail_entity) == 0:
                db.updateNode(head_entity_value, head_property_dict)
                db.createNode2(tail_entity_value, tail_entity_typename)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 尾实体已经存在，创建头实体和关系
            elif len(select_head_entity) == 0 and len(select_tail_entity) != 0:
                db.createNode(head_entity_value, head_entity_typename, head_property_dict)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 两个实体都已经存在，更新两个实体的属性
            else:
                db.updateNode(head_entity_value, head_property_dict)
                # 判断两个实体间是否已存在关系，若不存在则创建关系
                if db.findRelationByEntities(head_entity_value, tail_entity_value) or db.findRelationByEntities(
                        tail_entity_value, head_entity_value):
                    continue
                else:
                    db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value,
                                           tail_entity_typename,
                                           tail_entity_typename)
        else:
            continue
    cursor.close()  # 关闭游标
    conn.close()  # 关闭连接


def create_relation3(head_entity, tail_entity):
    conn = pymysql.connect(host='123.56.52.53', port=3306, user='root', password='root',
                           database='source')
    cursor = conn.cursor()

    # 头实体类型名
    head_entity_typename = head_entity
    # 尾实体类型名 / 关系名
    tail_entity_typename = tail_entity

    # 根据查询条件编写的查询语句
    sql = "select %s, %s from name" % (head_entity_typename, tail_entity_typename)
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

        # 根据头实体名来查找neo4j数据库是否已经存在实体
        select_head_entity = db.findEntity(head_entity_value)
        # 根据尾实体名来查找neo4j数据库是否已经存在实体
        select_tail_entity = db.findEntity(tail_entity_value)

        '''
            创建并更新节点和关系【先判断两个节点是否相同，再判断一下节点是否已经存在】
        '''
        # 两个实体名不一样
        if head_entity_value != tail_entity_value:
            # 两个实体都不存在，创建节点和关系
            if len(select_head_entity) == 0 and len(select_tail_entity) == 0:
                db.createNode2(head_entity_value, head_entity_typename)
                db.createNode2(tail_entity_value, tail_entity_typename)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 头实体已经存在，创建尾实体和关系
            elif len(select_head_entity) != 0 and len(select_tail_entity) == 0:
                db.createNode2(tail_entity_value, tail_entity_typename)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 尾实体已经存在，创建头实体和关系
            elif len(select_head_entity) == 0 and len(select_tail_entity) != 0:
                db.createNode2(head_entity_value, head_entity_typename)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 两个实体都已经存在，更新两个实体的属性
            else:
                # 判断两个实体间是否已存在关系，若不存在则创建关系
                if db.findRelationByEntities(head_entity_value, tail_entity_value) or db.findRelationByEntities(
                        tail_entity_value, head_entity_value):
                    continue
                else:
                    db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value,
                                           tail_entity_typename,
                                           tail_entity_typename)
        else:
            continue
    cursor.close()  # 关闭游标
    conn.close()  # 关闭连接
