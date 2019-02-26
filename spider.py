# -*- coding: UTF-8 -*-
#!/usr/bin/env python3
import datetime
import random
import time
import threading
import requests
from lxml import etree
import file


class Spider(object):

    headers = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"), 'Connection':'close'}
    max_try_count = 3  # 请求失败时最大尝试次数

    def __init__(self, id):
        self.id = id
        self.author = ''
        self.category = ''
        self.name = ''
        self.status = ''
        self.lastChapterTime = ''
        self.lastChapterName = ''
        self.lastChapterId = ''
        self.description = ''
        self.index = False  # 是否抓取index
        self.local = False  # 是否已抓取过小说内容
        self.index_count = -1  # 总章数
        self.index_url = 'https://www.qu.la/book/%s/'%self.id
        self.index_name = []  # 卷名列表
        self.index_cont_name = []  # 章名列表，列表
        self.index_cont_id = []  # 章id, 假设该值不变动
        self.do_index_name = []  # 待抓取卷名列表
        self.do_index_cont_name = []  # 待抓取章名列表，列表
        self.do_index_cont_id = []  # 待抓取章id

    def get_index(self, proxy=False):
        '''获取小说目录列表'''
        # 抓取index页
        try:
            if proxy == False:
                response = requests.get(self.index_url, headers=self.headers, timeout=6)
            else:
                response = requests.get(self.index_url, headers=self.headers, timeout=6, proxies=proxy[0])
            # 处理获得indexInfo
            html = etree.HTML(response.content.decode())
            # basic info
            self.author = html.xpath('//meta[@property="og:novel:author"]/@content')[0]
            self.category = html.xpath('//meta[@property="og:novel:category"]/@content')[0]
            self.name = html.xpath('//meta[@property="og:novel:book_name"]/@content')[0]
            self.status = html.xpath('//meta[@property="og:novel:status"]/@content')[0]
            self.lastChapterTime = html.xpath('//meta[@property="og:novel:update_time"]/@content')[0].split(' ')[0]
            try:
                self.lastChapterTime = datetime.datetime.strptime(self.lastChapterTime, "%m/%d/%Y").date()
            except:
                self.lastChapterTime = datetime.date(2017, 4, 29)
            self.lastChapterName = html.xpath('//meta[@property="og:novel:latest_chapter_name"]/@content')[0]
            self.lastChapterId = html.xpath('//meta[@property="og:novel:latest_chapter_url"]/@content')[0].split('/')[-1][:-5]
            self.description = html.xpath('//meta[@property="og:description"]/@content')[0]
            self.description = self.description.replace('<br>','')
            self.description = self.description.replace('<br/>','')
            self.description = self.description.replace('</br>','')
            self.description = self.description.replace('<br\>','')
            self.description = self.description.replace('\br','')
            self.description = "\n".join(self.description.split())
            # 建立卷章列表
            html_list = html.xpath('//div[@class="box_con"]/div/dl/*')
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
                        self.index_cont_name[-1].append(item.xpath('./a/text()')[0][:20])  # 此处[:20]为防止文件名过长，来源5883某章
                        self.index_cont_id[-1].append(item.xpath('./a/@href')[0].split('/')[-1][:-5])
                    except:
                        # 最新章节卷下章会抛出异常，无妨
                        continue
            print('ID %s , %s, NAME %s , Index分析完成, %s卷 , %s章'%(self.id, self.lastChapterTime, self.name, 
                                                                      len(self.index_name), len(html_list)-len(self.index_name)))
            #将index保存至本地
            file.saveIndex('%s_%s'%(str(self.id).zfill(7), self.name), 'index_name', self.index_name)
            file.saveIndex('%s_%s'%(str(self.id).zfill(7), self.name), 'index_cont_id', self.index_cont_id)
            file.saveIndex('%s_%s'%(str(self.id).zfill(7), self.name), 'index_cont_name', self.index_cont_name)
            self.index = True
            #尝试解析index数据
            try:
                index_name, index_cont_name, index_cont_id = file.getLocalIndex(self.id, self.name)
                self.index_count = 0
                for i in range(0,len(index_name)):
                    self.index_count += len(index_cont_id[i])
            except:
                self.index_count = -1
        except requests.exceptions.ProxyError:
            try:
                self.get_index(proxy=False)
            except:
                proxy[1] = False
                return(proxy)
            else:
                return(proxy)
        except Exception as e:
            raise(e)
        else:
            if proxy:
                return(proxy)

    def get_index_local(self):
        '''读取本地的index文件及数据库信息'''
        try:
            #读取数据库信息
            item = file.idSearch(self.id)
            self.author = item[3]
            self.category = item[1]
            self.name = item[2]
            self.status = item[4]
            self.local = item[5]
            self.lastChapterTime = item[10]
            self.lastChapterName = item[9]
            self.lastChapterId = item[8]
            self.description = item[7]
            self.index_count = item[6]
            #解析index数据
            self.index_name, self.index_cont_name, self.index_cont_id = file.getLocalIndex(self.id, self.name)
            self.index = True
        except Exception as e:
            raise(e)

    def get_cont(self, thread_number):
        '''抓取章节内容'''
        # 确认要抓取的章列表
        if self.index == False:
            raise(RuntimeError('Index Not Found'))
        (self.do_index_name, self.do_index_cont_name, self.do_index_cont_id) = file.check(
         self.id, self.name, self.index_name, self.index_cont_name, self.index_cont_id)
        print('Index本地比对完成,开始抓取章内容')
        # 开始抓取吧
        # 生成待抓取池
        pool = []
        pool_lock = threading.Lock()
        for i in range(0, len(self.do_index_name)):
            for j in range(0, len(self.do_index_cont_name[i])):
                pool.append([self.id, self.do_index_cont_id[i][j], 
                             '%s_%s'%(str(self.id).zfill(7), self.name),
                             '%s_%s'%(str(i).zfill(2), self.do_index_name[i]), 
                             '%s_%s'%(str(j).zfill(5), self.do_index_cont_name[i][j])])
        
        class ContSpider(threading.Thread):
            def __init__(self, tid):
                threading.Thread.__init__(self)
                self.id = tid
                self.headers = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"), 'Connection':'close'}
                self.proxies = {'http': 'socks5://127.0.0.1:1080', 'https': 'socks5://127.0.0.1:1080'}
            
            def run(self):
                nonlocal pool, pool_lock
                while pool != []:
                    try:
                        pool_lock.acquire()
                        item = pool.pop(0)
                        pool_lock.release()
                        #response = requests.get("https://www.qu.la/book/%s/%s.html"%(item[0], item[1]), headers=self.headers, proxies=self.proxies, timeout=3)
                        response = requests.get("https://www.qu.la/book/%s/%s.html"%(item[0], item[1]), headers=self.headers, timeout=4)
                        html = etree.HTML(response.content.decode())
                        text_list = html.xpath('//div[@id="content"]/text()')
                        text = "\n".join(text_list)
                        # 很重要，清洗\u3000\xa0等
                        text = "\n".join(text.split())
                        # 保存该章
                        file.saveFile(item[2], item[3], item[4], text)
                        print('已保存  %s_%s'%(len(pool), item))
                    except AttributeError:
                        #返回的是空页面，笔趣阁问题？
                        print('PAGE Thread_%s ERR: EMPTY PAGE, PASS '%self.id)
                    except Exception as e:
                        pool_lock.acquire()
                        item = pool.append(item)
                        pool_lock.release()
                        print('PAGE Thread_%s : %s'%(self.id, e))
                        #time.sleep(30)
        
        for i in range(0,thread_number):
            locals()['Thread_%s'%i] = ContSpider(i)
        print('start threads.')
        for i in range(0,thread_number):
            locals()['Thread_%s'%i].start()
        for i in range(0,thread_number):
            locals()['Thread_%s'%i].join()     


if __name__ == '__main__':
    pass
    
