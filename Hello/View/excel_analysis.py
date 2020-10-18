# coding=gbk

import xlrd
import csv
from Hello.toolkit.pre_load import neo4jconn

def excel_one_line_to_list():
    file_name = "C:/Users/刘珂/Desktop/excel_analysis/import.xlsx"
    excel = xlrd.open_workbook(file_name)
    sheet = excel.sheet_by_index(0)
    row_number = sheet.nrows
    column_number = sheet.ncols
    field_list = sheet.row_values(1)
    print(field_list)

    for data in field_list:
        if data == "故障件":
            # 故障件的列索引
            faulty_component = field_list.index(data)
        elif data == "专业":
            # 专业的列索引
            professional = field_list.index(data)
        elif data == "部门":
            # 部门的列索引
            department = field_list.index(data)
        elif data == "所在位置":
            # 所在位置的列索引
            local = field_list.index(data)
        elif data == "故障现象":
            # 故障现象的列索引
            failure_phenomenon = field_list.index(data)

        elif data == "发现时机":
            # 发现时机的列索引
            find_the_opportunity = field_list.index(data)
        elif data == "故障原因":
            # 部门的列索引
            cause_of_failure = field_list.index(data)
        elif data == "排除经过":
            # 排除经过的列索引
            ruled_out = field_list.index(data)
    data_list = []
    for i in range(2, row_number):
        data_list.append(sheet.row_values(i))
    print(data_list)
    db = neo4jconn

    # 存最终结果
    result_list = []
    temp_list = ["头实体", "头实体类型", "尾实体", "尾实体类型", "关系"]
    result_list.append(temp_list)
    for data in data_list:
        # 存中间结果
        temp_list = [data[faulty_component], "故障件", data[professional], "专业", "所属专业"]
        #temp_list = ["飞机", "飞机", data[faulty_component], "故障件", "包括"]

        #写入到临时结果列表
        result_list.append(temp_list)
        #将节点信息写入到Neo4j数据库
        if db.findEntity(data[faulty_component]) is None:
            db.createNode2(data[faulty_component], "故障件")
        if db.findEntity(data[professional]) is None:
            db.createNode2(data[professional], "专业")
        if db.findEntity(data[department]) is None:
            db.createNode2(data[department], "部门")
        if db.findEntity(data[local]) is None:
            db.createNode2(data[local], "所在位置")
        if db.findEntity(data[failure_phenomenon]) is None:
            db.createNode2(data[failure_phenomenon], "故障现象")
        if db.findEntity(data[find_the_opportunity]) is None:
            db.createNode2(data[find_the_opportunity], "发现时机")
        if db.findEntity(data[cause_of_failure]) is None:
            db.createNode2(data[cause_of_failure], "故障原因")
        if db.findEntity(data[ruled_out]) is None:
            db.createNode2(data[ruled_out], "排除经过")
        if db.findEntity("飞机") is None:
            db.createNode2("飞机", "飞机")

        db.insertExcelRelation(data[faulty_component], data[professional], "所属专业")
        temp_list = [data[faulty_component], "故障件", data[department], "部门", "所属部门"]
        result_list.append(temp_list)

        #db.createNode(data[faulty_component], "故障件", {})
        db.insertExcelRelation(data[faulty_component], data[department], "所属部门")
        temp_list = [data[faulty_component], "故障件", data[local], "所在位置", "所在位置"]
        result_list.append(temp_list)

        #db.createNode(data[faulty_component], "故障件", {})
        db.insertExcelRelation(data[faulty_component], data[local], "所在位置")
        temp_list = [data[faulty_component], "故障件", data[failure_phenomenon], "故障现象", "故障现象"]
        result_list.append(temp_list)


        #db.createNode(data[faulty_component], "故障件", {})
        db.insertExcelRelation(data[faulty_component], data[failure_phenomenon], "故障现象")
        temp_list = [data[failure_phenomenon], "故障现象", data[find_the_opportunity], "发现时机", "发现时机"]
        result_list.append(temp_list)

        #db.createNode(data[failure_phenomenon], "故障现象", {})
        db.insertExcelRelation(data[failure_phenomenon], data[find_the_opportunity], "发现时机")
        temp_list = [data[failure_phenomenon], "故障现象", data[cause_of_failure], "故障原因", "故障原因"]
        result_list.append(temp_list)

        #db.createNode(data[failure_phenomenon], "故障现象", {})
        db.insertExcelRelation(data[failure_phenomenon], data[cause_of_failure], "故障原因")
        temp_list = [data[cause_of_failure], "故障原因", data[ruled_out], "排除经过", "排除经过"]
        result_list.append(temp_list)

        db.insertExcelRelation("飞机", data[faulty_component], "包括")

        #db.createNode(data[cause_of_failure], "故障原因", {})
        db.insertExcelRelation(data[cause_of_failure], data[ruled_out], "排除经过")
        temp_list = ["飞机", "飞机", data[faulty_component], "故障件", "包括"]
        result_list.append(temp_list)

    print(result_list)
    #将列表信息存储到Excel中
    for data in result_list:
        with open("C:/Users/刘珂/Desktop/excel_analysis/export.csv", "w", newline="") as csvfile:
            write = csv.writer(csvfile)
            write.writerow(data)

if __name__ == '__main__':
    excel_one_line_to_list()