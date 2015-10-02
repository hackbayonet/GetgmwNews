# -*- coding: utf-8 -*-
# python 2.7.10

import urllib2
import re
import time
import thread

# 初始化 headers
user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
headers = {'User_agent':user_agent}
# 初始化索引Url存放地址
IndexUrls = []
# 初始化新闻url存放地址
NewUrls = []
# 获取当前年月日
currenttime = time.strftime('%Y-%m-%d', time.localtime())
# 初始化文件存放地址
file = open(currenttime + '.txt', 'w')
# 初始化全站新闻
urls = [
        ['http://guancha.gmw.cn/node_10056.htm', 'http://guancha.gmw.cn/'],
        ['http://world.gmw.cn/node_24177.htm', 'http://world.gmw.cn/'], 
        ['http://politics.gmw.cn/node_9840.htm', 'http://politics.gmw.cn/'], 
        ['http://politics.gmw.cn/node_9844.htm', 'http://politics.gmw.cn/'],
        ['http://culture.gmw.cn/node_10570.htm', 'http://culture.gmw.cn/'], 
        ['http://tech.gmw.cn/node_4360.htm', 'http://tech.gmw.cn/'],
        ['http://edu.gmw.cn/node_10602.htm', 'http://edu.gmw.cn/'], 
        ['http://economy.gmw.cn/node_12470.htm', 'http://economy.gmw.cn/'],
        ['http://life.gmw.cn/node_9269.htm', 'http://life.gmw.cn/'], 
        ['http://legal.gmw.cn/node_9020.htm', 'http://legal.gmw.cn/'],
        ['http://mil.gmw.cn/node_8986.htm', 'http://mil.gmw.cn/'], 
        ['http://health.gmw.cn/node_9583.htm', 'http://health.gmw.cn/'],
        ['http://yangsheng.gmw.cn/node_12215.htm', 'http://yangsheng.gmw.cn/'], 
        ['http://lady.gmw.cn/node_33669.htm', 'http://lady.gmw.cn/'],
        ['http://e.gmw.cn/node_8755.htm', 'http://e.gmw.cn/']
       ]

#去除img标签,1-7位空格,
removeImg = re.compile('<img.*?>| {1,7}| ')
#删除超链接标签
removeAddr = re.compile('<a.*?>|</a>')
#把换行的标签换为\n
replaceLine = re.compile('<tr>|<div>|</div>|</p>')
#将表格制表<td>替换为\t
replaceTD= re.compile('<td>')
#将换行符或双换行符替换为\n
replaceBR = re.compile('<br><br>|<br>')
#将其余标签剔除
removeExtraTag = re.compile('<.*?>')
#将多行空行删除
removeNoneLine = re.compile('\n+')
def replace(x):
    #删除多余内容
    x = re.sub(removeImg,'',x)
    x = re.sub(removeAddr,'',x)
    x = re.sub(replaceLine,'\n',x)
    x = re.sub(replaceTD,'\t',x)
    x = re.sub(replaceBR,'\n',x)
    x = re.sub(removeExtraTag,'',x)
    x = re.sub(removeNoneLine,'\n',x)
    #strip()将前后多余内容删除
    return x.strip()

def GetHtml(url):
    ''' 获取url地址的HTML并返回 '''
    try:
        request = urllib2.Request(url, headers=headers)
        html = urllib2.urlopen(request)
        return html.read()
    except urllib2.HTTPError, e:
        # 处理 4xx 
        if hasattr(e, 'code'):
            print e.code
            return None


def GetIndexUrls(html):
    ''' 获取光明网国际消息所有新闻Url '''
    del IndexUrls[:]
    indexurls = re.findall('<li><a href="(.*?)">(.*?)</a></li>', html, re.S)
    for indexurl in indexurls:
        if not re.search('http://', indexurl[0], re.S):
            if not re.search('target=', indexurl[0], re.S):
                print indexurl[0], indexurl[1].decode('utf-8').encode('gbk')
                IndexUrls.append([indexurl[0], indexurl[1].decode('utf-8').encode('gbk')]) 


def GetNewUrls(html, url):
    ''' 获取新闻具体Urls地址 '''
    newurls = re.findall('<li><a href=(.*?) target=_blank>.*?</a><span class="channel-newsTime">(.*?)</span>', html, re.S)
    for newurl in newurls:
        if not re.search('http', newurl[0], re.S):
            if not re.search('node', newurl[0], re.S):
                NewUrls.append([url,newurl[0],newurl[1]])



import threading
lock = threading.Lock()
def GetNews(url):
    ''' 获取新闻内容 '''
    html = GetHtml(url)
    news = re.findall('<!--enpcontent-->(.*?)<!--/enpcontent-->',html, re.S)
    # 调用acquire([timeout])时，线程将一直阻塞，
    # 直到获得锁定或者直到timeout秒后（timeout参数可选）。
    # 返回是否获得锁。
    if lock.acquire():
        print newurl[0] + newurl[1]
        file.write(replace(news[0]))
        # 调用release()将释放锁。
        lock.release()

if __name__ == '__main__':
    for url in urls:
        html = GetHtml(url[0])
        if not html:
            print u'获取HTML失败!'
            continue
        GetIndexUrls(html)
        for indexurl in IndexUrls:
            html = GetHtml(url[1] + indexurl[0])
            if not html:
                print u'获取HTML失败!'
                continue
            GetNewUrls(html, url[1])
    threads = []
    for newurl in NewUrls:
        if newurl[2] == currenttime:
            url = newurl[0] + newurl[1]
            t1 = threading.Thread(target=GetNews,args=(url,))
            threads.append(t1)

    for th in threads:
        th.start()

    for th in threads:
        th.join()

    file.close()
    print "OK"