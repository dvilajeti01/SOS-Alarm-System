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
import pandas

class alarms(object):
    
    def __init__(self,recipients):

        #Create instance of email with recipients
        self.EMAIL = email(recipients)

        self.tests = self.load_tests()
        
    def get_recipients(self):
        return self.EMAIL.get_recipients()
    
    def get_tests(self):
        return self.tests.copy()
    
    def add_test(self):
        pass
    
    def load_tests(self):
         
        database = db(to_str = True)
         
        SQL = """SELECT A.AlarmType
                       ,A.Id
                       ,A.Name
                       ,T.TestType
	                   ,T.ColumnCheck
	                   ,T.Threshold
	                   ,T.Operation
	                   ,T.Rate 
                 FROM FIS_CONED.sos.AlarmTypes AS A
                 INNER JOIN FIS_CONED.sos.TestTypes as T
                 ON A.Id = T.AlarmId;"""

        tests_df = pandas.read_sql(SQL,database.get_conn())
        
        
        database.close_conn()
        
        tests = {}
        
        for row in range(len(tests_df)):
            alarm_type = tests_df.loc[row,'AlarmType']
            alarm_id =  tests_df.loc[row,'Id']
            alarm_name = tests_df.loc[row,'Name']
            test_type = tests_df.loc[row,'TestType']
            column = tests_df.loc[row,'ColumnCheck']
            
            try:
                threshold = float(tests_df.loc[row,'Threshold'])
            except ValueError:
                threshold = tests_df.loc[row,'Threshold']
            
            operation = tests_df.loc[row,'Operation']
            rate = tests_df.loc[row,'Rate']
            
            tests.setdefault(alarm_type,{}).setdefault((alarm_id,alarm_name),{}).setdefault(test_type,[]).append(column)
            tests.setdefault(alarm_type,{}).setdefault((alarm_id,alarm_name),{}).setdefault(test_type,[]).append(threshold)
            tests.setdefault(alarm_type,{}).setdefault((alarm_id,alarm_name),{}).setdefault(test_type,[]).append(operation)
            
            if test_type == 'Rate':
                tests.setdefault(alarm_type,{}).setdefault((alarm_id,alarm_name),{}).setdefault(test_type,[]).append(rate)
        
        return tests
            
    def check(self,tests_map,data):
        
        CHECK = {'==': lambda reading,threshold: True if reading == threshold else False,
                 '<': lambda reading,threshold: True if reading < threshold else False,
                 '>': lambda reading,threshold: True if reading > threshold else False,
                 '<=': lambda reading,threshold: True if reading <= threshold else False,
                 '>=': lambda reading,threshold: True if reading >= threshold else False
        } 
        
        results_map = {}
        
        for row in range(len(data)):
            
            for test_id,test in tests_map.keys():
                
                main_check = tests_map[(test_id,test)]['Main']
                column,threshold,operation = main_check
                
                if CHECK[operation](data.loc[row,column],threshold):
                    try:
                        conditional_check = tests_map[(test_id,test)]['Conditional']
                        column,threshold,operation = conditional_check
                        
                    except KeyError:
                        results_map.setdefault((test_id,test),[]).append(row)
                    
                    else:
                        if CHECK[operation](data.loc[row,column],threshold):
                            results_map.setdefault((test_id,test),[]).append(row)
        return results_map
    
    def is_valid_reading(self,data,threshold = 8):

        constraints = self.tests['Constraint']
        
        invalids_maps = self.check(constraints,data)
        
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
        
    def record_alarm(self,alarm_id,alarm_type,imein,reading_start,reading_end):
        
        database = db()
        
        SQL = """INSERT INTO FIS_CONED.sos.Alarms (Alarm_ID,AlarmType,DateCreated,IMEINumber,ReadingsStart,ReadingsEnd)
                 VALUES (?,?,?,?,?,?)"""
        database.get_cursor().execute(SQL,(alarm_id,alarm_type,datetime.now(),imein,reading_start,reading_end))
        database.get_conn().commit()
        
        database.close_conn()
    
    def analyze(self,sos):
        
        unanalyzed_data = sos.get_unanalyzed_data()
        
        if not unanalyzed_data.empty:
            
            results_map = self.check(self.tests['Flat'],unanalyzed_data)
        
            if results_map:
           
                recent_readings = sos._get_context(unanalyzed_data)
            
                if self.is_valid_reading(recent_readings):
                
                    imeinumber = sos.get_imein()
                    serialno = sos.get_serialno()
                    structure_info = sos.get_structure_info()
                    earliest_measurement = recent_readings.loc[len(recent_readings)-1,'MeasurementTime']
                    latest_measurement = recent_readings.loc[0,'MeasurementTime']
                    
                    for test_id,test in results_map.keys():
                        self.record_alarm(test_id,test,imeinumber,latest_measurement,earliest_measurement)
                        self.trigger_alarm(recent_readings,test,imeinumber,serialno,structure_info,results_map[test])
                
        #sos._mark_as_analyzed(unanalyzed_data)
        
        
