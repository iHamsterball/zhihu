from django.core import serializers
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import json, string, time

from activities import Activities
from avatar import Avatar
from status import Status

def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render(request))

def activities(request):
    template = loader.get_template('activities.html')
    return HttpResponse(template.render(request))

def about(request):
    template = loader.get_template('about.html')
    return HttpResponse(template.render(request))

def avatar(request):
    template = loader.get_template('avatar.html')
    return HttpResponse(template.render(request))

def status(request):
    template = loader.get_template('status.html')
    return HttpResponse(template.render(request))

@csrf_exempt
def activities_handler(request):
    user_id = request.POST.get('user_id','')
    print 'request id: ' + user_id
    checked = request.POST.get('checked', 0)
    range_str = request.POST.get('range', '')
    timezone = request.POST.get('timezone', 'Asia/Harbin')
    print timezone
    msg = ''

    if Activities.check_userid(user_id):
        fetcher = Activities(user_id)
    else:
        msg = '用户名不存在'
        return HttpResponse(json.dumps({"list":'', "msg":msg}))

    if not fetcher.check_gathered():
        fetcher.gather_from_website()
        print "Gathering from website..."
    else:
        fetcher.load_from_file()
        print "Loading from saved file..."

    start = range_str[0:10] + ' 00:00:00'
    end = range_str[13:23] + ' 23:59:59'

    start = int(time.mktime(time.strptime(start,'%Y-%m-%d %H:%M:%S')))
    end = int(time.mktime(time.strptime(end,'%Y-%m-%d %H:%M:%S')))

    if string.atoi(checked) == 1:
        fetcher.generate_statistics(timezone, start, end)
    else:
        fetcher.generate_statistics(timezone)

    if(fetcher.calculate() == False):
        msg = '所选时段暂无数据'
    print fetcher.relative_frequency
    #list = serializers.serialize("json", fetcher.relative_frequency)
    return HttpResponse(json.dumps({"list":fetcher.relative_frequency, "msg":msg}))

@csrf_exempt
def avatar_handler(request):
    userid = request.POST.get('userid','')
    msg = ''

    if Activities.check_userid(userid):
        fetcher = Avatar(userid)
    else:
        msg = '用户名不存在'
        return HttpResponse(json.dumps({"src":'', "msg":msg}))

    fetcher.fetch_img_url()
    fetcher.save_img()
    return HttpResponse(json.dumps({"src":fetcher.ret, "msg":msg}))

@csrf_exempt
def status_handler(request):
    fetcher = Status()
    if fetcher:
	del fetcher
	fetcher = Status()
    return HttpResponse(json.dumps({"delay":fetcher.ping()}))
