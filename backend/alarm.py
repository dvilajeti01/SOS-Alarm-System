# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 11:38:48 2019

@author: VILAJETID
"""

    # -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 11:04:28 2019

@author: VILAJETID
"""


from styles import draw_table
from sql_email import email

class alarms(object):
    
    def __init__(self,recipients):
        
        '''
        Initializes an instance with its own 'to' list for the emails and 
        then tests to be ran on the SOS data
        
        Class Attributes:
            self.recipients
            self.tests
        
        Parameters:
            recipients: list, a list of all the recipients of the alarm emails
        '''
        #Create instance of email with recipients
        self.EMAIL = email(recipients)
    
        #Initializes the tests to be conducted
        #A map consisting of an alarm name as the key and a list containing 
        #the test and an optional condition as the vlaues
        self.tests = {'Temperature':[['Temperature',122,'>']],
                      'CO':[['CO',35,'>='],['Flood',False,'==']],
                      'StrayVoltage':[['StrayVoltage',5,'>=']]}
    
    def check(self,reading,constraint):
        '''
        Checks if a given reading has reached the threshold value in such case 
        the function returns 1 otherwise 0
        
        Parameters:
            readings: list, The reading to be checked against threshold using a specified comparison
            constraints: tuple, threshold value, and the comparison to be conducted 
            (threshold,comparison)
            
        Returns:
            int, 1 if compariosn True else 0
        '''
        #Dictionary mapping of str representation of operands to a lambda function which takes two values and applies operand
        OPERATIONS = {'==': lambda reading,threshold: 1 if reading == threshold else 0,
                      '<': lambda reading,threshold: 1 if reading < threshold else 0,
                      '>': lambda reading,threshold: 1 if reading > threshold else 0,
                      '<=': lambda reading,threshold: 1 if reading <= threshold else 0,
                      '>=': lambda reading,threshold: 1 if reading >= threshold else 0
        } 
        
        threshold = constraint[0]
        operation = constraint[1]
        
        #All readings must meet constraint otherwise you return 0. Think of it as if there was an invisible AND operator
        if OPERATIONS[operation](reading,threshold) == 0:
            return 0
        
        return 1
    
    
    def is_valid_reading(self,data,threshold = 5):
        
        '''
        Checks the validity of given readings
        
        Parameters:
            data: pandas.DataFrame instance, The readings to be validified 
            threshold: int, The maximum number of invalid readings allowed (default 5 invalid for all 12 rows)
            
        Returns:
            True is num_invalid below threshold else False
        '''
        #Dictionary containing the different invalid reading signifiers/constraints
        CONSTRAINTS = {
                'Humidity': [(0,'=='),(100,'==')],
                'Temperature': [(264.2,'=='),(0,'<')],
                'Barometer': [(800,'<'),(1200,'>')],
                'Flood': [(True,'==')]
                }
       
       
        num_invalid = 0
       
    
        for row in range(len(data)):
           
            for col in CONSTRAINTS.keys():
               
                for constraint in CONSTRAINTS[col]:
                    
                    #Check the reading at index and column against constraints
                    #Increment invalid reading count by the return of 'check' function
                    num_invalid += self.check(data.loc[row,col],constraint)
                   
                    if num_invalid >= threshold:
                        return False
          
        return True
    
    def trigger_alarm(self,alarm_type,sos,data,trigger_readings = [],FILL = 20):
        '''
        Builds the email to be sent if an alarm is triggered
        
        Parameters:
            
            alarm_type: str, The name of the larm being triggered
            sos: <class 'sos.sos'>, The sos object whose data is being analyzed
            data: <class 'pandas.DataFrame'> The data that triggered the alarm 
            trigger_readings: list, a list of rows in the data table that specify the trigger readings(the rows to be highlighted)
        '''
        
        
        print('sending email...')
        subject = alarm_type.upper() + ' Alarm Notification--' + sos.get_imein() + '--' + sos.get_serialno()
                                    
        body = '<h1 align="center">%s</h1>\n' % (alarm_type.upper() + ' Threshold Alarm')
        body += '<h2 align="center">Structure Info</h1>\n'
        body += draw_table(sos.get_structure_info())
        
        
        body += '<h2 align="center">Readings</h1>'
        
        if len(data) < 20:
            recent_readings = sos._get_context(data,FILL)
        else:
            recent_readings = data
        
        body += draw_table(recent_readings,alarm_type,trigger_readings,'red',False)
        #body += '<h1 align="center">Cable Info</h1>'
        #body += draw_table(sos.get_cable_info())
                        
        self.EMAIL.send_email(subject,body)
        
    
    def analyze(self,sos):
        '''
        Analyze data from an instance of SOS class and send Email if an alarm is triggered
        
        Parameters:
            sos, SOS instance, The instance of an sos box to be analyzed
        '''
        
        data = sos.get_unanalyzed_data()
        
        alarms_map = {}
        
        #If there is data and it is valid conduct test
        if len(data) >= 1 and self.is_valid_reading(data):

            #Check every row in the recent readings
            for row in range(len(data)):
            
                #Against every test
                for test in self.tests.keys():
                
                    flat_check = self.tests[test][0]
                    
                    col = flat_check[0]
                    constraint = flat_check[1:]
                    
                    #Check the reading against constraint
                    if self.check(data.loc[row,col],constraint) == 1:
                        
                        #Exception handling is used for flow of control (also to avoid the Index error lol)
                        try:
                            conditional_check = self.tests[test][1]
                            
                            col = conditional_check[0]
                            constraint = conditional_check[1:]
                        
                        #If reading exceeded threshold and there is no conditional check send email
                        except IndexError:
                        
                            alarms_map.setdefault(test,[]).append(row)
                        
                        #Otherwise if there is a conditional check  conduct test if that returns positive then send email
                        else:
                        
                            if self.check(data.loc[row,col],constraint) == 1:
                               
                                alarms_map.setdefault(test,[]).append(row)     
        
        #For every alarm send an email if there were any readings that exceeded thresholds
        for alarm in alarms_map.keys():
            
            trigger_readings = alarms_map[alarm]
            print(alarm,trigger_readings)
            
            if len(trigger_readings) >= 1:
                
                self.trigger_alarm(alarm,sos,data,trigger_readings)
        
        #After analyzing the data, mark is at analyzed as not to recieve duplicate emails
        sos._mark_as_analyzed(data)   