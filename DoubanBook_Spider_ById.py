#!/usr/bin
#-*- coding: UTF-8 -*-
#按book_id采集书籍信息

import requests
import re
import time
import numpy as np
from bs4 import BeautifulSoup
from openpyxl import Workbook
from pymongo import MongoClient

#备选Agents
hds=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
{'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},\
{'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}]

#代理IP
proxies = {
  "https": "27.17.45.90:43411",
  "https": "101.236.50.94:8866",
  "https": "123.7.61.8:53281",
  "https": "61.135.217.7:80",
  "https": "218.24.16.19:43620"
}

###定义数据库IP、端口和数据库名
client = MongoClient('127.0.0.1', 27017)
db = client.douban_book

###指定集合名称
coll_book_by_id = db['book_by_id']
coll_knnlike_book = db['knnlike_book']

###数据采集主流程
def book_spider(id_begin, id_end):
    #定义Id索引变量 
    id_index = id_begin

    #按照定义好的Id区间进行数据采集
    while(id_index <= id_end):
        #拼接图书url
        url = 'https://book.douban.com/subject/'+str(id_index)
        #打印日志
        print('Downloading Information From Book Id: '+str(id_index))
        #设置随机的采集间隔时间
        time.sleep(np.random.rand()*5)
        #获取图书信息，如果IP被禁，则退出采集
        if get_detail_book_info(url) == 1:
            break

        id_index += 1

def get_detail_book_info(url):
    #使用代理，获取url对应网页的数据
    try:
        req = requests.get(url, headers=hds[np.random.randint(0,len(hds))], proxies = proxies)
        plain_text=req.text
    except(OSError, TypeError) as reason:
        print('错误的原因是:', str(reason))
        return 0

    #如果返回报文中提示检测到异常请求，则退出采集，并打印返回报文
    if re.search('检测到有异常请求',plain_text) is not None:
        print(plain_text)
        return 1

    soup = BeautifulSoup(plain_text,"lxml")

    #获取评价人数
    try:
    	people_num=int(soup.find('div',{'class':'rating_sum'}).findAll('span')[1].string.strip())
    except:
    	people_num = 0

    #获取评价分数
    try:
        rating=soup.find('strong',{'class':'ll rating_num '}).string.strip()
        if rating == '':
            rating = 0.0
        else:
            rating = float(rating)
    except:
        rating = 0.0

    #获取图片链接
    try:
        img_url=soup.find('img').get('src').strip()
    except:
        img_url = ''

    #书名
    try:
        title=soup.find('h1').find('span').string.strip()
    except:
        title = ''

    #获取标签信息
    try:
        tagListStr = ''
        for tag in soup.find('div', id='db-tags-section').find('div').find_all('span'):
            tagListStr = tagListStr+'#'+tag.find('a').string.strip()
    except:
        tagListStr = ''

    #测试
    print(tagListStr)

    #获取也喜欢信息
    try:
        if soup.find('div', id='db-rec-section') is not None:
            for knnlike_book in soup.find('div', id='db-rec-section').find('div').find_all('dl'):
                if knnlike_book.dd is not None:
                    # print(type(knnlike_book))
                    knnlike_book_url = knnlike_book.find('dd').find('a').get('href')
                    knnlike_book_name = knnlike_book.find('dd').find('a').string.strip()
                
                    #测试
                    # print(knnlike_book_url+'###'+knnlike_book_name)
                    coll_knnlike_book.insert_one({'book_url':url,'knnlike_book_url':knnlike_book_url,\
                                                'knnlike_book_name':knnlike_book_name,\
                                                'data_time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
    except(OSError, TypeError) as reason:
        print('错误的原因是:', str(reason))
        print('no knnlike book!')

    #获取info节点
    detail_book_info = soup.find('div',{'id':'info'})
    
    #通过字符串搜索含有"ISBN"的tag,通过next_sibling查询兄弟节点
    try:    
    	isbn = detail_book_info.find('span',string=re.compile('ISBN')).next_sibling.string.strip()
    except:
    	isbn = 'null'

    #通过字符串搜索含有"页数"的tag,通过next_sibling查询兄弟节点
    try:
    	page_num = detail_book_info.find('span',string=re.compile('页数')).next_sibling.string.strip()
    except:
    	page_num = 'null'

    #通过字符串搜索含有"出版社"的tag,通过next_sibling查询兄弟节点
    try:
    	pub_house = detail_book_info.find('span',string=re.compile('出版社')).next_sibling.string.strip()
    except:
    	pub_house = 'null'

	#通过字符串搜索含有"出版年"的tag,通过next_sibling查询兄弟节点
    try:
    	pub_year = detail_book_info.find('span',string=re.compile('出版年')).next_sibling.string.strip()
    except:
    	pub_year = 'null'

    #通过字符串搜索含有"定价"的tag,通过next_sibling查询兄弟节点
    try:
    	price = detail_book_info.find('span',string=re.compile('定价')).next_sibling.string.strip()
    except:
    	price = 'null'

    #通过字符串搜索含有"作者"的tag,通过next_sibling查询兄弟节点
    try:
        author_info = detail_book_info.find('span',string=re.compile('作者')).next_sibling.next_sibling.string.strip()
    except:
        author_info = '暂无'

    #获取采集时间戳
    # data_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # return pub_house,pub_year,price,people_num,page_num,isbn

    coll_book_by_id.insert_one({'title':title,'rating':rating,'people_num':people_num,\
        'author_info':author_info,'pub_house':pub_house,'pub_year':pub_year,'price':price,\
        'page_num':page_num,'tag':tagListStr,'isbn':isbn,\
        'book_url':url,'img_url':img_url,'data_time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
    
    #测试
    # print(title)
    # print(people_num)
    # print(rating)
    # print(img_url)
    # print(isbn)
    # print(page_num)
    # print(pub_house)
    # print(pub_year)
    # print(price)
    # print(author_info)
    # print(data_time)

if __name__=='__main__':
    #设置采集的book_id范围
    book_spider(1000001,1003000)
