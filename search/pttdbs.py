import requests
from lxml import etree
from bs4 import BeautifulSoup
import re

import multiprocessing as mp
import threading
import _thread
import time
import requests
import numpy as np

from hashlib import md5

from django.db import transaction


from .models import Ptt
from .models import Querywho

import os
import datetime
import time

ptturl = 'https://www.ptt.cc'

#https://www.ptt.cc/bbs/LoL/M.1521979680.A.83E.html => 偵測推文內容
def comments_in_article(url,sess):

    #print(url)
    r = sess.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    comments = []
    for x in soup.find_all(re.compile('^span')):
        try:
            if 'article-meta-value' in x['class']:
                pass
            elif 'push-userid' in x['class']:
                #md5 用來做 primary key 防止更新的時候重複
                Q = dict(hash= md5( (x.string+x.next_sibling.string).encode('utf-8')).hexdigest(),ID=x.string, content=x.next_sibling.string, time=x.next_sibling.next_sibling.string , link=url)
                comments.append(Q)
        except:
            pass
    #print(comments)

    return comments

#取得滿18歲 session
def pass_ask18():

    s = requests.Session()
    payloads = {'from': '/bbs/Gossiping/index.html', 'yes': 'yes'}
    s.post('https://www.ptt.cc/ask/over18', data = payloads)

    return s

#取得目前 https://www.ptt.cc/bbs/Gossiping/index.html 其實是 https://www.ptt.cc/bbs/Gossiping/index?????.html
def get_board_nowindex(url,sess):

    r = sess.get(url)
    #print(r.text)

    soup = BeautifulSoup(r.text, "lxml")
    QQ = ''
    for x in soup.find_all(re.compile('^a')):
        if '上頁' in str(x.string):
            QQ = x['href']

    index_num = int(QQ[QQ.find('/index')+6:-5])

    return index_num

def article_date(url,sess):

    #print(url)
    r = sess.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    article_info = []

    counter = 0
    for x in soup.find_all(re.compile('^span')):
        try:
            if 'article-meta-value' in x['class']:
                article_info.append(str(x.string))
                counter +=1
        except:
            pass
        if counter == 4:
            break
    try:
        a = article_info[3]
    except:
        return -1

    #Sat Jun  2 00:56:43 2018

    dt = datetime.datetime.strptime(a, "%a %b %d %H:%M:%S %Y")
    #print(dt)
    return dt


#https://www.ptt.cc/bbs/Gossiping/index.html => [https://www.ptt.cc/bbs/Gossiping/M.1521999297.A.04F.html, ...]
def get_article_inpage(url,sess):
    #print(url)
    r = sess.get(url)
    soup = BeautifulSoup(r.text, "lxml")

    boardname = url[url.find('/bbs/')+5:url.find('/index')]
    Q = []
    flag = '/bbs/'+boardname+'/M'
    for x in soup.find_all(re.compile('^a')):
        try:
            if flag in str(x['href']):
                Q.append(str(x['href']))
        except:
            pass

    urls = []
    for x in Q:
        urls.append(x)
        #print(article_date(ptturl+x,sess))

    last_date = 0
    for i in range(0,5):
        last_date = article_date(ptturl+Q[i],sess)
        if(last_date !=-1):
            break;

    return urls,last_date

database_content = []
datacounter = []
#這是為了數更新了幾筆資料


#一次更新一批資料
#def bulk_update(BUF, lock):



def partition(a,b,post,lock,sess,threadnum):
    BUF = []

    pa = time.time()
    for c in range(a,b):
        #print(ptturl+post[c])
        try:
            A = comments_in_article(ptturl+post[c],sess)
        except:
            continue
        BUF.extend(A)
        #每三千筆寫入資料庫一次
        if len(BUF) > 5000:
            print('threadnum: ', threadnum, len(BUF))
            lock.acquire()
            with transaction.atomic():
                for Q in BUF:
                    for key in Q.keys():
                        if Q[key] == None:
                            Q[key] = "[maybe it is a picture]"
                    q = Ptt(hash=Q['hash'], ID=Q['ID'], content = Q['content'], time = Q['time'] , link = Q['link'])
                    q.save()

            datacounter.append(len(BUF))
            BUF.clear()
            print("#")
            lock.release()

    lock.acquire()
    with transaction.atomic():
        for Q in BUF:
            for key in Q.keys():
                if Q[key] == None:
                    Q[key] = "[maybe it is a picture]"
            q = Ptt(hash=Q['hash'], ID=Q['ID'], content = Q['content'], time = Q['time'] , link = Q['link'])
            q.save()
    datacounter.append(len(BUF))
    BUF.clear()
    print("#",end='')
    lock.release()
    #把資料寫進資料庫裡面所以需要用LOCK來保證這個動作不會受到干擾

    pb = time.time()
    print('time: ', pb-pa)


