import threading
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from dwebsocket import accept_websocket

from probeData.models import ParamInfo,SiteInfo,WarningInfo,UrgentPerson,User
from . import forms
import datetime
import json


import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

# Create your views here.
def index(request):
    list = [1,2,3,4,5,6,]
    return render(request, "probeData/index.html", {'list':list})

def index(request):
    site = SiteInfo()
    site.siteName = "都匀站"
    site.siteWest = "4548"
    site.siteEast = "4879"
    site.info = "都匀站位于贵州省黔南布依苗族自治区，该地区气候宜人，十分适合居住"
    # site.save()
    return render(request, "probeData/index.html")

# 单位转换
def typeToUnit(type):
    if type == "PH":
        return "pH"
    if type == "Cond":
        return "μS/cm"
    if type == "Turb":
        return "NTU"
    if type == "LDO":
        return "mg/L"
    if type == "NH":
        return "mg/L"
    if type == "COD":
        return "mg/L"
    if type == "Chla":
        return "μg/L"
    if type == "TEMP":
        return "℃"

# 站点选择
def selectSite(request):
    paramType = []
    if request.method == 'POST':
        currentSiteId =request.POST.get('currentSiteId')
        # 当前时间
        now = datetime.datetime.now()
        # 24小时前的时间
        start = now - datetime.timedelta(hours=1000, minutes=00, seconds=00)
        #获取该站点24小时之内的所有数据类型
        mm = ParamInfo.objects.filter(siteId=currentSiteId,paramTime__range=(start, now), paramTime__minute="00", paramTime__second="00").values('paramType').distinct().order_by('paramType')
        for m in mm:
            paramType.append(m['paramType'])
        return JsonResponse({"currentSiteId":currentSiteId,"paramType":paramType})


# 站点发送数据过来，此函数将站点数据存储到数据库
def probesqlsave(request):
    if request.method == 'POST':
        getdata = request.body.decode('utf-8')
        print(getdata)
        jsondata = json.loads(getdata)
        if jsondata['type'] == 'psdata':
            #截取要保存的数据
            tempbuff = '{' + getdata[33 + len(jsondata['time']) + len(jsondata['type']) + len(jsondata['siteId']):]
            tempbuff = json.loads(tempbuff)
            #循环保存数据
            for k, v in tempbuff.items():
                paramInfo = ParamInfo()
                paramInfo.siteId_id = jsondata['siteId']
                paramInfo.paramTime = jsondata['time']
                paramInfo.paramType = k
                paramInfo.data = v
                paramInfo.unit = typeToUnit(k)
                paramInfo.save()
        return HttpResponse('probesqlsave ok')


# dwebsocket 连接通道，用于保存客户端连接信息
clients =[]
@accept_websocket
def transport(request):
    print("webSocket连接成功2")
    if request.is_websocket:
        #request.session.set_expiry(10000)
        lock = threading.RLock()
        try:
            lock.acquire()
            clients.append(request.websocket)
            for message in request.websocket:
                 pass
        finally:
            clients.remove(request.websocket)
            lock.release()


# 站点post探头实时数据处理显示到前端
def sendData(request):
    if (request.method == 'POST'):
        getdata = request.body.decode('utf-8')
        jsondata = json.loads(getdata)
        # if (jsondata['siteId'] == currentSiteId):
        if (jsondata['type'] == 'pdata'):
            # tempbuf = '{' + getdata[44 + len(jsondata['siteId']):]
            for client in clients:
                client.send(getdata)
    return HttpResponse('postdataok')


# 获取24小时图表数据
def get24HourData(request):
    if request.method == "POST":
        currentSiteId = request.POST.get('currentSiteId')
        param = request.POST.get('param')
        now = datetime.datetime.now()
        start =now - datetime.timedelta(hours=1000, minutes=00, seconds=00)
        print(now)
        list = []
        time = []
        #从数据库查询24小时内指定类型的整点数据
        params = ParamInfo.objects.filter(siteId=currentSiteId,paramType=param,paramTime__range= (start,now),paramTime__minute="00",paramTime__second="00").order_by('paramTime')
        for param in params:
            list.append(param.data)
            #将时间转化为字符串，直接传时间前端显示会有问题
            time.append(param.paramTime.strftime('%Y-%m-%d %H:%M:%S') )
        return JsonResponse({'data':list,'time':time})

#获取全部站点
def getSites(request):
    list = []
    sites = SiteInfo.objects.all()
    for site in sites:
        dic = site.__dict__
        dic.pop('_state')
        list.append(dic)
        print(dic)
    return JsonResponse({'list':list})


