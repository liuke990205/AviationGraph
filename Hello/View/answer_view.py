from django.shortcuts import render, redirect

# 跳转到问答系统页面
def toAnswer(request):
    username = request.session.get('username')
    #如果session里面没有用户名
    if username is None:
        return render(request, 'login.html')
    return render(request, 'answer.html')

def answer_question(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        print(question)

    return redirect('/toAnswer')