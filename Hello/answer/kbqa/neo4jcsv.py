from py2neo import Graph, Node, Relationship
import csv

# 连接neo4j数据库，输入地址、用户名、密码
graph = Graph("http://localhost:7474", username="neo4j", password='root')

graph.delete_all()
path = "D:/code/kbqa_sim/app/kbqa/data/data.csv"

with open(path, 'r',encoding="utf-8") as f:
    reader = csv.reader(f)
    data = list(reader)
print(data[1])
#1,系统,系统不好用,提高知名度
for i  in  range(1,len(data)):
    node1 = Node('entity',name = data[i][1],id = data[i][0])
    node2 = Node('pxx',name = data[i][2])
    node3 = Node('reason',name = data[i][3])

    graph.create(node1)
    graph.create(node2)
    graph.create(node3)

    pxx = Relationship(node1,'现象',node2)
    reason = Relationship(node2,'原因',node3)
    graph.create(pxx)
    graph.create(reason)

'''
MATCH (n:entity)
WITH n.name AS name, COLLECT(n) AS nodelist, COUNT(*) AS count
WHERE count > 1
CALL apoc.refactor.mergeNodes(nodelist) YIELD node
RETURN node
'''
# 归并节点
