# -*- coding: UTF-8 -*-
import requests
import time
import random
from lxml import etree
import file


class Spider(object):

    headers = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36")}
    max_try_count = 3  # 请求失败时最大尝试次数

    def __init__(self, id):
        self.id = id
        self.index_url = 'https://www.qu.la/book/%s/'%self.id
        self.name = ''  # 书名
        self.index_name = []  # 卷名列表
        self.index_cont_name = []  # 章名列表，列表
        self.index_cont_id = []  # 章id, 假设该值不变动
        self.do_index_name = []  # 待抓取卷名列表
        self.do_index_cont_name = []  # 待抓取章名列表，列表
        self.do_index_cont_id = []  # 待抓取章id

    def retry(self):
        '''请求失败处理'''
        pass

    def get_index(self):
        '''获取小说目录列表'''
        # 抓取index页
        try:
            response = requests.get(self.index_url, headers = self.headers)
            # 处理获得index
            html = etree.HTML(response.content.decode())
            html_list = html.xpath('//div[@class="box_con"]/div/dl/*')
            self.name = html.xpath('//div[@id="info"]/h1/text()')[0]
            print('ID %s , NAME %s , Index抓取完毕'%(self.id, self.name))
            time.sleep(1)
            # 建立卷章列表
            for item in html_list:
                if item.xpath('./text()')[0] != ' ':
                    # 若子节点为卷
                    if '最新章节' in item.xpath('./text()')[0]:
                        # 跳过"最新章节"卷
                        pass
                    else:
                        # 创建改卷列表
                        self.index_name.append(item.xpath('./text()')[0])
                        self.index_cont_name.append([])
                        self.index_cont_id.append([])
                else:
                    # 子节点为章
                    try:
                        self.index_cont_name[-1].append(item.xpath('./a/text()')[0])
                        self.index_cont_id[-1].append(item.xpath('./a/@href')[0].split('/')[-1][:-5])
                    except:
                        # 最新章节卷下章会抛出异常，无妨
                        continue
            print('Index分析完成, %s卷 , %s章'%(len(self.index_name), len(html_list)-len(self.index_name)))
            file.saveIndex('%s_%s'%(str(self.id).zfill(7), self.name), 'index_name', self.index_name)
            file.saveIndex('%s_%s'%(str(self.id).zfill(7), self.name), 'index_cont_id', self.index_cont_id)
            file.saveIndex('%s_%s'%(str(self.id).zfill(7), self.name), 'index_cont_name', self.index_cont_name)
            time.sleep(random.randint(1, 3))
        except Exception as e:
            print(e)
            return self.retry()

    def get_cont(self):
        '''抓取章节内容'''
        # 确认要抓取的章列表
        (self.do_index_name, self.do_index_cont_name, self.do_index_cont_id) = file.check\
        (self.id, self.index_name, self.index_cont_name, self.index_cont_id)
        print('Index本地比对完成,开始抓取章内容')
        # 开始抓取吧
        for i in range(0, len(self.do_index_name)):
            for j in range(0, len(self.do_index_cont_name[i])):
                try_count = 0
                while try_count <= self.max_try_count:
                    try:
                        response = requests.get("https://www.qu.la/book/%s/%s.html"\
                        %(self.id, self.do_index_cont_id[i][j]), headers = self.headers)
                        html = etree.HTML(response.content.decode())
                        text_list = html.xpath('//div[@id="content"]/text()')
                        text = "\n".join(text_list)
                        # 很重要，清洗\u3000\xa0等
                        text = "\n".join(text.split())
                        # 保存该章
                        file.saveFile('%s_%s'%(str(self.id).zfill(7), self.name), '%s_%s'%(str(i).zfill(2), self.do_index_name[i]), \
                        '%s_%s'%(str(j).zfill(5), self.do_index_cont_name[i][j]), text)
                        print('已保存  %s'%self.do_index_cont_name[i][j])
                        break
                    except Exception as e:
                        print(e)
                        try_count += 1
                        time.sleep(random.randint(30, 60))
                time.sleep(random.randint(1, 3))

if __name__ == '__main__':
    pass