def myscript(time_diff):
    #boards = dfs_find_allboard()

    datacounter.clear()
    bound_date = datetime.datetime.now()
    #time_diff = datetime.timedelta(hours = -3)

    boards = ['Gossiping', 'NBA', 'sex', 'C_Chat', 'Baseball', 'WomenTalk', 'Stock', 'marriage', 'BabyMother', 'LoL', 'movie', 'Boy-Girl', 'Beauty', 'marvel', 'MobileComm', 'car', 'ToS', 'joke', 'Lifeismoney', 'AllTogether', 'Tech_Job', 'Hearthstone', 'e-shopping', 'Japandrama', 'HatePolitics', 'Japan_Travel', 'ONE_PIECE', 'PC_Shopping', 'PlayStation', 'KR_Entertain', 'MakeUp', 'Tennis', 'SportLottery', 'home-sale', 'Tainan', 'Kaohsiung', 'Steam', 'NY-Yankees', 'KoreaDrama', 'japanavgirls', 'iOS', 'KoreaStar', 'MLB', 'TaichungBun', 'BuyTogether', 'creditcard', 'StupidClown', 'EAseries', 'BeautySalon', 'NSwitch', 'PokemonGO', 'Monkeys', 'Palmar_Drama', 'HardwareSale', 'Hsinchu', 'CFantasy', 'OverWatch', 'YuanChuang', 'MH', 'KanColle', 'Wanted', 'Salary', 'WOW', 'MuscleBeach', 'FATE_GO', 'TaiwanDrama', 'AC_In', 'FITNESS', 'PuzzleDragon', 'TypeMoon', 'PathofExile', 'TY_Research', 'WorldCup', 'Examination', 'Elephants', 'Food', 'LGBT_SEX', 'Headphone', 'Aviation', 'Guardians', 'basketballTW', 'feminine_sex', 'TWICE', 'TW_Entertain', 'mobilesales', 'CN_Entertain', 'CVS', 'cat', 'Lions', 'lesbian', 'give', 'fastfood', 'NBA_Film', 'GetMarry', 'biker', 'CarShop', 'studyteacher', 'medstudent', 'StarCraft', 'BabyProducts', 'facelift', 'ALLPOST', 'DSLR', 'Soft_Job', 'BTS', 'cookclub', 'Lineage', 'Zastrology', 'PUBG', 'nb-shopping', 'points', 'MayDay', 'AKB48', 'CATCH', 'Brand', 'EuropeTravel', 'BB-Love', 'GirlsFront', 'RealmOfValor', 'AzurLane', 'Gamesale', 'Finance', 'E-appliance', 'China-Drama', 'ShuangHe', 'part-time', 'Gemini', 'Suckcomic']

    sess = pass_ask18()
    url = 'https://www.ptt.cc/bbs/{boardname}/index{pagenum}.html'

    urls = []
    for x in boards:
        page_num = get_board_nowindex(url.format(boardname = x, pagenum='' ),sess)
        print(page_num)
        c = -1
        while 1:
            try:
                A,B = get_article_inpage(url.format(boardname = x,pagenum = page_num -c ), sess)
                urls.extend(A)
                print(B,bound_date, time_diff , bound_date+time_diff)
                if B < bound_date + time_diff:
                    break
                c+=1
            except:
                break

    print(urls)

    thread_num = 8                             #線程數
    p = np.linspace(0, len(urls), thread_num)
    thrds = []

    ss = []

    for i in range(0,thread_num):
        sess = pass_ask18()
        ss.append(sess)


    lock = threading.Lock()
    for i in range(0,thread_num-1):
        t = threading.Thread(target=partition, args=((int(p[i]) , int(p[i+1]) , urls , lock, ss[i], i)))
        t.start()
        thrds.append(t)
    for t in thrds:
        t.join()
    print('Parallels exit normal')
    #print("result:  ", database_content)
    print(str(sum(datacounter))+" records" + datetime.datetime.now().__str__())
    return str(sum(datacounter))+" records" + datetime.datetime.now().__str__()

#A = myscript()

#sess = pass_ask18()
#article_date('https://www.ptt.cc/bbs/Boy-Girl/M.1527872206.A.357.html',sess)
#comments_in_article('https://www.ptt.cc/bbs/Boy-Girl/M.1527872206.A.357.html',sess)
