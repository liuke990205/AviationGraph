# Create your models here.
from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)


class Annotation(models.Model):
    annotation_id = models.AutoField(primary_key=True)
    content = models.TextField()
    flag = models.BooleanField()
    file_name = models.CharField(max_length=100)
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)  # 设置外键


class Log(models.Model):
    log_id = models.AutoField(primary_key=True)
    annotation_id = models.CharField(max_length=10)
    user_id = models.CharField(max_length=10)


class Temp(models.Model):
    temp_id = models.AutoField(primary_key=True)
    headEntity = models.CharField(max_length=100)
    headEntityType = models.CharField(max_length=100)

    tailEntity = models.CharField(max_length=100)
    tailEntityType = models.CharField(max_length=100)

    relationshipCategory = models.CharField(max_length=100)
    annotation_id = models.ForeignKey('Annotation', on_delete=models.CASCADE)
    user_id = models.IntegerField()
    filename = models.CharField(max_length=100)


class Dictionary(models.Model):
    dictionary_id = models.AutoField(primary_key=True)
    entity = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100)


class Relation(models.Model):
    relation_id = models.AutoField(primary_key=True)
    head_entity = models.CharField(max_length=100)
    tail_entity = models.CharField(max_length=100)
    relation = models.CharField(max_length=100)


class Aircraft(models.Model):
    aircraft_id = models.AutoField(primary_key=True)
    aircraft_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)


class Model(models.Model):
    model_id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)


class Rel(models.Model):
    rel_id = models.AutoField(primary_key=True)
    headEntity = models.CharField(max_length=100)
    headEntityType = models.CharField(max_length=100)
    tailEntity = models.CharField(max_length=100)
    tailEntityType = models.CharField(max_length=100)
    relationshipCategory = models.CharField(max_length=100)
    text = models.CharField(max_length=255)
    re_flag = models.IntegerField()

class Fault(models.Model):
    """
    创建如下几个表的字段
    """
    id = models.IntegerField(primary_key=True)

    phenomenon = models.CharField('phenomenon', max_length=100)

    reason = models.CharField('reason', max_length=100)

    # 指定表名 不指定默认APP名字——类名(app_demo_Student)
    class Meta:
        db_table = 'fault'