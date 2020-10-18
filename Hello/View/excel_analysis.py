# coding=gbk

import xlrd
import csv
from Hello.toolkit.pre_load import neo4jconn

def excel_one_line_to_list():
    file_name = "C:/Users/����/Desktop/excel_analysis/import.xlsx"
    excel = xlrd.open_workbook(file_name)
    sheet = excel.sheet_by_index(0)
    row_number = sheet.nrows
    column_number = sheet.ncols
    field_list = sheet.row_values(1)
    print(field_list)

    for data in field_list:
        if data == "���ϼ�":
            # ���ϼ���������
            faulty_component = field_list.index(data)
        elif data == "רҵ":
            # רҵ��������
            professional = field_list.index(data)
        elif data == "����":
            # ���ŵ�������
            department = field_list.index(data)
        elif data == "����λ��":
            # ����λ�õ�������
            local = field_list.index(data)
        elif data == "��������":
            # ���������������
            failure_phenomenon = field_list.index(data)

        elif data == "����ʱ��":
            # ����ʱ����������
            find_the_opportunity = field_list.index(data)
        elif data == "����ԭ��":
            # ���ŵ�������
            cause_of_failure = field_list.index(data)
        elif data == "�ų�����":
            # �ų�������������
            ruled_out = field_list.index(data)
    data_list = []
    for i in range(2, row_number):
        data_list.append(sheet.row_values(i))
    print(data_list)
    db = neo4jconn

    # �����ս��
    result_list = []
    temp_list = ["ͷʵ��", "ͷʵ������", "βʵ��", "βʵ������", "��ϵ"]
    result_list.append(temp_list)
    for data in data_list:
        # ���м���
        temp_list = [data[faulty_component], "���ϼ�", data[professional], "רҵ", "����רҵ"]
        #temp_list = ["�ɻ�", "�ɻ�", data[faulty_component], "���ϼ�", "����"]

        #д�뵽��ʱ����б�
        result_list.append(temp_list)
        #���ڵ���Ϣд�뵽Neo4j���ݿ�
        if db.findEntity(data[faulty_component]) is None:
            db.createNode2(data[faulty_component], "���ϼ�")
        if db.findEntity(data[professional]) is None:
            db.createNode2(data[professional], "רҵ")
        if db.findEntity(data[department]) is None:
            db.createNode2(data[department], "����")
        if db.findEntity(data[local]) is None:
            db.createNode2(data[local], "����λ��")
        if db.findEntity(data[failure_phenomenon]) is None:
            db.createNode2(data[failure_phenomenon], "��������")
        if db.findEntity(data[find_the_opportunity]) is None:
            db.createNode2(data[find_the_opportunity], "����ʱ��")
        if db.findEntity(data[cause_of_failure]) is None:
            db.createNode2(data[cause_of_failure], "����ԭ��")
        if db.findEntity(data[ruled_out]) is None:
            db.createNode2(data[ruled_out], "�ų�����")
        if db.findEntity("�ɻ�") is None:
            db.createNode2("�ɻ�", "�ɻ�")

        db.insertExcelRelation(data[faulty_component], data[professional], "����רҵ")
        temp_list = [data[faulty_component], "���ϼ�", data[department], "����", "��������"]
        result_list.append(temp_list)

        #db.createNode(data[faulty_component], "���ϼ�", {})
        db.insertExcelRelation(data[faulty_component], data[department], "��������")
        temp_list = [data[faulty_component], "���ϼ�", data[local], "����λ��", "����λ��"]
        result_list.append(temp_list)

        #db.createNode(data[faulty_component], "���ϼ�", {})
        db.insertExcelRelation(data[faulty_component], data[local], "����λ��")
        temp_list = [data[faulty_component], "���ϼ�", data[failure_phenomenon], "��������", "��������"]
        result_list.append(temp_list)


        #db.createNode(data[faulty_component], "���ϼ�", {})
        db.insertExcelRelation(data[faulty_component], data[failure_phenomenon], "��������")
        temp_list = [data[failure_phenomenon], "��������", data[find_the_opportunity], "����ʱ��", "����ʱ��"]
        result_list.append(temp_list)

        #db.createNode(data[failure_phenomenon], "��������", {})
        db.insertExcelRelation(data[failure_phenomenon], data[find_the_opportunity], "����ʱ��")
        temp_list = [data[failure_phenomenon], "��������", data[cause_of_failure], "����ԭ��", "����ԭ��"]
        result_list.append(temp_list)

        #db.createNode(data[failure_phenomenon], "��������", {})
        db.insertExcelRelation(data[failure_phenomenon], data[cause_of_failure], "����ԭ��")
        temp_list = [data[cause_of_failure], "����ԭ��", data[ruled_out], "�ų�����", "�ų�����"]
        result_list.append(temp_list)

        db.insertExcelRelation("�ɻ�", data[faulty_component], "����")

        #db.createNode(data[cause_of_failure], "����ԭ��", {})
        db.insertExcelRelation(data[cause_of_failure], data[ruled_out], "�ų�����")
        temp_list = ["�ɻ�", "�ɻ�", data[faulty_component], "���ϼ�", "����"]
        result_list.append(temp_list)

    print(result_list)
    #���б���Ϣ�洢��Excel��
    for data in result_list:
        with open("C:/Users/����/Desktop/excel_analysis/export.csv", "w", newline="") as csvfile:
            write = csv.writer(csvfile)
            write.writerow(data)

if __name__ == '__main__':
    excel_one_line_to_list()