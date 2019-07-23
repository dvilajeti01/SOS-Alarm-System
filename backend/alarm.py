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
    
        self.tests = {'Temperature':[['Temperature',122,'>']],
                      'CO':[['CO',35,'>='],['Flood',False,'==']],
                      'Stray Voltage':[['StrayVoltage',5,'>=']]}
    
    def check(self,reading,constraint):
        '''
        Counts the number of invalid readings in a given row
        
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
       
    
        for row_index in range(len(data)):
           
            for col in CONSTRAINTS.keys():
               
                for constraint in CONSTRAINTS[col]:
                    #Check the reading at index and column against constraints
                    #Increment invalid reading count by the return of 'check' function
                    
                    num_invalid += self.check(data.loc[row_index,col],constraint)
                   
                    if num_invalid >= threshold:
                        return False
          
        return True

    def analyze(self,sos):
        '''
        Analyze data from an instance of SOS class and send Email if an alarm is triggered
        
        Parameters:
            sos, SOS instance, The instance of an sos box to be analyzed
        '''
        
        
        data = sos.get_data()
        
        #Check fo validity of datagroup
        if self.is_valid_reading(data):

            for row in range(len(data)):
            
                for test in self.tests.keys():
                
                    flat_check = self.tests[test][0]
                    col = flat_check[0]
                    constraint = flat_check[1:]
                    
                    if self.check(data.loc[row,col],constraint) == 1:
                        
                        #Exception handling is used for flow of control (also to avoid the Index error lol)
                        try:
                            conditional_check = self.tests[test][1]
                            
                            col = conditional_check[0]
                            constraint = conditional_check[1:]
                                        
                        except IndexError:
                                    
                            subject = test.upper() + ' Alarm Notification--' + sos.get_imein()
                                    
                            body = '<h1 align="center">%s</h1>\n' % (test.upper() + ' Threshold Alarm')
                            body += '<h2 align="center">Structure Info</h1>\n'
                            body += draw_table(sos.get_structure_info())
                            body += '<h2 align="center">Readings</h1>'
                            body += draw_table(data,row,'red',False)
                            #body += '<h1 align="center">Cable Info</h1>'
                            #body += draw_table(sos.get_cable_info())
                        
                            self.EMAIL.send_email(subject,body)
                        else:
                        
                            if self.check(data.loc[row,col],constraint) == 1:
                               
                                subject = test.upper() + ' Alarm Notification--' + sos.get_imein()
                                    
                                body = '<h1 align="center">%s</h1>\n' % (test.upper() + ' Threshold Alarm')
                                body += '<h2 align="center">Structure Info</h1>\n'
                                body += draw_table(sos.get_structure_info())
                                body += '<h2 align="center">Readings</h1>'
                                body += draw_table(data,row,'red',False)
                                #body += '<h1 align="center">Cable Info</h1>'
                                #body += draw_table(sos.get_cable_info())
                            
                                self.EMAIL.send_email(subject,body)     
                    