# -*- coding: utf-8 -*-
"""
name:sql_email.py

description: Allows for execution of sp_send_dbmail

author:Daniel Vilajeti

email: vilajetid@coned.com

maintained by: Daniel Vilajeti,Steven Barrios(barrioss@coned.com)

python-version: 2.7
"""
from db import db as database

class email(database):
    
    '''
    Class inherits from parent class db since send_email calls a stored procedure
    which needs an SQL DB connection to be executed
    
    '''
    def __init__(self,recipients):
        '''
        Create an instance of email with a list of recipients
        
        Class Attributes;
        
            self.database: an object of the db class which provides a connection to the 
            databse
            
            self.recipients: a list of recipients to send the emails to
        
        Parameters:
            recipients: list, A list of recipients
        '''
        #Inherit from super class
        database.__init__(self)
        
        #Initialize the recipients list as a string emails delimited by ';'
        self.recipients = ';'.join(recipients)
        
    def get_recipients(self):
        return self.recipients
    
    def send_email(self, subject, body, attachment = '', body_format = 'HTML', importance = 'High'):
        
        """
        This function sends an email using the sql sstored procedure 'sp_send_dbmail' from the SQL server
        
        Parameters:
            
            subject: str, subject of the email
            body: str, All the contents of the body this will contain mostly the tables created
            body_format: str, Either 'TEXT' or 'HTML' defaults to HTML
            importance: str, The importance level of the email either 'Low', 'Normal' or 'High' defaults to 'High'
            attachment: str, The absolute file path of the file you wish to attach. File size must be <= 1MB 
            
        """
        
        cursor = self.get_cursor()
        conn = self.get_conn()
        
        #Tuple containing all the parameter values required to send email
        email_info = (self.get_recipients(),subject,body,body_format,importance,attachment)
        
        #SQL Query to be executed which sends the email
        cursor.execute("""EXEC msdb.dbo.sp_send_dbmail  
                       @recipients = ?, 
                       @subject = ?, 
                       @body = ?, 
                       @body_format = ?, 
                       @importance = ?,
                       @file_attachments = ?"""
                       , email_info)
        conn.commit()