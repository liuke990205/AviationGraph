# -*- coding: utf-8 -*-
from py2neo import Graph, NodeMatcher


# 版本说明：Py2neo v4
class Neo4j_Handle():
    graph = None
    matcher = None

    def __init__(self):
        print("Neo4j Init ...")

    def connectDB(self):
        self.graph = Graph("bolt: // localhost:7687", username="neo4j", password="root")
        self.matcher = NodeMatcher(self.graph)

    # 实体查询
    def getEntityRelationbyEntity(self, value):
        # 查询实体：不考虑实体类型，只考虑关系方向
        answer = self.graph.run(
            "MATCH (n1) - [rel] -> (n2)  WHERE n1.name =~ \"" + value + ".*\"  OR n2.name = \"" + value + "\" RETURN n1, rel,n2").data()
        return answer

    # 关系查询:实体1
    def findRelationByEntity1(self, entity1):
        answer = self.graph.run("MATCH (n1{name:\"" + entity1 + "\"})- [rel] -> (n2) RETURN n1,rel,n2").data()
        return answer

    # 关系查询：实体2
    def findRelationByEntity2(self, entity1):
        answer = self.graph.run("MATCH (n1)- [rel] -> (n2{name:\"" + entity1 + "\"}) RETURN n1,rel,n2").data()
        return answer

    # 关系查询：实体1+关系
    def findOtherEntities(self, entity, relation):
        answer = self.graph.run(
            "MATCH (n1{name:\"" + entity + "\"})- [rel:" + relation + " {type:\"" + relation + "\"}] -> (n2) RETURN n1,rel,n2").data()
        return answer

    # 关系查询：关系+实体2
    def findOtherEntities2(self, entity, relation):
        answer = self.graph.run(
            "MATCH (n1)- [rel:" + relation + "{type:\"" + relation + "\"}] -> (n2{name:\"" + entity + "\"}) RETURN n1,rel,n2").data()
        return answer

    # 关系查询：实体1+实体2(注意Entity2的空格）
    def findRelationByEntities(self, entity1, entity2):
        # 品牌 + 品牌
        answer = self.graph.run(
            "MATCH (n1{name:\"" + entity1 + "\"})- [rel] -> (n2{name:\"" + entity2 + "\"}) RETURN n1,rel,n2").data()
        return answer

    # 查询数据库中是否有对应的实体-关系匹配
    def findEntityRelation(self, entity1, relation, entity2):
        answer = self.graph.run(
            "MATCH (n1{name:\"" + entity1 + "\"})- [rel{type:\"" + relation + "\"}] -> (n2{name:\"" + entity2 + "\"}) RETURN n1,rel,n2").data()
        return answer

    def findAll(self):
        answer = self.graph.run("MATCH (n1)-[rel]->(n2) RETURN n1,n2,rel ").data()
        return answer

    def findAllEntity(self):
        answer = self.graph.run("MATCH (n) RETURN n").data()
        return answer

    def findEntity(self, entity):
        answer = self.graph.run("MATCH(x) WHERE x.name = \"" + entity + "\" return x").data()
        print(answer)
        return answer

    def insertRelation(self, entity1, relation, entity2, id):
        #print("MERGE (x{name:\"" + entity1 + "\"})-[jx:" + relation + "{type: \"" + relation + "\", id: \"" + id + "\"}]->(y{name:\"" + entity2 + "\"})")
        self.graph.run("MERGE (x{name:\"" + entity1 + "\"})-[jx:" + relation + "{type: \"" + relation + "\", id: \"" + id + "\"}]->(y{name:\"" + entity2 + "\"})")
    def insertExcelRelation(self, entity1, entity2, relation):
        self.graph.run(
            "MERGE (x{name:\"" + entity1 + "\"})-[jx:" + relation + "{type: \"" + relation + "\"}]->(y{name:\"" + entity2 + "\"})")
        print("MATCH (x{name:\"" + entity1 + "\"}), (y{name:\"" + entity2 + "\"}) MERGE (x)-[jx:" + relation + "{type: \"" + relation + "\"}]->(y)")
    def createNode(self, entity, type, dict):
        string_list = []
        for key, value in dict.items():
            # 利用格式化函数
            st = "{0}{1}{2}{3}{4}{3}".format(",", key, ":", "'", value)
            # 将字符串添加到列表中  便于后续字符串拼接
            string_list.append(st)
        # 进行字符串拼接
        st_list = "".join(string_list)
        str = "CREATE(x:" + type + "{" + " name:\"" + entity + " \" " + st_list + "})"
        self.graph.run(str)

    def createNode2(self, entity, type):
        str = "MERGE(x:" + type + "{" + " name:\"" + entity + " \" " + "})"
        print(str)
        self.graph.run(str)

    def modifyRelation(self, entity1, entity2, relation, temp_id):
        self.graph.run(
            "MATCH (n)-[rel{id:\"" + temp_id + "\"}]->(m) SET n.name=\"" + entity1 + "\", m.name=\"" + entity2 + "\", rel.type=\"" + relation + "\"")

    def deleteRelation(self, temp_id):
        self.graph.run("MATCH ()-[rel{id:\"" + temp_id + "\"}]->() DELETE rel")