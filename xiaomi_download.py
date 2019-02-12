from multiprocessing import Pool
import os
import json
import pymongo
import gridfs
import requests

client = pymongo.MongoClient('localhost', 27017)
db = client['xiaomishangdian']
path = 'f:/scrapyDownload/androidAPK/'   # 图片存储入磁盘路径


header = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 QIHU 360SE'}

def download(catagory):
    table=db[catagory]
    i=1
    for attr in table.find():
        filename=attr['filename']
        down_url=attr['download_url']
        apkPath=path+catagory+'/'
        if os.path.exists(apkPath):  # 创建磁盘存储路径
            pass
        else:
            os.makedirs(apkPath)

        if os.path.exists(apkPath+filename+'.apk'):  # 创建磁盘存储路径
            print('已经存在',filename+'.apk')
            pass
        else:
            data = requests.get(down_url, headers=header)
            fp=open(apkPath+filename+'.apk','wb')
            fp.write(data.content)
            fp.close()
        i=i+1
        print('第',i,'个','已下载'+filename)
    print(catagory+'栏目下载完毕')

if __name__ == '__main__':



    catagories=['游戏', '实用工具', '影音视听', '聊天社交', '图书阅读', '学习教育', '效率办公', '时尚购物', '居家生活', '旅行交通', '摄影摄像', '医疗健康',
                    '体育运动', '新闻资讯', '娱乐消遣', '金融理财']

    # for catagory in catagories:
    #     download(catagory)
    pool = Pool(processes=4)
    pool.map(download, catagories)





            # if fs.exists(query):

