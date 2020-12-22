import json

from django.shortcuts import render

from Hello.toolkit.pre_load import neo4jconn


# 跳转到主页面
def toHome(request):
    username = request.session.get('username')
    if username is None:
        return render(request, 'login.html')
    db = neo4jconn
    searchResult = db.findAll()
    searchEntity = db.findAllEntity()

    number = request.session.get('number')

    return render(request, 'home.html',
                  {'searchResult': json.dumps(searchResult, ensure_ascii=False), 'relation_amount': len(searchResult),
                   'searchEntity': json.dumps(searchEntity, ensure_ascii=False),'entity_amount': len(searchEntity),
                   'number': number})
