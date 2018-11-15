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

###定义数据库IP、端口和数据库名
client = MongoClient('127.0.0.1', 27017)
db = client.douban_book

###指定集合名称
coll = db['book_by_id']

###数据采集主流程
def book_spider(id_begin, id_end):
    #定义Id索引变量 
    id_index = id_begin

    #按照定义好的Id区间进行数据采集
    while(id_index <= id_end):
        url = 'https://book.douban.com/subject/'+str(id_index)
        print('Downloading Information From Book Id: '+str(id_index))
        get_detail_book_info(url)
        id_index += 1

def get_detail_book_info(url):
    #获取url对应的网页数据
    try:
        req = requests.get(url, headers=hds[np.random.randint(0,len(hds))])
        plain_text=req.text   
    except:
        print('someting goes wrong!')
        return

    soup = BeautifulSoup(plain_text,"lxml")

    #获取评价人数
    try:
    	people_num=soup.find('div',{'class':'rating_sum'}).findAll('span')[1].string.strip()
    except:
    	people_num = '0'

    #获取评价分数
    try:
        rating=soup.find('strong',{'class':'ll rating_num '}).string.strip()
        if rating == '':
            rating = '0.0'
    except:
        rating = '0.0'

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
    data_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # return pub_house,pub_year,price,people_num,page_num,isbn

    coll.insert_one({'title':title,'rating':rating,'people_num':people_num,\
        'author_info':author_info,'pub_house':pub_house,'pub_year':pub_year,'price':price,\
        'page_num':page_num,'isbn':isbn,'book_url':url,'img_url':img_url,'data_time':data_time})
    
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
    book_spider(1001137,1010000)
