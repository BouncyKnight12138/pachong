# -*- coding: UTF-8 -*-
from spider import *


if __name__ == '__main__':
    print('Hello world!')
    spider = Spider(input('BOOK ID: '))
    spider.get_index()
    spider.get_cont()
    print('Bye world!')