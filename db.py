# -*- coding: UTF-8 -*-
#!/usr/bin/python3
from peewee import *

db = MySQLDatabase(
     'test', 
     user = 'test', 
     password = 'passwd', 
     host = '127.0.0.1', 
     port = 3306, 
     charset = 'utf8')