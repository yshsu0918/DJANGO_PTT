from django.shortcuts import render
from django.http import HttpResponse
from . import pttdbs
from datetime import timedelta

# Create your views here.

from .models import Ptt
from .models import Querywho


def index(request):
	return HttpResponse('Hello world...')


def TEST(request):
	if request.method == 'POST':
		A = request.POST['A']

		print("Query: ", A)

		C = Querywho(id=A)
		C.save()

		Q = Ptt.objects.filter(ID=A)
		Q = Q.order_by('link').reverse()

		content = ''
		QQ = '<p>URL: <a href="{url}">{url}</a></p>'
		for x in Q:
			content += QQ.format(url=x.link) + x.ID + ' ' +x.content +' ' +x.time+ ' <br>'

		return HttpResponse(content)
	else:
		return render(request, "search/search.html")

def UPDATEDAY(request):
	#按照時間更新 每天更新兩天的量
	result = pttdbs.myscript( timedelta(days=-2) )
	return HttpResponse(result)

def UPDATE(request):
	#每小時更新兩小時的量
	result = pttdbs.myscript( timedelta(hours=-2) )
	return HttpResponse(result)



'''
	counter = 0
	for x in dbs:
		#print(x)
		try:
			q = Ptt(hash=x['hash'], ID=x['ID'], content = x['content'], time = x['time'] , link = x['link'])
			q.save()
		except:
			print(x)
		if(counter % 10000==0):
			print(x)
			print('#',end='')
		counter += 1

	content = 'Update complete'
'''
