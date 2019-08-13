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

from structure import structure
from db import db
import pandas
from alarm import alarms
from sos import sos

def load_structures():
    #Retrieves all sos boxes that have sent data in the past month
    #and their structure info
    
    database = db()
    
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

    database.close_con()
    
    #List of objects of type structure
    sos_boxes = []

    print('Loading Structures...') 

    for row in data.values:
    
        imein = row[0]
        serial = row[1]
        structure_info = row[2:]
        
        sos_boxes.append(sos(imein,serial,structure_info))
                
    print('%s Structures Loaded!' % str(len(sos_boxes)))

    return sos_boxes


def load_recipients():
#    database = db()
#
#    SQL = """ SELECT * FROM FIS_CONED.sos.Users"""
#
#    recipients = pandas.read_sql(SQL,database.get_conn()).loc[:,'Email'].astype(str).to_list()
#    
#    database.close_con()
#    
#    return recipients
    return ['vilajetid@coned.com']

def main():
    
    sos_boxes = load_structures()    
    
    SPEAR = load_recipients()
    
    finished = False

    #Create alarm object
    test_alarm = alarms(SPEAR) #DRAW FROM sos.Users
    
    while not finished:
        
        print('ANALYZING DATA...')    
        #For every structure analyze the sos data
        i = 0
        for sos_box in sos_boxes:
            
           test_alarm.analyze(sos_box)
           i += 1
           print(i)
        print('FINISHED ANALYZING')
       

if __name__ == '__main__':
    main()
    
