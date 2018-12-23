# -*- coding: UTF-8 -*-
import os, re

def check(bookId, indexName1, indexName2, indexId):
    #To Do:本地历史比对
    return((indexName1, indexName2,indexId))
    
def saveFile(name0, name1, name2, content):
    '''书名， 卷名，章名，内容'''
    #清洗文件名
    name0 = re.sub(r'[\/:*?"<>|]', '', name0)
    name1 = re.sub(r'[\/:*?"<>|]', '', name1)
    name2 = re.sub(r'[\/:*?"<>|]', '', name2)
    #确认路径
    if os.path.exists("./book/%s/%s"%(name0, name1)) == False:
        os.makedirs("./book/%s/%s"%(name0, name1))
    with open("./book/%s/%s/%s.txt"%(name0, name1, name2), "w", encoding="utf-8") as f:
        f.write(content)
        

if __name__ == '__main__':
    pass