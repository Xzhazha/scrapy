#无法获取第二页的app


from selenium import webdriver
from lxml import etree
import requests
import time
import re
import json
from multiprocessing import Pool
import os
import pymongo
import gridfs

client = pymongo.MongoClient('localhost',27017)
db = client['fileDB']
file_table = db['fileTable']
headers ={
    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 QIHU 360SE'}

def get_page(url): #爬取各类别url
    html = requests.get(url, headers=headers)
    selector = etree.HTML(html.text)
    hrefs = selector.xpath('/html/body/div[6]/div/div[2]/div[2]/ul/li/a/@href')
    urls=[url+ href for href in hrefs]
    catagories=selector.xpath('/html/body/div[6]/div/div[2]/div[2]/ul/li/a/text()')
    #page_num=selector.xpath('//*[@id="all-pagination"]/a/text()')[1:-1] JavaScript 动态网页无法爬取
    return urls

def get_app(url):
    urls=[url + '#page={}'.format(i) for i in range(0,80)]
    app_attrs=[]
    app_urls=[]
    for url_tmp in urls:
        try:
            html = requests.get(url_tmp, headers=headers) #获取某一页所有app的url
            selector = etree.HTML(html.text)
            hrefs = selector.xpath('//*[@id="all-applist"]/li/a/@href')
            app_urls.append([url_path + href for href in hrefs])
            time.sleep(10)
        except ConnectionError:
            print('连接失败')
            pass
    for app_url in app_urls:
        app_html = requests.get(app_url, headers=headers)  # 进入某一个app的主页
        app_selector = etree.HTML(app_html.text)
        download_href = app_selector.xpath('/html/body/div[6]/div[1]/div[2]/div[1]/div/div[2]/a/@href')[0]
        filename = app_selector.xpath('/html/body/div[6]/div[1]/div[2]/div[1]/div/h3/text()')[0]
        star = app_selector.xpath('/html/body/div[6]/div[1]/div[2]/div[1]/div/div[1]/div/@class')[0]
        evaluate_num = app_selector.xpath('/html/body/div[6]/div[1]/div[2]/div[1]/div/span/text()')[0]
        owner = app_selector.xpath('/html/body/div[6]/div[1]/div[2]/div[1]/div/p[1]/text()')[0]
        size = app_selector.xpath('/html/body/div[6]/div[1]/div[2]/div[2]/div/ul[1]/li[2]/text()')[0]
        version = app_selector.xpath('/html/body/div[6]/div[1]/div[2]/div[2]/div/ul[1]/li[4]/text()')[0]
        update_time = app_selector.xpath('/html/body/div[6]/div[1]/div[2]/div[2]/div/ul[1]/li[6]/text()')[0]
        package_name = app_selector.xpath('/html/body/div[6]/div[1]/div[2]/div[2]/div/ul[1]/li[8]/text()')[0]
        appid = app_selector.xpath('/html/body/div[6]/div[1]/div[2]/div[2]/div/ul[1]/li[10]/text()')[0]
        download_url = url_path + download_href
        app_attr = {'download_url': download_url, 'filename': filename, 'star': star, 'evaluate_num': evaluate_num,
                    'owner': owner, 'size': size, 'version': version, 'update_time': update_time,
                    'package_name': package_name, 'appid': appid}
        app_attrs.append(app_attr)
    return app_attrs

def store2mongo(app_attrs):#将mongodb中数据存入文件系统
    count=0
    fs = gridfs.GridFS(db, 'fileTable')
    for item in app_attrs:
        bdata = requests.get(item['download_url'],headers=headers)
        fs.put(bdata.content,item) #存入mongodb
        count += 1
        print('已经下载', count, '张图片')



# def get_pic_urls(url_path,num,content):
#     urls = [url_path + content + '/?page={}'.format(i) for i in range(1,num)]
#     urlList = []
#     for url in urls:
#         html = requests.get(url,headers=headers)
#         selector = etree.HTML(html.text)
#
#         imgs = soup.select('article > a > img')
#         if imgs==[]:
#             pass
#         else:
#             for img in imgs:
#                 photoUrl = img.get('src')
#                 urlList.append(photoUrl)
#     return urlList


def mongo2disk(path):
    if os.path.exists(path): #创建磁盘存储路径
        pass
    else:
        os.makedirs(path)
    fs = gridfs.GridFS(db, 'fileTable')
    i = 0
    for file in fs.find():
        bdata = file.read()
        filename=fs.list()[i]
        fp = open(path +filename , 'wb')
        i = i + 1
        fp.write(bdata)
        fp.close()


def store2mongo(urlList):#将mongodb中数据存入文件系统
    count=0
    fs = gridfs.GridFS(db, 'fileTable')
    for item in urlList:
        filename=str(item.split('?')[0][-10:])
        query = {'filename': filename}
        if fs.exists(query):
            print('已经存在该文件')
        else:

            data = requests.get(item.split('?')[0],headers=headers)
            fs.put(data.content,filename=filename) #存入mongodb
            count += 1
            print('已经下载', count, '张图片')

if __name__=='__main__':
    url_path = 'http://app.mi.com'
    urls=get_page(url_path)
    app_attrs=get_app(urls[1])
    store2mongo(app_attrs)
    # path = 'f://photo//' + content + '/' #图片存储入磁盘路径
    # urlList=get_pic_urls(url_path,num,content)
    # store2mongo(urlList)
    # mongo2disk(path)