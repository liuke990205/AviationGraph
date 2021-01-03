# -*- coding: utf-8 -*-
import csv

'''
 * @Author 刘珂
 * @date 2020/9/21 19:15
 * @Version v1.0
 */
'''

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


def made_of_1(string: str, line: str) -> list:
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
    start = line.find(string)
    end = line.find("。")
    list = line[start + len(string):end]
    # print(line[start + len(r):end], 222)
    result_list = []
    if list.find("、") != -1:
        for data in list.split("、"):
            if data[-1] == "等":
                temp_list = [line[0:start], "组成关系", data[0:-1], line.replace("\n", "")]
                result_list.append(temp_list)
            else:
                temp_list = [line[0:start], "组成关系", data, line.replace("\n", "")]
                result_list.append(temp_list)
    elif list.find("；") != -1:
        list = list[1:]
        # list =  a) 小型客车（1辆）；b) 中型客车（1辆）；c) 大型客车（3辆），分为铰接式客车，双层客车和多层客车等
    return result_list


'''
关系：【位置关系】
string  = 位于......
'''


def local(string: str, line: str) -> list:
    # 获取关键字位置
    start = line.find(string)
    # 获取结束位置
    end = line.find("。")
    temp_list = [line[0:start], "位置关系", line[start + len(string):end], line.replace("\n", "")]  # 注意删除换行符
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


def main(infile):
    infopen = open(infile, 'r', encoding="utf-8")
    # 后期读取配置文件或者前端列表
    relation = ["位于", "使用", "采用", "主要包括", "分为", "\t", "组成", "构成"]
    result_list = []
    # 读取格式化之后的文件
    lines1 = infopen.readlines()
    for line in lines1:
        # print(line)
        for r in relation:
            if line.find(r) != -1:
                if r == "采用" or r == "使用":
                    temp_list = use(r, line)
                    # for data in temp_list:
                    result_list.append(temp_list)
                    # print(use(r, line))
                if r == "位于":
                    # print(local(r, line))
                    temp_list = local(r, line)
                    # for data in temp_list:
                    result_list.append(temp_list)
                if r == "主要包括" or r == "分为":
                    # print(made_of_2(r, line))
                    temp_list = made_of_2(r, line)
                    for data in temp_list:
                        result_list.append(data)
                if r == "\t":
                    # print(table(line))
                    temp_list = table(line)
                    for data in temp_list:
                        result_list.append(data)
                if line.find("由") != -1:
                    # print(made_of_1(r, line))
                    temp_list = made_of_1(r, line)
                    for data in temp_list:
                        result_list.append(data)
    for data in result_list:
        with open("C:/Users/26407/Desktop/txt_analysis/txt_export.csv", "a+", newline="") as csvfile:
            write = csv.writer(csvfile)
            write.writerow(data)
    infopen.close()


'''
格式化待处理文件
1.去掉空行
2.去掉数字开头的行
3.将列表形式处理成一行（未完成）
'''


def format_file(infile, outfile):
    infopen = open(infile, 'r', encoding="utf-8")
    outfopen = open(outfile, 'w', encoding="utf-8")

    lines = infopen.readlines()

    t_list = []
    for j in range(len(lines)):
        if lines[j].split():
            if lines[j].find("主要包括") != -1:
                for i in range(ord("a"), ord("z") + 1):
                    if lines[j + 1].startswith(chr(i)) == True:
                        t_list.append(lines[j].replace("\n", ""))
                        t_list.append(lines[j + 1].replace("\n", ""))
                        for k in range(j + 2, len(lines)):
                            for i in range(ord("a"), ord("z") + 1):
                                if lines[k].startswith(chr(i)) == True:
                                    t_list.append(lines[k].replace("\n", ""))
            list_str = ''.join(t_list)
            if list_str:
                outfopen.writelines(list_str + "\n")
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
    # 调用主处理函数
    main(outfile)


if __name__ == '__main__':
    format_file("C:/Users/26407/Desktop/txt_analysis/test.txt", "C:/Users/26407/Desktop/txt_analysis/temp.txt")
