# -*- coding: UTF-8 -*-
import requests
from lxml import etree


headers = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36")}

def search(keyWord):
    book = []
    response = requests.get('https://sou.xanbhx.com/search?siteid=qula&q=%s'%keyWord,\
    headers = self.headers)
    html = etree.HTML(response.content.decode())
    liList = html.xpath('//div[@class="search-list"]/ul/li')
    for item in liList:
        if item.xpath('./span[@calss="s1"]/b/text()')[0] == '作品分类'：
            continue
        bookType = ('./span[@calss="s1"]/text()')[0]
        bookType = ('./span[@calss="s1"]/text()')[0]
    
    


if __name__ == '__main__':
    while True:
        ttt = input('test:')
        print(ttt == '1')
    
    