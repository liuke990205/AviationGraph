import docx
from django.contrib import messages
from django.shortcuts import render, redirect

from Hello.models import Dictionary
# Create your views here.
from Hello.ner_ch.src.lstm_crf.main import NER


def toEntityRecognition(request):
    return render(request, 'entity_recognition.html')


index = 0


def convert(dict, sentence):
    lables = {'AIR': '航空器', 'WEA': '武器', 'MATH': '数学模型', 'SYS': '系统', 'TAR': '性能指标', 'DOC': '参考文档'}
    list = []
    s = 0
    end = len(sentence)

    def function(date):
        return date['start']

    dict.sort(key=function)
    # 声明全局变量
    global index
    for t in dict:
        start = t['start']
        stop = t['stop']
        type = lables[t['type']]
        if t['start'] > s:
            data = {'index': index, 'str': sentence[s:start], 'type': 'none'}
            list.append(data)
        data = {'index': index, 'str': sentence[start:stop], 'type': type}
        list.append(data)
        s = stop
        end = stop
        index = index + 1
    if len(sentence) > end:
        data = {'index': index + 1, 'str': sentence[end:len(sentence)], 'type': 'none'}
        list.append(data)
    return list


def ner(request):
    list = []
    if request.POST:
        sentence = request.POST.get('sentence', None)
        if sentence:
            sentence = sentence.replace(" ", "")
            cn = NER("predict")
            temp = cn.predict(sentence)
            list = convert(temp, sentence)
            # save(temp)
    request.session['doc'] = list
    return redirect('/display_result/')


def upload2(request):
    if request.method == 'POST':
        # 获取文件名
        file = request.FILES.get('file')
        if file:
            new_data = []
            with open('upload_file/entoty_extraction_word.docx', 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            file = docx.Document("upload_file/entoty_extraction_word.docx")
            for p in file.paragraphs:
                print(p.text)
                data = p.text.strip('\n')
                new_data.append(data)
            list = []
            cn = NER("predict")
            for sentence in new_data:
                sentence = sentence.replace(" ", "")
                temp = cn.predict(sentence)
                list.extend(convert(temp, sentence))
                list.append({'index': '', 'str': '', 'type': 'enter'})
                # save(temp)
            request.session['doc'] = list
            return redirect('/display_result/')
        else:
            messages.success(request, "文件为空！")
            return redirect('/ner/')


def save_entity(request):
    resultList = request.session.get('result_List')
    print(resultList)
    for data in resultList:
        # 注意get和filter的区别
        d = Dictionary.objects.filter(entity=data['str'])
        if d:
            pass
        else:
            dict = Dictionary(entity=data['str'], entity_type=data['type'])  # 将数据插入到数据库中
            dict.save()
    messages.success(request, "保存成功！")
    return render(request, 'entity_recognition.html')


def display_result(request):
    doc = request.session.get('doc')
    resultList = []
    for li in doc:
        if (li['type'] != 'none') & (li['type'] != 'enter'):
            resultList.append(li)
    print(resultList)
    request.session['result_List'] = resultList

    return render(request, 'entity_recognition.html', {'doc': doc, 'resultList': resultList})


def modifyEntity(request):
    entity = request.POST.get('Entity')
    entityType = request.POST.get('EntityType')
    index = request.POST.get('index')
    # print(index, entity, entityType)
    resultList = request.session.get('result_List')

    for data in resultList:
        if data['index'] == int(index):
            print(index)
            data['str'] = entity
            data['type'] = entityType

    print(resultList)
    doc = request.session.get('doc')

    request.session['result_List'] = resultList

    return render(request, 'entity_recognition.html', {'doc': doc, 'resultList': resultList})


def deleteEntity(request):
    index = request.GET.get('index')
    print(index)
    # print(index, entity, entityType)
    resultList = request.session.get('result_List')

    for data in resultList:
        if data['index'] == int(index):
            print(data)
            resultList.remove(data)
        print(resultList)

    request.session['result_List'] = resultList
    doc = request.session.get('doc')
    return render(request, 'entity_recognition.html', {'doc': doc, 'resultList': resultList})