# 报警信息实时通讯
def warningRealTime(request):
    if request.method == 'POST':
        getdata = request.body.decode('utf-8')
        jsondata = json.loads(getdata)
        if (jsondata['type'] == 'warning'):
            warning = WarningInfo()
            warning.siteId_id = jsondata['siteId']
            warning.warningTime = jsondata['time']
            warning.warningType = jsondata['warningType']
            warning.warningParam = jsondata['warningParam']
            warning.warningValue = jsondata['warningValue']
            warning.limitValue = jsondata['limitValue']
            warning.isHandle = False
            # warning.save()                  #保存数据库

            siteInfo = SiteInfo.objects.get(id = jsondata['siteId'])
            #邮件内容
            content  = siteInfo.siteName + jsondata['warningParam'] +"参数报警,时间："+jsondata['time']+\
                       "  类型："+jsondata['warningType']+"  报警值："+jsondata['warningValue']+"  限定值：" \
                        ""+jsondata['limitValue']
            recs = []   #报警站点的邮箱地址
            urgentPersons = UrgentPerson.objects.filter(siteId=jsondata['siteId']) #从数据库查询当前站点对应的维护人员
            for rec in urgentPersons:
                dic = rec.__dict__
                recs.append(dic.pop('email'))   #添加邮箱地址
            mail(content,recs)                  #发送邮件
            for client in clients:
                client.send(getdata.encode('utf-8'))        #发送到前端
        return HttpResponse('warningdataok')


#获取历史报警信息
def historyWarning(request):
    if(request.method == "POST"):
        list = []
        id = request.POST.get("currentSiteId")
        warningInfos = WarningInfo.objects.filter(isHandle=False,siteId=id)
        for info in warningInfos:
            dic = info.__dict__
            dic.pop('_state')
            dic.pop('isHandle')
            list.append(dic)
            print(list)
        return JsonResponse({"list":list})

# 实时站点信息
def rtSite(request):
    if(request.method == "POST"):
        getData = request.body.decode('utf-8')
        jsonData = json.loads(getData)
        if(jsonData["type"] == "rtSite"):
            site = SiteInfo.objects.get(id = jsonData["siteId"])
            site.siteLat = jsonData["lat"]
            site.siteLng = jsonData["lng"]
            site.state = jsonData["state"]
            site.save()
            for client in clients:
                client.send(getData.encode('utf-8'))  # 发送到前端
        return HttpResponse('rtSiteok')


def ugPerson(request):
    list = []
    if (request.method == "POST"):
        id = request.POST.get("currentSiteId")
        ugpersons = UrgentPerson.objects.filter(siteId=id)
        for ug in ugpersons:
            dic = ug.__dict__
            dic.pop('_state')
            list.append(dic)
            print(list)
        return JsonResponse({"list": list})


def mail(content,receivers):
    my_sender = '1421606162@qq.com'  # 发件人邮箱账号
    my_pass = 'xgwsjidpbjrmjihe'  # 发件人邮箱密码
    my_user = ['1421606162@qq.com','lgl1996@vip.qq.com']  # 收件人邮箱账号，我这边发送给自己

    ret = True
    try:
        print("开始发送")
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = formataddr(["FromRunoob", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        # msg['To'] = formataddr(["王彪", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "站点参数报警"  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
        # server = smtplib.SMTP()
        # server.connect("smtp.qq.com", 465)
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        #server.sendmail(my_sender, receivers, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
        print("发送成功")
    except Exception as err:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
        print(err)
    return ret


def login(request):
    if request.session.get('is_login',None):
        print("已经登录")
        return redirect('/index/')

    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = '请检查填写的内容！'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            pwd = login_form.cleaned_data.get('pwd')
            print(username,pwd)
        #验证用户名是否和密码是否为空
            try:
                user = User.objects.get(name=username)
            except:
                message = '用户名不存在！'
                return render(request, 'login/login.html',locals())
            if user.pwd == pwd:
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/index/')
            else:
                message = '密码不正确！'
                return render(request,'login/login.html',locals())
        else:
            return render(request,'login/login.html',locals())
    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        return redirect('/index/')
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            sex = register_form.cleaned_data.get('sex')

            if password1 != password2:
                message = '两次输入的密码不同！'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已经存在'
                    return render(request, 'login/register.html', locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已经被注册了！'
                    return render(request, 'login/register.html', locals())

                new_user = User()
                new_user.name = username
                new_user.password = password1
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                return redirect('/login/')
        else:
            return render(request, 'login/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有退出一说
        return redirect("/login/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/login/")