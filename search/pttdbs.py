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
from datetime import timedelta

from hashlib import md5

from django.db import transaction


from .models import Ptt
from .models import Querywho
import sqlite3
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
    #print(dt,type(dt))
    return dt


#https://www.ptt.cc/bbs/Gossiping/index.html => [https://www.ptt.cc/bbs/Gossiping/M.1521999297.A.04F.html, ...]
def get_article_inpage(url,sess,time_diff):
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
    bound_date = datetime.datetime.now()
    for i in range(len(Q)):
        try:
            last_date = article_date(ptturl+Q[i],sess)
        except:
            continue
        #print(last_date, Q[i], bound_date + time_diff )
        if type(last_date) != type(bound_date):
            print(urls)
            continue
        if last_date < bound_date + time_diff:
            continue
        else:
            urls.append(Q[i])
        #print(article_date(ptturl+x,sess))

    return urls

database_content = []
datacounter = []
#這是為了數更新了幾筆資料


#一次更新一批資料
#def bulk_update(BUF, lock):
def write_db():
    fnames = os.listdir()
    comments = []
    for fname in fnames:
        if 'thread' in fname:
            print(fname)
            with open(fname,'r') as f:
                x = f.readlines()
                i=0
                while i <  len(x) :
                    comments.append( (x[i][:-1],x[i+1][:-1],x[i+2][:-1],x[i+3][:-1],x[i+4][:-1]) )
                    i+=5
                    if( i % (len(x)/100) == 0):
                        print('#', end='')
                f.close()

    print("total number of comments ", len(comments))
    connect = sqlite3.connect("db.sqlite3")
    con = connect.cursor()
    con.executemany("INSERT OR IGNORE into search_ptt(hash, ID, content, time, link) values (?,?,?,?,?)", comments)
    connect.commit()
    connect.close()

def partition(a,b,post,lock,sess,threadnum):
    BUF = []

    for c in range(a,b):
        #print(ptturl+post[c])
        try:
            A = comments_in_article(ptturl+post[c],sess)
        except:
            continue
        BUF.extend(A)

    with open(str(threadnum) + ".temp-thread", 'w') as f:
        for Q in BUF:
            for key in Q.keys():
                if Q[key] == None:
                    Q[key] = "[maybe it is a picture]"
            hash=Q['hash']
            ID=Q['ID']
            content = Q['content']
            time = Q['time']
            link = Q['link']

            for x in [hash,ID,content,time,link]:
                f.write(x.__str__().replace('\n','')+"\n")
        f.close()




def myscript(time_diff):
    #boards = dfs_find_allboard()
    print(os.listdir())
    datacounter.clear()
    bound_date = datetime.datetime.now()
    #time_diff = datetime.timedelta(hours = -3)

    #boards = ['WomenTalk']

    boards = ['Gossiping', 'NBA', 'sex', 'C_Chat', 'Baseball', 'WomenTalk', 'Stock', 'marriage', 'BabyMother', 'LoL', 'movie', 'Boy-Girl', 'Beauty', 'marvel', 'MobileComm', 'car', 'ToS', 'joke', 'Lifeismoney', 'AllTogether', 'Tech_Job', 'Hearthstone', 'e-shopping', 'Japandrama', 'HatePolitics', 'Japan_Travel', 'ONE_PIECE', 'PC_Shopping', 'PlayStation', 'KR_Entertain', 'MakeUp', 'Tennis', 'SportLottery', 'home-sale', 'Tainan', 'Kaohsiung', 'Steam', 'NY-Yankees', 'KoreaDrama', 'japanavgirls', 'iOS', 'KoreaStar', 'MLB', 'TaichungBun', 'BuyTogether', 'creditcard', 'StupidClown', 'EAseries', 'BeautySalon', 'NSwitch', 'PokemonGO', 'Monkeys', 'Palmar_Drama', 'HardwareSale', 'Hsinchu', 'CFantasy', 'OverWatch', 'YuanChuang', 'MH', 'KanColle', 'Wanted', 'Salary', 'WOW', 'MuscleBeach', 'FATE_GO', 'TaiwanDrama', 'AC_In', 'FITNESS', 'PuzzleDragon', 'TypeMoon', 'PathofExile', 'TY_Research', 'WorldCup', 'Examination', 'Elephants', 'Food', 'LGBT_SEX', 'Headphone', 'Aviation', 'Guardians', 'basketballTW', 'feminine_sex', 'TWICE', 'TW_Entertain', 'mobilesales', 'CN_Entertain', 'CVS', 'cat', 'Lions', 'lesbian', 'give', 'fastfood', 'NBA_Film', 'GetMarry', 'biker', 'CarShop', 'studyteacher', 'medstudent', 'StarCraft', 'BabyProducts', 'facelift', 'ALLPOST', 'DSLR', 'Soft_Job', 'BTS', 'cookclub', 'Lineage', 'Zastrology', 'PUBG', 'nb-shopping', 'points', 'MayDay', 'AKB48', 'CATCH', 'Brand', 'EuropeTravel', 'BB-Love', 'GirlsFront', 'RealmOfValor', 'AzurLane', 'Gamesale', 'Finance', 'E-appliance', 'China-Drama', 'ShuangHe', 'part-time', 'Gemini', 'Suckcomic']
    sess = 0
    sess = pass_ask18()

    url = 'https://www.ptt.cc/bbs/{boardname}/index{pagenum}.html'

    urls = []
    for x in boards:
        try:
            page_num = get_board_nowindex(url.format(boardname = x, pagenum='' ),sess)
        except:
            pass
        print(page_num)
        c = -1
        while 1:
            A = get_article_inpage(url.format(boardname = x,pagenum = page_num - c ), sess,time_diff)
            print(" len A: " , len(A))
            urls.extend(A)
            if(len(A)==0):
                break
            c+=1
            '''
            try:
                A = get_article_inpage(url.format(boardname = x,pagenum = page_num - c ), sess,time_diff)
                urls.extend(A)
                print(c)
                c+=1
            except:
                break
            '''
    #print("urls ",urls)
    thread_num = 8 #線程數
    pa = time.time()
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
    pb = time.time()
    print(' time: ', pb-pa)

    pa = time.time()

    write_db()
    pb = time.time()
    print(' time: ', pb-pa)

    #print("result:  ", database_content)
    print(str(sum(datacounter))+" records" + datetime.datetime.now().__str__())
    return str(sum(datacounter))+" records" + datetime.datetime.now().__str__()


#A = myscript()
#sess = pass_ask18()
#article_date('https://www.ptt.cc/bbs/Boy-Girl/M.1527872206.A.357.html',sess)
#comments_in_article('https://www.ptt.cc/bbs/Boy-Girl/M.1527872206.A.357.html',sess)


if __name__ == '__main__':
    A = myscript( timedelta(hours=-2) )
