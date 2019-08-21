    # -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 11:04:28 2019

@author: VILAJETID
"""


from styles import draw_table
from email import email
import pandas


class Alarms:
    
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
        
        self.tests = {('Temperature','any'):[['Temperature',122,'>']],
                      ('Temperature','6'):[['Temperature',20,'>=']],
                      ('CO','any'):[['CO',35,'>='],['Flood',0,'==']],
                      ('CO','2'):[['CO',60,'>='],['Flood',0,'==']],
                      ('Stray Voltage','any'):[['StrayVolatage',5,'>=']]}
                
    
    def check(self,readings,constraint):
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
        for reading in readings:
                
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
                'Flood': [(1,'==')]
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
    
        #Iterate over every Alarm
        for (alarm_name,alarm_type) in self.alarms.keys():
            
            #Check if alarm is of type RATE (if the alarm_type is a number signifying time frame)
            if alarm_type.isalnum():
                
                #Specify rate check(main)
                rate_check = self.alarms[(alarm_name,alarm_type)][0]
               
                #Retrieve a list of "data groups" grouped by the specified rate 
                data = sos.get_data(alarm_type)
                
                for data_group in data:
                    
                    #Check that the data group is a valid reading 
                    if self.is_valid_reading(data_group):
                        
                        #Retrieves the rate of change
                        #POSSIBLE BUG
                        #THE ARITHMETIC DONE ON THE MEASUREMENT TIME WILL BE OF TYPE date RATHER THAN INT
                        #BAD VAR NAME
                        rate_function = (abs(data_group.loc[-1,rate_check[0]] - data_group.loc[0,rate_check[0]])) / (abs(data_group.loc[-1,'MeasurementTime'] - data_group.loc[0,'MeasurementTime'])) 
                        
                        if self.check(rate_function,rate_check[1:]) == 1:
                            #Exception handling for better control flow
                            try:
                                #Check if there is a conditional check
                                conditional_check = self.alarms[(alarm_name,alarm_type)][1]
                            except IndexError:
                                #If not the create and send email
                                print('Test:',alarm_name + '(RATE) has no conditonal test')
                            
                                subject = alarm_name.upper() + '(RATE)' + sos.get_imeain()
                                
                                body = ''
                                body = draw_table(data_group,range(len(data_group)))
                            
                                self.EMAIL.send_email(subject,body)
                            else:
                                #Else perform conditional check if True create and send email
                                readings = []
                        
                                readings.append(data_group.loc[index,conditional_check[0]] for index in len(data_group))
                        
                                if self.check(readings,conditional_check[1:]) == 1:
                            
                                    subject = alarm_name.upper() + '(RATE)' + sos.get_imeain()
                                    
                                    body = ''
                                    body = draw_table(data_group,range(len(data_group)))
                            
                                    self.EMAIL.send_email(subject,body)
            else:
                
                #Specify flat check(main)
                flat_check = self.alarms[alarm_name][0]
            
                #Retrieve list of data groupings
                data = sos.get_data(alarm_type)
                
                for data_group in data:
                    
                    #Check fo validity of datagroup
                    if self.is_valid_reading(data_group):
                        
                        for index in len(data_group):
                            
                            #Check row against flat check
                            if self.check([data_group.loc[index,flat_check[0]]],flat_check[1:]) == 1:
                           
                                
                                #Like above, exception handling is used for flow of control
                                try:
                                    conditional_check = self.alarms[alarm_name][1]
                                    
                                except IndexError:
                                    print('Test:',alarm_name + '(FLAT) has no conditonal test')
                                    
                                    subject = alarm_name.upper() + '(FLAT)' + sos.get_imeain()
                                    
                                    body = ''
                                    body += self.draw_table(data_group,index)
                            
                                    self.EMAIL.send_email(subject,body)
                                else:
                                    if self.check([data_group.loc[index,conditional_check[0]]],conditional_check[1:]) == 1:
                                        subject = alarm_name.upper() + '(FLAT)' + sos.get_imeain()
                                        
                                        body = ''
                                        body += self.draw_table(data_group,index)
                            
                                        self.EMAIL.send_email(subject,body)
