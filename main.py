# -*- coding: UTF-8 -*-
from spider import *


if __name__ == '__main__':
    spider = Spider(input('BOOK ID: '))
    print('Hello world!')
    spider.get_index()
    spider.get_cont()
    print('Bye world!')