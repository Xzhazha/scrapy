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

client = pymongo.MongoClient('localhost', 27017)
db = client['xiaomishangdian']

# file_table = db['fileTable']
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 QIHU 360SE'}
driver = webdriver.Chrome()
driver.maximize_window()


def get_catagory_page(url):  # 爬取各类别url
    html = requests.get(url, headers=headers)
    selector = etree.HTML(html.text)
    hrefs = selector.xpath('/html/body/div[6]/div/div[2]/div[2]/ul/li/a/@href')
    catagory_urls = [url + href for href in hrefs]  # 每个类别url
    catagories = selector.xpath('/html/body/div[6]/div/div[2]/div[2]/ul/li/a/text()')

    #catagory_urls = ['http://app.mi.com/category/6']
    catagory_attrs = []

    for curl in catagory_urls:
        page_attrs=get_page_url(curl)
        catagory_attrs.append(page_attrs)
    attrs=dict(zip(catagories,catagory_attrs))
    return attrs


def get_page_url(curl):
    i = 1
    driver.get(curl)
    driver.implicitly_wait(10)

    # page_html = requests.get(curl, headers=headers)
    # page_selector = etree.HTML(page_html.text)
    # page_hrefs = page_selector.xpath('//*[@id="all-applist"]/li/a/@href')  # 每一页所有app的url
    # page_urls = [url_path + url for url in page_hrefs]

    page_urls=[]
    href_elements=driver.find_elements_by_xpath('//*[@id="all-applist"]/li/a')
    for href in href_elements:
        page_urls.append(href.get_attribute('href'))
    for url in page_urls:
        app_attr = get_info(url)
        page_attrs.append(app_attr)

    time.sleep(1)
    next_page(curl)
    i = i + 1
    print(i)
    return


def next_page(url):
    try:
        driver.find_element_by_class_name('next').click()
        time.sleep(1)
        driver.implicitly_wait(3)
        curl = driver.current_url
        get_page_url(curl)
    except:
        print('错了错了')
        #driver.close()
        #return



def get_info(url):
    # page = page + 1
    try:
        app_html = requests.get(url, headers=headers)  # 进入某一个app的主页
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

        query = {'filename': app_attr['filename']}
        if not table.find_one(query):
            table.insert_one(app_attr)
    except:
        pass

    return app_attr



if __name__ == '__main__':
    url_path = 'http://app.mi.com'
    html = requests.get(url_path, headers=headers)
    selector = etree.HTML(html.text)
    hrefs = selector.xpath('/html/body/div[6]/div/div[2]/div[2]/ul/li/a/@href')
    catagory_urls = [url_path + href for href in hrefs]  # 每个类别url
    catagories = selector.xpath('/html/body/div[6]/div/div[2]/div[2]/ul/li/a/text()')

    # catagory_urls = ['http://app.mi.com/category/6']
    catagory_attrs = []

    for i in range(16):
        table = db[catagories[i]]
        curl=catagory_urls[i]
        page_attrs=[]
        get_page_url(curl)
        catagory_attrs.append(page_attrs)
    attrs = dict(zip(catagories, catagory_attrs))
    driver.close()



    f=open('xiaomi1.json','a')
    f.write(json.dumps(attrs,ensure_ascii=False)) #ensure_ascii=False确保中文字符正确存储
    f.close()

    # f = open("xiaomi1.json", 'r')
    # attr = json.load(f)