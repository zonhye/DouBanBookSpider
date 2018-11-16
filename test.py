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
  "https": "https://180.118.243.187:61234",
  # "https": "http://59.110.1.27:8118",
  # "https": "http://113.108.242.36:47713",
  # "https": "http://27.17.45.90:43411"
}

try:
	url = 'https://book.douban.com/subject/1001503'
	req = requests.get(url, headers=hds[np.random.randint(0,len(hds))], proxies = proxies)
	print(req.text)
except:
    print('someting goes wrong!')
