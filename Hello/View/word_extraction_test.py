# -*- coding: utf-8 -*-

def test(string: str, line: str) -> list:
    start = line.find(string)
    end = line.find("等")
    headEntity = line[0:start]
    print(headEntity) #客车

    list = line[start + len(string) + 1:end]
    print(list)#a） 小型客车（1辆）；b） 中型客车（1辆）；c） 大型客车（3辆），分为铰接式客车，双层客车和多层客车
    result_list = []

    for data in list.split("；"):
        index = data.find('）')
        if index != -1:
            data2 = data[index+1:] #大型客车（3辆），分为铰接式客车，双层客车和多层客车
            #print(data2, 222)
            for i in range(1, 1000):
                if data2.find(chr(i)) != -1:
                    beg_index = data2.find('（')
                    end_index = data2.find('）')
                    tailEntity = data2[0:beg_index] #大型客车
                    in_entity = data2[beg_index + 1:end_index]
                    temp_list =[tailEntity, "有", in_entity]
                    result_list.append(temp_list)

                    temp_list1 = [headEntity, "组成关系", tailEntity]  #, line.replace("\n", "")
                    result_list.append(temp_list1)
                    break
    return result_list


if __name__ == '__main__':
    test("主要包括", "客车主要包括：a） 小型客车（1辆）；b） 中型客车（1辆）；c） 大型客车（3辆），分为铰接式客车，双层客车和多层客车等。")