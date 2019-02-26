# -*- coding: UTF-8 -*-
#!/usr/bin/env python3
from __future__ import unicode_literals
import gzip
import json
import os
import re
import threading
import time




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
                with gzip.open('%s/index.json.gz'%book_path, 'wt', encoding='utf-8',compresslevel=9) as f:
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
                    with gzip.open('%s/%s.json.gz'%(book_path, chapter), 'wt', encoding='utf-8',compresslevel=9) as f:
                        json.dump(content, f, ensure_ascii=False)
                # 删除原内容
                for item in del_pool:
                    os.system('rm -rf %s/%s'%(book_path, item))
                print('Book: %s'%book)

    for i in range(0,thread_number):
        locals()['Thread_%s'%i] = LThread()
    print('start threads.')
    for i in range(0,thread_number):
        locals()['Thread_%s'%i].start()
    for i in range(0,thread_number):
        locals()['Thread_%s'%i].join()  

if __name__ == '__main__':
    print('Hello world')
    transfer()
    print('Bye world')