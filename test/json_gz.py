# -*- coding: UTF-8 -*-
#!/usr/bin/env python3
from __future__ import unicode_literals
import gzip
import json
import os
import re
import threading
import time
from file import *




def transfer(thread_number=32):
    path = './book'
    book_pool = os.listdir(path)
    book_pool.sort()
    book_pool_lock = threading.Lock()
    print(len(book_pool))

    class LThread(threading.Thread):

        def __init__(self):
            threading.Thread.__init__(self)

        def run(self):
            nonlocal book_pool, book_pool_lock
            while book_pool != []:
                with book_pool_lock:
                    book = book_pool.pop()
                book_path = os.path.join(path, book)
                if os.path.exists('%s/index.json.gz'%book_path):
                    continue
                chapter_pool = os.listdir(book_path)
                del_pool = os.listdir(book_path)
                chapter_pool.sort()
                chapter_pool.remove('index_name.txt')
                chapter_pool.remove('index_cont_name.txt')
                chapter_pool.remove('index_cont_id.txt')
                # 处理Index
                index = {}
                for item in ['index_name.txt', 'index_cont_name.txt', 'index_cont_id.txt']:
                    index_path = os.path.join(book_path, item)
                    with open(index_path, "r", encoding="utf-8") as f:
                        index[item[:-4]] = eval(f.read())
                with gzip.open('%s/index.json.gz'%book_path, 'wt', encoding='utf-8', compresslevel=9) as f:
                    json.dump(index, f, ensure_ascii=False)
                # 处理章节内容
                for chapter in chapter_pool:
                    section_path = os.path.join(book_path, chapter)
                    section_pool = os.listdir(section_path)
                    section_pool.sort()
                    content = {}
                    for section in section_pool:
                        section_id = int(section[:5])
                        section_name = section[6:-4]
                        with open(os.path.join(section_path, section), 'r', encoding='utf-8') as f:
                            section_content = f.read()
                        content[section_id] = [section_name, section_content]
                    chapter = re.sub('《[\s\S]*》', '', chapter)
                    with gzip.open('%s/%s.json.gz'%(book_path, chapter), 'wt', encoding='utf-8', compresslevel=9) as f:
                        json.dump(content, f, ensure_ascii=False)
                # 删除原内容
                for item in del_pool:
                    os.system('rm -rf "%s/%s"'%(book_path, item))
                print('Book: %s'%book)

    for i in range(0,thread_number):
        locals()['Thread_%s'%i] = LThread()
    print('start threads.')
    for i in range(0,thread_number):
        locals()['Thread_%s'%i].start()
    for i in range(0,thread_number):
        locals()['Thread_%s'%i].join()

def transfer2():
    '''transfer功能补充'''
    # 1.delete '《', '》' in the book name;
    # 2.delete '《', '》' in the index.json.gz.index_name;
    # 3.delete nongz file in the sub_path;
    # 4.update the book name in the database;

    path = './book'
    book_pool = os.listdir(path)
    book_pool.sort()
    for book in book_pool:


        # fuc 1
        if book != re.sub(r'[《》]', '' , book):
            os.system('mv "%s/%s" "%s/%s"'%(path, book, path, re.sub(r'[《》]', '' , book)))
            book = re.sub(r'[《》]', '' , book)

            # fuc 4
            db.connect()
            item = Book.get(Book.id == int(book[:7]))
            item.name = book[8:]
            item.save()
            db.close()
            print('name clean, ', end='')
        else:
            print('name pass,  ', end='')

        # fuc 3
        sub_path = os.path.join(path, book)
        sub_pool = os.listdir(sub_path)
        for item in sub_pool:
            if item[-2:] != 'gz':
                os.system('rm -rf "%s/%s"'%(sub_path, item))
                print('file clean, ', end='')

        # fuc 2
        with gzip.open('%s/index.json.gz'%sub_path, 'rt', encoding='utf-8') as f:
            content = json.load(f)
        index_name = content['index_name']
        new_index_name = []
        for item in index_name:
            new_index_name.append(re.sub('《[\s\S]*》', '' , item))
        if new_index_name != index_name:
            content['index_name'] = new_index_name
            with gzip.open('%s/index.json.gz'%sub_path, 'wt', encoding='utf-8', compresslevel=9) as f:
                json.dump(content, f, ensure_ascii=False)
            print('index clean: ', end='')
        else:
            print('index pass:  ', end='')

        print('%s: '%book)




if __name__ == '__main__':
    print('Hello world')
    transfer2()
    print('Bye world')