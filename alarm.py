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
    
    def __init__(self,recipients,tests = None,constraints = None, disable_constraints = False):
        '''
        Initializes an object of type alarms
            
        Class Attributes:
            self.email is an object of the email class. This allows the alarms to be sent to the team
            using the SQL Stored Procedure. Look at the sql_email class for more
            self.tests a mapping of different tests to be conducted on the sos data*
            self.constraints a mapping of constraints that invalidate or validate sos data*
            
        Parameters:
            recipients: list, a list of recipient emails
            tests: dict, (optional)a mapping of tests* 
            constraints: dict, (optional)a mapping of data constraints*
            disable_constraints: bool, signifies wether to consider data constraints or not. False by default,
            setting to True may result in excessive emails
            
            *See Readme for more info
        
        '''

        #Create instance of email with recipients
        self.email = email(recipients)

        if tests:
            self.tests = tests
        else:
            self.tests = self.load_tests()
            
        if not disable_constraints:
            
            if constraints:
                self.constraints = constraints
            else:
                try:
                    self.constraints = self.tests['Constraint']
                except KeyError:
                    print('There are no constraints in the loaded tests')
                    self.constraints = {}

        else:
            self.constraints = {}
        
    def get_recipients(self):
        '''
        Retrieves the list of recipients stored in SQL Server.
        Returns a list of strings
        '''
        return self.email.get_recipients()
    
    def get_tests(self):
        '''
        Retrieves tests stored in SQL Server
        '''
        return self.tests.copy()

    def load_tests(self):
        '''
        Retrieves all tests stored in sql.
        Returns a dict of tests.
        
        See Readme for dict structure.
        '''
        database = db(to_str = True)
         
        SQL = """SELECT * FROM FIS_CONED.sos.Tests;"""

        tests_df = pandas.read_sql(SQL,database.get_conn())
        
        database.close_conn()
        
        tests = {}
        
        for row in range(len(tests_df)):
            alarm_type = tests_df.loc[row,'AlarmType']
            alarm_id =  str(tests_df.loc[row,'ID'])
            alarm_name = tests_df.loc[row,'Name']
            test_type = tests_df.loc[row,'TestType']
            column = tests_df.loc[row,'ColumnCheck']

            
            try:
                threshold = float(tests_df.loc[row,'Threshold'])
            except ValueError:
                threshold = tests_df.loc[row,'Threshold']
            
            operation = tests_df.loc[row,'Operation']
            rate = float(tests_df.loc[row,'Rate'])
            
            tests.setdefault(alarm_type,{}).setdefault((alarm_id,alarm_name),{}).setdefault(test_type,[]).append(column)
            tests.setdefault(alarm_type,{}).setdefault((alarm_id,alarm_name),{}).setdefault(test_type,[]).append(threshold)
            tests.setdefault(alarm_type,{}).setdefault((alarm_id,alarm_name),{}).setdefault(test_type,[]).append(operation)
            tests.setdefault(alarm_type,{}).setdefault((alarm_id,alarm_name),{}).setdefault(test_type,[]).append(rate)
        
        return tests
            
    def check(self,tests_map,data):
        '''
        The check function runs the direct analysis on the sos data.
        
        Parameters:
            tests_map, dict: A mapping of the tests
            data, pandas.datframe: The table to be analyzed
            
        Returns:
            results_map, dict: A mapping of the test that triggered the alarm and the row which contains
            the data that triggered the alarm
        '''
        
        #A mapping between the operation and equivalent lambda function that performs the operation
        CHECK = {'==': lambda reading,threshold: True if reading == threshold else False,
                 '<': lambda reading,threshold: True if reading < threshold else False,
                 '>': lambda reading,threshold: True if reading > threshold else False,
                 '<=': lambda reading,threshold: True if reading <= threshold else False,
                 '>=': lambda reading,threshold: True if reading >= threshold else False,
                 '!=': lambda reading,threshold: True if reading != threshold else False
        } 
        
        results_map = {}
        
        #For every row in the table
        for row in range(len(data)):
            
            #Check data in row against every test
            for test_id,test in tests_map.keys():
                
                
                main_check = tests_map[(test_id,test)]['Main']
                column,threshold,operation,rate = main_check
                
                if rate == 0:
                
                    #If the main check returned true
                    if CHECK[operation](data.loc[row,column],threshold):

                        #Check conditional test
                        try:
                            conditional_check = tests_map[(test_id,test)]['Conditional']
                            column,threshold,operation,rate = conditional_check
                            
                            if CHECK[operation](data.loc[row,column],threshold):
                                #In the case that both main and conditional tests return true
                                #append instanceto the results_map
                                results_map.setdefault((test_id,test),[]).append(row)
                            
                        except KeyError:
                            results_map.setdefault((test_id,test),[]).append(row)

                else:
                    #PERFROM RATE CHECK
                    pass
        
        return results_map
    
    def is_valid_reading(self,data,threshold = 8):

        '''
        Checks if a given set of data is valid or invlaid
        
         Parameters:
            data, pandas.datframe: The table to be analyzed
            threshold, int: Number of invalid readings that classify an invalid data table
            default set to 8
        Returns:
            bool: True signifies valid data false signifies invalid
        '''
        constraints = self.constraints
        
        invalids_map = self.check(constraints,data)
        
        num_invalid = 0
        
        for rows in invalids_map.values():
            
            num_invalid += len(rows)
            
            if num_invalid >= threshold:
                return False
                
        return True
    
    def trigger_alarm(self,data,alarm_type,imeinumber,serialno,structure_info,trigger_readings = []):
        '''
        Builds the email to be sent out to team
        
         Parameters:
            data, pandas.datframe: The table to be analyzed
            alarm_type, str: the alarm type that has been triggered
            imeinumber, str: unique identifier of the sos box
            serialno, str: serial number of the box
            structure_info, pandas.dataframe: Contains structure_info of the sos box
            trigger_readings, list: list of rows which triggered alarm
            
        '''
        print('sending email...')
        subject = alarm_type.upper() + ' Alarm Notification--' + imeinumber + '--' + serialno
        
        body = '<h1 align="center">%s</h1>\n' % (alarm_type.upper() + ' Threshold Alarm')
        body += '<h2 align="center">Structure Info</h1>\n'
        body += draw_table(structure_info)
        body += '<h2 align="center">Readings</h2>'
        body += draw_table(data,alarm_type,trigger_readings,'red',False)
        
        #Append link to sos dash board
        body += """<p align="center">
                        <a href="http://ssawebn/sos/?structure={Borough}_{MSPlate}_{StructType}_{StructNum}&show_chart=true">SOS Dash<a/>
                   </p>""".format(Borough = structure_info.loc[0,'Borough']
                                  ,MSPlate = structure_info.loc[0,'MSPlate']
                                  ,StructType = structure_info.loc[0,'StructureType']
                                  ,StructNum = structure_info.loc[0,'StructureNumber'])
                            
        self.email.send_email(subject,body)
        
    def record_alarm(self,alarm_id,alarm_type,imein,reading_start,reading_end):
        '''
        Stores alarm triggered by saving box and alarm info as well as the first and last
        readings so one can recreate the alarm later
        
         Parameters:
            alarm_id, str: The alarm id
            alarm_type, str: The alarm type
            imein, str: unique identifier of the sos box
            reading_start, str: The measurement time of the first reading
            reading_end, str: The measurement time of the last reading

        '''
        database = db()
        
        SQL = """INSERT INTO FIS_CONED.sos.Alarms(AlarmID,DateCreated,IMEINumber,ReadingsStart,ReadingsEnd)
                 VALUES (?,?,?,?,?)"""
        database.get_cursor().execute(SQL,(alarm_id,datetime.now(),imein,reading_start,reading_end))
        database.get_conn().commit()
        
        database.close_conn()
    
    def analyze(self,sos,mark_as_unanalyzed = True):
        '''
         Parameters:
            sos, sos: Instance of the sos box to be analyzed
            mark_as_unanalyzed, bool: Determines if analyzed data gets marked as analyzed or not.

        '''
        unanalyzed_data = sos.get_unanalyzed_data()
                
        if not unanalyzed_data.empty:
            
            results_map = self.check(self.tests['Flat'],unanalyzed_data)

            if results_map:
           
                recent_readings = sos._get_context(unanalyzed_data)

                if self.is_valid_reading(recent_readings):

                    imeinumber = sos.get_imein()
                    serialno = sos.get_serialno()
                    structure_info = sos.get_structure_info()
                    earliest_measurement = str(recent_readings.loc[len(recent_readings)-1,'MeasurementTime'])
                    latest_measurement = str(recent_readings.loc[0,'MeasurementTime'])
                    
                    for test_id,test in results_map.keys():
                        self.record_alarm(test_id,test,imeinumber,latest_measurement,earliest_measurement)
                        self.trigger_alarm(recent_readings,test,imeinumber,serialno,structure_info,results_map[test_id,test])
        
            results_map.clear()
        
        if mark_as_unanalyzed:
                
            sos._mark_as_analyzed(unanalyzed_data)
        
        
