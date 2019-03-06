# -*- coding: UTF-8 -*-
#!/usr/bin/python3
import time
import random
import requests
from lxml import etree


headers = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36")}

def search(keyWord):
    bookList = []
    response = requests.get('https://sou.xanbhx.com/search?siteid=qula&q=%s'%keyWord,\
    headers = headers)
    html = etree.HTML(response.content.decode())
    liList = html.xpath('//div[@class="search-list"]/ul/li')
    for item in liList:
        try:
            if item.xpath('./span[@class="s1"]/b/text()')[0] == '作品分类':
                continue
        except:
            bookID = item.xpath('./span[@class="s2"]/a/@href')[0].split('/')[-2]  # 作品ID
            bookType = item.xpath('./span[@class="s1"]/text()')[0][1:-1]  # 作品分类
            bookName = item.xpath('./span[@class="s2"]/a/text()')[0]  # 作品名称
            bookName = ''.join(bookName.split())
            bookNewID = item.xpath('./span[@class="s3"]/a/@href')[0].split('/')[-1][:-5]  # 最新章节ID
            bookAuthor = item.xpath('./span[@class="s4"]/text()')[0]  # 作者
            #bookClick = item.xpath('./span[@class="s5"]/text()')[0]  # 点击
            bookUptime = item.xpath('./span[@class="s6"]/text()')[0]  # 更新时间
            bookStatu = item.xpath('./span[@class="s7"]/text()')[0]  # 状态
            #bookList.append([bookID, bookType, bookName, bookNewID, bookAuthor,
            #                 bookClick, bookUptime, bookStatu])
            bookList.append([bookID, bookType, bookName, bookNewID, 
                             bookAuthor, bookUptime, bookStatu])
    @time.sleep(random.randint(1,3))
    return(bookList)

if __name__ == '__main__':
    print(search('灵气'))

