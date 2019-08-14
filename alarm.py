# -*- coding: utf-8 -*-

"""
name:alarm.py

description: Contains all methods used to analyze sos data

author:Daniel Vilajeti

email: vilajetid@coned.com

maintained by: Daniel Vilajeti,Steven Barrios(barrioss@coned.com)

python-version: 2.7
"""


from styles import draw_table
from sql_email import email
from db import db
from datetime import datetime

class alarms(object):
    
    def __init__(self,recipients):

        #Create instance of email with recipients
        self.EMAIL = email(recipients)
    
        #Initializes the tests to be conducted
        #A map consisting of an alarm name as the key and a list containing 
        #the test and an optional condition as the vlaues
        self.TESTS = {'Temperature':[['Temperature',122,'>=']],
                      'CO':[['CO',35,'>='],['Flood',False,'==']],
                      'StrayVoltage':[['StrayVoltage',5,'>=']]}
    
    def get_recipients(self):
        return self.EMAIL.get_recipients()
    
    def get_tests(self):
        return self.TESTS.copy()

    def check(self,tests_map,data):
        
        CHECK = {'==': lambda reading,threshold: True if reading == threshold else False,
                 '<': lambda reading,threshold: True if reading < threshold else False,
                 '>': lambda reading,threshold: True if reading > threshold else False,
                 '<=': lambda reading,threshold: True if reading <= threshold else False,
                 '>=': lambda reading,threshold: True if reading >= threshold else False
        } 
        
        results_map = {}
        
        for row in range(len(data)):
            
            for test in tests_map.keys():
                
                main_check = tests_map[test][0]
                column,threshold,operation = main_check
                
                if CHECK[operation](data.loc[row,column],threshold):
                    try:
                        conditional_check = tests_map[test][1]
                        column,threshold,operation = conditional_check
                        
                    except IndexError:
                        results_map.setdefault(test,[]).append(row)
                    
                    else:
                        if CHECK[operation](data.loc[row,column],threshold):
                            results_map.setdefault(test,[]).append(row)
        return results_map
    
    def is_valid_reading(self,data,threshold = 8):

        CONSTRAINTS = {
                'Humidity0': [['Humidity',0,'==']],
                'Humidity100': [['Humidity',100,'==']],
                'Temperature0': [['Temperature',0,'<']],
                'Temperature264': [['Temperature',264.2,'==']],
                'Barometer800': [['Barometer',800,'<']],
                'Barometer1200': [['Barometer',1200,'>']],
                'Flood': [['Flood',True,'==']]
                }
        
        invalids_maps = self.check(CONSTRAINTS,data)
        
        num_invalid = 0
        
        for rows in invalids_maps.values():
            
            num_invalid += len(rows)
            
            if num_invalid >= threshold:
                return False
                
        return True
    
    def trigger_alarm(self,data,alarm_type,imeinumber,serialno,structure_info,trigger_readings = []):
        
        print('sending email...')
        subject = alarm_type.upper() + ' Alarm Notification--' + imeinumber + '--' + serialno
        
        body = '<h1 align="center">%s</h1>\n' % (alarm_type.upper() + ' Threshold Alarm')
        body += '<h2 align="center">Structure Info</h1>\n'
        body += draw_table(structure_info)
        body += '<h2 align="center">Readings</h2>'
        body += draw_table(data,alarm_type,trigger_readings,'red',False)
        body += """<p align="center">
                        <a href="http://ssawebn/sos/?structure={Borough}_{MSPlate}_{StructType}_{StructNum}&show_chart=true">SOS Dash<a/>
                   </p>""".format(Borough = structure_info.loc[0,'Borough']
                                  ,MSPlate = structure_info.loc[0,'MSPlate']
                                  ,StructType = structure_info.loc[0,'StructureType']
                                  ,StructNum = structure_info.loc[0,'StructureNumber'])
                            
        self.EMAIL.send_email(subject,body)
        
    def record_alarm(self,alarm_type,imein,reading_start,reading_end):
        
        database = db()
        
        SQL = """INSERT INTO FIS_CONED.sos.Alarms (AlarmType,DateCreated,IMEINumber,ReadingsStart,ReadingsEnd)
                 VALUES (?,?,?,?,?)"""
        database.get_cursor().execute(SQL,(alarm_type,datetime.now(),imein,reading_start,reading_end))
        database.get_conn().commit()
        
        database.close_con()
    
    def analyze(self,sos):
        
        unanalyzed_data = sos.get_unanalyzed_data()
        
        if not unanalyzed_data.empty:
            
            results_map = self.check(self.TESTS,unanalyzed_data)
        
            if results_map:
           
                recent_readings = sos._get_context(unanalyzed_data)
            
                if self.is_valid_reading(recent_readings):
                
                    imeinumber = sos.get_imein()
                    serialno = sos.get_serialno()
                    structure_info = sos.get_structure_info()
                    earliest_measurement = recent_readings.loc[len(recent_readings)-1,'MeasurementTime']
                    latest_measurement = recent_readings.loc[0,'MeasurementTime']
                    
                    for test in results_map.keys():
                        #self.record_alarm(test,imeinumber,latest_measurement,earliest_measurement)
                        self.trigger_alarm(recent_readings,test,imeinumber,serialno,structure_info,results_map[test])
                
        sos._mark_as_analyzed(unanalyzed_data)