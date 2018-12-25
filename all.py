# -*- coding: UTF-8 -*-
from spider import *
from search import *
import file


if __name__ == '__main__':
    print('Hello world!')
    for i in range(1, 147476):
        spider = Spider(i)
        spider.get_index()
        for item in search(spider.name):
            if item[0] == str(i):
                file.addBookList(item)
                print('状态命中： %s'%item[-1])
                if item[-1] == '完成':
                    status = 0 # 0为完本，1为连载
                else:
                    status = 1
        if status == 0:
            #spider.get_cont()
            pass
    print('Bye world!')