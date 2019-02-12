# -*- coding: UTF-8 -*-
from spider import *
from file import *
import threading


def addBPOLL(content):
    # TODO: 添加文件名参数传入，移到file去
    content = str(content)
    if os.path.exists('./BPOLL.txt') == False:
        with open('./BPOLL.txt', 'w', encoding='utf-8') as f:
            f.write('%s\n'%content)
    else:
        with open('./BPOLL.txt', 'a', encoding='utf-8') as f:
            f.write('%s\n'%content)

def updateDatabasePool(timeDelta):
    '''生成timedelta(日)前的小说idPool'''
    print('init book list.')
    pool = []
    today = datetime.date.today()
    deadline = today - datetime.timedelta(timeDelta)
    db.connect()
    for book in Book.select().where(Book.lastChapterTime > deadline):
        pool.append(book.id)
    db.close()
    return(pool)


def getIndex(pool, threadNum=16):
    '''多线程抓取pool中ID的Index并更新database'''
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
                poolLock.acquire()
                bookId = pool.pop(0)
                poolLock.release()
                spider = Spider(bookId)
                try:
                    spider.get_index()
                except Exception as e:
                    print('ERR %s_%s'%(bookId, e))
                    pool.append(bookId)  # 该操作存在死循环风险，仅限于ID确认存在情况，否则使用下方except
                    continue
                #except:
                #    addBPOLL(bookId)
                #    continue
                else:
                    if spider.index:
                        item = [spider.id, spider.category, spider.name, spider.author, spider.status, spider.description, 
                                spider.lastChapterId, spider.lastChapterName, spider.lastChapterTime, spider.index_count]
                        dbLock.acquire()
                        try:
                            addItemDB(item)
                        except:
                            addBookList(item)
                        dbLock.release()
                        print('%s Thread%s done %s_%s'%(time.ctime(time.time()), self.id, bookId, len(pool)))
                    else:
                        addBPOLL(bookId)
    
    for i in range(0,threadNum):
        locals()['Thread_%s'%i] = SpiderThread(i)
    print('start threads.')
    for i in range(0,threadNum):
        locals()['Thread_%s'%i].start()
    for i in range(0,threadNum):
        locals()['Thread_%s'%i].join()


class Download_book(threading.Thread):
    '''抓取idPool中的小说内容至本地'''
    def __init__(self, tid, pageThreadNumber):
        threading.Thread.__init__(self)
        self.id = tid
        self.pageThreadNumber = pageThreadNumber
        
    def run(self):
        global doList, pool_lock
        while doList != 0 :
            pool_lock.acquire()
            item = doList.pop(0)
            pool_lock.release()
            try:
                spider = Spider(item)
                try:
                    spider.get_index()
                except:
                    spider.get_index_local()
                spider.get_cont(self.pageThreadNumber)
                if spider.index == True:
                    completeLocal(item)
                    print('Done %s_%s'%(len(doList), item))
                    #time.sleep(2)
            except:
                pool_lock.acquire()
                doList.append(item)
                pool_lock.release()
                print('Get Index Err %s'%item)
                time.sleep(10)

if __name__ == '__main__':
    print('Hello world!')
    print('init db list')
    thread_number = 32
    pageThreadNumber = 8
    doList = []
    db.connect()
    for book in Book.select().where(Book.chapterNumber>0).where(Book.chapterNumber<100).where(Book.local==False).order_by(Book.chapterNumber):
       doList.append(book.id)
    db.close()
    print(len(doList))
    pool_lock = threading.Lock()
    for i in range(0,thread_number):
        locals()['Download_%s'%i] = Download_book(i, pageThreadNumber)
    print('start threads.')
    for i in range(0,thread_number):
        locals()['Download_%s'%i].start()
    for i in range(0,thread_number):
            locals()['Download_%s'%i].join()
    print('Bye world!')
