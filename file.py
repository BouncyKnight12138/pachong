# -*- coding: UTF-8 -*-
#!/usr/bin/env python3
import datetime
import re
import os
from ast import literal_eval
from db import *
from copy import deepcopy

def addLog(name, content):
    '''生成本地log文件'''
    content = str(content)
    if os.path.exists('./%s.txt'%name) == False:
        with open('./%s.txt'%name, 'w', encoding='utf-8') as f:
            f.write('%s\n'%content)
    else:
        with open('./%s.txt'%name, 'a', encoding='utf-8') as f:
            f.write('%s\n'%content)

def check(bookId, bookName, index_name, index_cont_name, index_cont_id):
    '''本地文件校验，返回未缓存的章节列表'''
    bindex_name, bindex_cont_name, bindex_cont_id = (
    deepcopy(index_name), deepcopy(index_cont_name), deepcopy(index_cont_id))
    try:
        bookName = re.sub(r'[\/:*?"<>|]', '', bookName)
        path='./book/%s_%s'%(str(bookId).zfill(7), bookName)
        if os.path.isdir(path):
            dir_one = os.listdir(path)
            dir_one.remove('index_name.txt')
            dir_one.remove('index_cont_name.txt')
            dir_one.remove('index_cont_id.txt')
            dir_one.sort()
            for i in range(0, len(dir_one)):
                if os.path.isdir(os.path.join(path, dir_one[i])):
                    dir_two = os.listdir(os.path.join(path, dir_one[i]))
                    dir_two.sort()
                    dir_two.reverse()
                    for item in dir_two:
                        index_cont_name[i].pop(int(item[:5]))
                        index_cont_id[i].pop(int(item[:5]))
    except:
        # 本地文件校验出错，清除已缓存内容
        print('%s_%s Local Cache is Broken.'%(bookId, bookName))
        os.system('rm -rf %s/0*'%path)
        # 取消数据库中local标记
        try:
            db.connect()
            obj = Book.get(Book.id == bookId)
            obj.local = False
            obj.save()
            db.close()
        except Exception as e:
            db.close()
            print(e)
            time.sleep(3)
        return((bindex_name, bindex_cont_name, bindex_cont_id))
    else:
        #检验本地文件是否完整，重置local状态
        for i in range(0,len(index_name)):
            if index_cont_id[i] != []:
                print('%s_%s Local Cache Incomplete.'%(bookId, bookName))
                try:
                    db.connect()
                    obj = Book.get(Book.id == bookId)
                    obj.local = False
                    obj.save()
                    db.close()
                except:
                    db.close()
                break
        return((index_name, index_cont_name, index_cont_id))

def getLocalIndex(bookId, bookName):
    '''读取本地的index文件'''
    bookName = re.sub(r'[\/:*?"<>|]', '', bookName)
    path='./book/%s_%s'%(str(bookId).zfill(7), bookName)
    if os.path.isdir(path):
        with open('%s/index_cont_id.txt'%path, "r", encoding="utf-8") as f:
            index_cont_id = eval(f.read())
        with open('%s/index_cont_name.txt'%path, "r", encoding="utf-8") as f:
            index_cont_name = eval(f.read())
        with open('%s/index_name.txt'%path, "r", encoding="utf-8") as f:
            index_name = eval(f.read())
        return((index_name, index_cont_name, index_cont_id))
    else:
        return(1)

def saveFile(name0, name1, name2, content):
    '''书名， 卷名，章名，内容'''
    # 清洗文件名
    name0 = re.sub(r'[\/:*?"<>|]', '', name0)
    name1 = re.sub(r'[\/:*?"<>|]', '', name1)
    name2 = re.sub(r'[\/:*?"<>|]', '', name2)
    # 确认路径
    if os.path.exists("./book/%s/%s"%(name0, name1)) == False:
        os.makedirs("./book/%s/%s"%(name0, name1))
    with open("./book/%s/%s/%s.txt"%(name0, name1, name2), "w", encoding="utf-8") as f:
        f.write(content)

