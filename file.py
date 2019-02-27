# -*- coding: UTF-8 -*-
#!/usr/bin/env python3
from __future__ import unicode_literals
import datetime
import gzip
import json
import os
import re
from copy import deepcopy
from db import *


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
            dir_one.remove('index.json.gz')
            dir_one.sort()
            for i in range(0, len(dir_one)):
                chapter_path = os.path.join(path, dir_one[i])
                if os.path.exists(chapter_path):
                    with gzip.open(chapter_path, 'rt') as f:
                        chapter_content = json.load(f)
                    dir_two = list(chapter_content.keys())
                    dir_two = [int(x) for x in dir_two]
                    dir_two.sort(reverse=True)
                    for item in dir_two:
                        index_cont_name[i].pop(item)
                        index_cont_id[i].pop(item)
    except Exception as e:
        # 本地文件校验出错，清除已缓存内容
        print('Broken Local Cache: %s_%s: %s'%(bookId, bookName,e))
        os.system('rm -rf "%s"'%path)
        # 取消数据库中local标记
        try:
            changeLocalStatus(bookId, False)
        except Exception as e:
            print(e)
        return((bindex_name, bindex_cont_name, bindex_cont_id))
    else:
        # 检验本地文件是否完整，重置local状态
        for i in range(0,len(index_name)):
            if index_cont_id[i] != []:
                print('Incomplete Local Cache: %s_%s'%(bookId, bookName))
                changeLocalStatus(bookId, False)
                break
        return((index_name, index_cont_name, index_cont_id))

def getLocalIndex(bookId, bookName):
    '''读取本地的index文件'''
    bookName = re.sub(r'[\/:*?"<>|]', '', bookName)
    path='./book/%s_%s/index.json.gz'%(str(bookId).zfill(7), bookName)
    try:
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            index = json.load(f)
        index_name = index['index_name']
        index_cont_name = index['index_cont_name']
        index_cont_id = index['index_cont_id']
        return((index_name, index_cont_name, index_cont_id))
    except Exception as e:
        raise(e)

def saveFile(name0, name1, name2, content):
    '''书名， 卷名，章名，内容'''
    # 这块本该重写的，但是我选择后面接上 fuc transfer 续一续
    # 清洗文件名
    name0 = re.sub(r'[\/:*?"<>|]', '', name0)
    name1 = re.sub(r'[\/:*?"<>|]', '', name1)
    name2 = re.sub(r'[\/:*?"<>|]', '', name2)
    # 确认路径
    if os.path.exists("./book/%s/tmp/%s"%(name0, name1)) == False:
        os.makedirs("./book/%s/tmp/%s"%(name0, name1))
    with open("./book/%s/tmp/%s/%s.txt"%(name0, name1, name2), "w", encoding="utf-8") as f:
        f.write(content)

def transfer(id, name):
    '''把楼上产生的临时文件合并到json.gz里去'''
    name = re.sub(r'[\/:*?"<>|]', '', name)
    path = './book/%s_%s'%(str(id).zfill(7), name)
    try:
        pool = os.listdir('%s/tmp'%path)
    except:
        return(0)
    else:
        for chapter in pool:
            try:
                # 尝试解析已有json文件
                with gzip.open('%s/%s.json.gz'%(path, chapter), 'rt', encoding='utf-8') as f:
                    content = json.load(f)
            except:
                content = {}
            sub_path = '%s/tmp/%s'%(path, chapter)
            sub_pool = os.listdir(sub_path)
            for section in sub_pool:
                section_id = int(section[:5])
                section_name = section[6:-4]
                with open(os.path.join(sub_path, section), 'r', encoding='utf-8') as f:
                    section_content = f.read()
                content[section_id] = [section_name, section_content]
            with gzip.open('%s/%s.json.gz'%(path, chapter), 'wt', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False)
        os.system('rm -rf "%s/tmp"'%path)

def saveIndex(id, name, index_name, index_cont_name, index_cont_id):
    '''保存Index文件'''
    index = {}
    index['index_name'] = index_name
    index['index_cont_name'] = index_cont_name
    index['index_cont_id'] = index_cont_id
    book_path = './book/%s_%s'%(str(id).zfill(7), re.sub(r'[\/:*?"<>|]', '', name))
    with gzip.open('%s/index.json.gz'%book_path, 'wt', encoding='utf-8', compresslevel=9) as f:
        json.dump(index, f, ensure_ascii=False)


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

def changeLocalStatus(id, status=True):
    '''更新数据库中状态'''
    try:
        db.connect()
        obj = Book.get(Book.id == id)
        obj.local = status
        obj.save()
        db.close()
    except Exception as e:
        db.close()
        raise(e)


if __name__ == '__main__':
    print('Hello world')
    print('Bye world')

