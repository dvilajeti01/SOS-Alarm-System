# -*- coding: utf-8 -*-
'''
name:__main__.py

description: Program performs 'black and white' analysis on all
incoming sos data and sends alert emails

author:Daniel Vilajeti

email: vilajetid@coned.com

maintained by: Daniel Vilajeti,Steven Barrios(barrioss@coned.com)

python-version: 2.7
'''

from sos import sos
from db import db
import pandas
from alarm import alarms

def load_structures(SQL_db):
    #Retrieves all sos boxes that have sent data in the past month
    #and their structure info
    
    database = SQL_db
    
    SQL = """SELECT IMEINumber
                    ,SerialNo
                    ,StructureType
                    ,StructureNumber
                    ,Borough
                    ,MSPlate
                    ,Network
                    ,FacilityName
                    ,isVented
                    ,Inspection 
            FROM FIS_CONED.sos.SOS_Structures;"""

    #Contains query results
    data = pandas.read_sql(SQL,database.get_conn())

    #List of objects of type structure
    structures = []

    print('Loading Structures...') 

    for row in data.values:
    
        imein = row[0]
        serial = row[1]
        structure_info = row[2:]
        
        structures.append(sos(imein,serial,structure_info,database))
                
    print('%s Structures Loaded!' % str(len(structures)))

    return structures


def load_recipients(SQL_db):
    
#    database = SQL_db
#
#    SQL = """ SELECT * FROM FIS_CONED.sos.Users"""
#
#    recipients = pandas.read_sql(SQL,database.get_conn()).loc[:,'Email'].astype(str).to_list()
#    
#    return recipients
    
    return ['vilajetid@coned.com']

def main():
    
    SQL_db = db()
    
    structures = load_structures(SQL_db)    
    
    
    SPEAR = load_recipients(SQL_db)
    
    finished = False

    #Create alarm object
    test_alarm = alarms(SPEAR) #DRAW FROM sos.Users
    
    while not finished:
        
        print('ANALYZING DATA...')    
        #For every structure analyze the sos data
        for struct in structures:
            
           test_alarm.analyze(struct)
    
        print('FINISHED ANALYZING')
        finished = True
    SQL_db.close_con()

if __name__ == '__main__':
    main()
    