def saveIndex(name0, name1, content):
    '''保存索引'''
    name0 = re.sub(r'[\/:*?"<>|]', '', name0)
    content = str(content)
    if os.path.exists("./book/%s"%name0) == False:
        os.makedirs("./book/%s"%name0)
    with open("./book/%s/%s.txt"%(name0, name1), "w", encoding="utf-8") as f:
        f.write(content)

def addBookList(content):
    '''将小说信息添加到bookList.txt文件'''
    content = str(content)
    if os.path.exists('./bookList.txt') == False:
        with open('./bookList.txt', 'w', encoding='utf-8') as f:
            f.write('%s\n'%content)
    else:
        with open('./bookList.txt', 'a', encoding='utf-8') as f:
            f.write('%s\n'%content)
            

# peewee取代本地bookList文件

class Book(Model):
    id = IntegerField(primary_key=True)
    category = CharField(max_length=12)
    name = CharField(max_length=120)
    author = CharField(max_length=120)
    status = CharField(max_length=6)
    local = BooleanField()
    chapterNumber = IntegerField()
    description = TextField()
    lastChapterId = IntegerField()
    lastChapterName= CharField(max_length=120)
    lastChapterTime = DateField()
    class Meta:
        database = db

def createTable():
    '''创建Book表'''
    try:
        db.connect()
        db.create_tables([Book])
        db.close()
    except Exception as e:
        db.close()
        raise(e)

def addItemDB(item): 
    '''将小说信息添加到数据库'''
    # item: [id, category, name, author, status, description, lastChapterId, lastChapterName, lastChapterTime, chapterNumber]
    try:
        db.connect()
        id, category, name, author, status, description, lastChapterId, lastChapterName, lastChapterTime, chapterNumber = item
        try:
            # 若已存在则更新
            book = Book.get(Book.id == int(id))
            book.category, book.name, book.author, book.description = (category, name, author, description)
            book.status, book.lastChapterId, book.lastChapterName, book.lastChapterTime, book.chapterNumber = (
            status, lastChapterId, lastChapterName, lastChapterTime, chapterNumber)
            book.local = False
            book.save()
        except:
            # 若不存在则新建
            Book.create(id=id, category=category, name=name, author=author, status=status, description=description, 
                        lastChapterId=lastChapterId, lastChapterName=lastChapterName, lastChapterTime=lastChapterTime, 
                        local=False, chapterNumber=chapterNumber)
        db.close()
    except Exception as e:
        db.close()
        raise(e)

def idSearch(id):
    '''根据ID返回小说信息'''
    db.connect()
    try:
        item = Book.get(Book.id == int(id))
        db.close()
        return([item.id, item.category, item.name, item.author, item.status, item.local, item.chapterNumber, 
                item.description, item.lastChapterId, item.lastChapterName, item.lastChapterTime])
    except Exception as e:
        db.close()
        raise(e)

def fileToDatabase():
    '''将写入数据库失败的数据重新写入'''
    with open('./bookList.txt', encoding= 'utf-8') as f:
        for line in f.readlines():
            try:
                item = eval(line.strip())
                addItemDB(item)
                print(item)
            except Exception as e:
                print('ERR or END：%s'%e)

def completeLocal(id):
    '''更新数据库中状态为缓存完成'''
    db.connect()
    obj = Book.get(Book.id == id)
    obj.local = True
    obj.save()
    db.close()


if __name__ == '__main__':
    print('Hello world')
    pool = []
    db.connect()
    for book in Book.select():
       pool.append((book.id, book.name))
    db.close()
    for item in pool:
        id, name = item
        index_name, index_cont_name, index_cont_id = getLocalIndex(id, name)
        check(id, name, index_name, index_cont_name, index_cont_id)
        print('  DONE %s_%s '%(id,name))
    print('Bye world')

        