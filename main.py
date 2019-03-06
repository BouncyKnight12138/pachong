# -*- coding: UTF-8 -*-
#!/usr/bin/env python3
from spider import *
from file import *
import threading


def updateNovel(timeDelta=7, threadNum=128):
    '''抓取timeDelta日前的小说Index'''
    print('init book list.')
    pool = []
    today = datetime.date.today()
    deadline = today - datetime.timedelta(timeDelta)
    db.connect()
    for book in Book.select().where(Book.lastChapterTime > deadline):
        pool.append(book.id)
    db.close()
    print('待抓取Index数: %s'%len(pool))
    poolLock = threading.Lock()
    dbLock = threading.Lock()
    print('init threads.')

    class SpiderThread(threading.Thread):
        def __init__(self, tid):
            threading.Thread.__init__(self)
            self.id = tid

        def run(self):
            nonlocal pool, poolLock, dbLock
            while pool != []:
                with poolLock:
                    bookId = pool.pop(0)
                spider = Spider(bookId)
                try:
                    lastDate = idSearch(bookId)[10]
                    spider.get_index()
                except AttributeError:
                    print('INVALID ID : %s'%bookId)
                    continue
                except Exception as e:
                    print('ERR %s_%s'%(bookId, e))
                    pool.append(bookId)
                    continue
                else:
                    if spider.lastChapterTime > lastDate:
                        item = [spider.id, spider.category, spider.name, spider.author, spider.status, spider.description,
                                spider.lastChapterId, spider.lastChapterName, spider.lastChapterTime, spider.index_count]
                        with dbLock:
                            try:
                                addItemDB(item)
                            except:
                                addLog('bookList', item)
                        print('Index已更新: %s'%bookId)
                    else:
                        print('Index无更新: %s'%bookId)

    for i in range(0,threadNum):
        locals()['Thread_%s'%i] = SpiderThread(i)
    print('start threads.')
    for i in range(0,threadNum):
        locals()['Thread_%s'%i].start()
    for i in range(0,threadNum):
        locals()['Thread_%s'%i].join()

def rebuildIndex(end=160000, threadNum=128):
    '''重建未收录于数据库的Index'''
    print('init book list.')
    pool = []
    for i in range(1,end):
        pool.append(i)
    db.connect()
    for book in Book.select():
        pool.remove(book.id)
    db.close()
    print('待抓取Index数: %s'%len(pool))
    input('Press ENTER to continue.')
    poolLock = threading.Lock()
    dbLock = threading.Lock()
    print('init threads.')

    class SpiderThread(threading.Thread):
        def __init__(self, tid):
            threading.Thread.__init__(self)
            self.id = tid

        def run(self):
            nonlocal pool, poolLock, dbLock
            while pool != []:
                with poolLock:
                    bookId = pool.pop(0)
                spider = Spider(bookId)
                try:
                    spider.get_index()
                except AttributeError:
                    print('INVALID ID : %s'%bookId)
                except Exception as e:
                    print('ERR %s_%s'%(bookId, e))
                    pool.append(bookId)
                else:
                    item = [spider.id, spider.category, spider.name, spider.author, spider.status, spider.description,
                            spider.lastChapterId, spider.lastChapterName, spider.lastChapterTime, spider.index_count]
                    with dbLock:
                        try:
                            addItemDB(item)
                        except:
                            addLog('BookList', item)

    for i in range(0,threadNum):
        locals()['Thread_%s'%i] = SpiderThread(i)
    print('start threads.')
    for i in range(0,threadNum):
        locals()['Thread_%s'%i].start()
    for i in range(0,threadNum):
        locals()['Thread_%s'%i].join()

def downloadAll(thread_number=8, pageThreadNumber=16):
    '''下载所有local标记为false的小说'''
    print('init db list')
    doList = []
    db.connect()
    for book in Book.select().where(Book.local==False).order_by(Book.chapterNumber):
       doList.append(book.id)
    db.close()
    print('待抓取小说数: %s'%len(doList))
    pool_lock = threading.Lock()

    class Download_book(threading.Thread):
        '''抓取idPool中的小说内容至本地'''
        def __init__(self, tid, pageThreadNumber):
            threading.Thread.__init__(self)
            self.id = tid
            self.pageThreadNumber = pageThreadNumber

        def run(self):
            nonlocal doList, pool_lock
            while doList != 0 :
                with pool_lock:
                    item = doList.pop(0)
                try:
                    spider = Spider(item)
                    try:
                        spider.get_index()
                    except:
                        spider.get_index_local()
                    spider.get_cont(self.pageThreadNumber)
                    if spider.index == True:
                        changeLocalStatus(item, True)
                        print('Done %s_%s'%(len(doList), item))
                        #time.sleep(2)
                except Exception as e:
                    with pool_lock:
                        doList.append(item)
                    print('Get Index Err %s, %s'%(item, e))
                    time.sleep(5)

    for i in range(0,thread_number):
        locals()['Download_%s'%i] = Download_book(i, pageThreadNumber)
    print('start threads...')
    for i in range(0,thread_number):
        locals()['Download_%s'%i].start()
    for i in range(0,thread_number):
            locals()['Download_%s'%i].join()

def checkCache():
    '''校验所有本地缓存文件'''
    pool = []
    db.connect()
    for book in Book.select():
       pool.append((book.id, book.name))
    db.close()
    for item in pool:
        id, name = item
        try:
            index_name, index_cont_name, index_cont_id = getLocalIndex(id, name)
            check(id, name, index_name, index_cont_name, index_cont_id)
            print('  DONE %s_%s '%(id,name))
        except Exception as e:
            changeLocalStatus(id, False)
            print('ERR: %s_%s'%(id, e))


if __name__ == '__main__':
    print('Hello world!')
    downloadAll(1, 128)
    print('Bye world!')
