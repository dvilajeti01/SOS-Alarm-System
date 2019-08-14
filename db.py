# -*- coding: utf-8 -*-
"""
name:db.py

description: Allows for connection to sql database

author:Daniel Vilajeti

email: vilajetid@coned.com

maintained by: Daniel Vilajeti,Steven Barrios(barrioss@coned.com)

python-version: 2.7
"""
import pyodbc
import pandas

class db(object):
    
    def __init__(self, to_str = False):
        '''
        Initialize an instance of class db which contains a connection instance from
        pyodbc and a cursor object
        
        Class Attributes:
            
            self.conn: connection to database
            self.cursor: Cursor object to execute queries
        '''
        
        file = open('SQL_DB.txt','r')
        
        #Get database info such as db name, username and password to connect to db
        db_info = file.read()
        
        file.close()
        
        #Create connection to database
        self.conn = pyodbc.connect('DRIVER={%s};'
                      'SERVER=%s;'
                      'DATABASE=%s;'
                      'UID=%s;'
                      'PWD=%s' % tuple(db_info.split(',')), autocommit=True)

        if to_str:
            
            self.conn.setdecoding(pyodbc.SQL_CHAR, encoding='latin1', to=str)
            self.conn.setencoding(str, encoding='latin1')
    
        #Creates cursor object to query the database
        self.cursor = self.conn.cursor()
        
    def get_conn(self):
        '''
        Returns a connection to the database
        '''
        return self.conn
    
    def get_cursor(self):
        '''
        Returns a cursor object from the databse connection used to execute queries
        '''
        return self.cursor

    def close_con(self):
        '''
        Close connection to avoid interference with other connections
        '''
        self.cursor.close()
     