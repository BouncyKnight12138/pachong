#https://www.qu.la
import requests
from lxml import etree
import os, re, time, random


class Spider(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}
    def get_url(self):
        url = input("输入书籍目录url")
        typ = input("输入类型，1为单文件，2为多文件")
        self.start_request(url, typ)

    def start_request(self, url, typ):
        change = int(typ)
        try:
            response = requests.get(url, headers=self.headers)
        except Exception as e:
            print(e)
            return
        html = etree.HTML(response.content.decode())
        bigtit_list = html.xpath('//div[@class="box_con"]/div/dl/dd/a/text()')
        bigsrc_list = html.xpath('//div[@class="box_con"]/div/dl/dd/a/@href')
        big_title = html.xpath('//div[@id="info"]/h1/text()')
        big_url = url.rsplit("/")[2]
        if change == 1:
            for bigsrc, bigtit in zip(bigsrc_list, bigtit_list):
                self.finally_file_a(bigtit, bigsrc,big_title, big_url)
                time.sleep(random.randint(2, 5))
                #print(bigsrc)
        elif change == 2:
            for bigsrc, bigtit in zip(bigsrc_list, bigtit_list):
                self.finally_file_m(bigtit, bigsrc, big_url)
                time.sleep(random.randint(2, 5))
                #print(bigsrc)

    def finally_file_m(self, tit, url, big_url):
        try:
            response = requests.get("https://"+ big_url+url, headers=self.headers)
        except Exception as e:
            print(e)
            return
        html = etree.HTML(response.content.decode())
        text_list = html.xpath('//div[@id="content"]/text()')
        text = "\n".join(text_list)
        file_name = re.sub(r'[\/:*?"<>|]', '', "小说\\" + tit + ".txt")
        print("爬取文章" + file_name)
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(text)

    def finally_file_a(self, tit, url,big_title, big_url):
        try:
            response = requests.get("https://"+ big_url+ url, headers=self.headers)
        except Exception as e:
            print(e)
            return
        html = etree.HTML(response.content.decode())
        text_list = html.xpath('//div[@id="content"]/text()')
        text = "\n".join(text_list)
        big_tit = big_title[0]
        file_big_name ="小说\\" +big_tit +".txt"
        file_name = re.sub(r'[\/:*?"<>|]', '',  tit)
        print("爬取文章" + file_name)
        with open(file_big_name,"a", encoding="utf-8") as f:
            f.write(file_name)
            f.write(text)


if __name__ == '__main__':
    if os.path.exists("小说") == False:
        os.mkdir("小说")
    spider = Spider()
    spider.get_url()
    print("完成啦")
