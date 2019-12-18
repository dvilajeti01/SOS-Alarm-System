# Structure Observation System (SOS) Alarm Tool
#### Development: Daniel Vilajeti
#### Documentation: Daniel Vilajeti, Steven Barrios


## Context

The SOS serves as an integrated environmental monitoring tool for underground structures. The system is comprised of devices (also known as SOS boxes) that contain sensors and cameras that collect ambient data. The data that is captured is important because it provides a way to remotely check if an underground structure presents a safety hazard, based on insight on the condition of the structure itself . 

The SOS alarm tool will analyze the data from the SOS boxes, and will determine if the data recorded at a specfic time requires followup by appropiate personnel. In such event, an email alert will be sent that will provide information about the alarm triggered, the data collected by the SOS box, and the structure that the box is located in.

## Technologies
  
 * Python
    - [pandas](https://pandas.pydata.org/)
    - [pyodbc](https://github.com/mkleehammer/pyodbc/wiki)
 * Microsoft SQL Server 2014

## Logistics

Roughly 4 thousand SOS boxes have been installed, with about 3 thousand in †continuous communication at any given time. The boxes are manufactored by an outside vendor, who also handles the communication between the SOS boxes and ConEd. The data that is collected by all active SOS boxes are uploaded hourly as a .csv file to ```\\m020diseng1\datadirs2\Secondary Analysis\RDX\CNIGuard ```. 

From here, the file is parsed and appended to a Microsoft SQL Server table named ```FIS_CONED.sos.SensorData``` via an SQL SISS(Service Integration Services Package) Job created by a former intern(Mikhail Foemko) and currently maintained by Srini Budatis. The job is scheduled to run everyday in 30 minute intervals. 
> The photographic data (still and infared photos) the box can provide is also stored on the Con Edison side. However, the SOS alarm tool currently *does not support analysis of this data*. 

The vendor also sends a .csv file specifying the locations of all the boxes to ```\\m020diseng1\datadirs2\Secondary Analysis\RDX\CNIGuard ```. The file is named 'DeviceLocationStockInformation.csv' though there are multiple other similarly named files and the best way to destinguish the correct one is by the 'Data modified'. Like with the data csv files there is an additional SQL job that parses the info and appends it to ```FIS_CONED.sos.SensorLocations```.

From here, we will use pandas to help extract,analyze and display the data to determine if any row of the tabular data represents a condition that needs to be further analyzed by appropiate personnel. 

## Justification

The original tool was written in SQL by creating multiple stored procedures. However, there is limited (and sometimes no) documentation on the procedures. It would be extremely difficult to edit without breaking the code. In addition to the lack of documentation the data displayed by the older email system is incorrect due to poor logic. The plan with the new Alarm tool is that it be built to be future proof since it is so difficult to append to the code and provide up-to-date and correct info. The new Alarm tool will laso provide visuals to help with the comprehension of the data. 

Daniel Vilajeti decided to rebuild the alarm tool using python and supplement the solution with extensive documentation. He chose python for its readability, low learning curve, and its enormous library of data analysis tools.

## The Alarm System
  
The alarm system may look complicated at first glance due to all the files in the folder, though it is quite the opposite. To understand the alarm system, let us begin by first establishing fundamental concepts of the SOS as a process, and relating this back to the backend files.
   
## System Structure

The alarm system is mainly comprised of four classes named alarm, sos, sql_email, and db. Each class is implemented in the corresponding file. Ex. alarm class implementation belongs inside alarm.py. These four classes interact in such a way that allows for an orchastrated excecution of the alarm system. Below you'll find detailed explanation of implementation of the four major classes and any major helper functions or odd scripts.

### alarm.py

The alarm class holds majority of the computation and data analysis. Here the user can create an instance or object of the alarm class by specifying the list of users the alrms will be mailed out to, a dictionary mapping out the tests and constraints they wish to test the data against or proceed with the default tests and constriants. In addition the user may also specify to ignore constraints entirely. This may result in an influx of emails containing mostly invalid data.

``` python
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
```
The dictionary format for tests and constraints should follow the below structure otherwise results may be unpredictible:

(alarm_type : (alarm_id,alarm_name) : [column, threshold, operation, rate]) }

alarm_type could be a 'flat' signifying that the test is looking for exceeding threshold values to flag for alarms
or the alarm_type could be 'constraint' which signifies wether the data is valid or invalid

(alarm_id_alarm_name) is pairing which uniquely identifies a given alarm

column specifies the datafield with in the data which the test is being conducted for. e.i 'Temperature'

threshold is the threshold value which the column needs to meet. The specification as to how this threshold is met is specified by
the operation which could be '==' ,'<=' , '>=, '<', '>' or '!='

Finally rate is the time interval which the data is being checked over. This should be 0 until the rate of change functionality is implemented.

The tests and constraints are stored in the view ``` FIS_CONED.sos.Tests ```. Here the ``` sos.Alarm_Types ``` and ```sos.Test_Types```
are joined to produce this view. The Alarm_Types table contains the general info of an alarm such as creater, datecreated, name, id and
wether its active or not. While the Test_Types holds the specific implementation of the test such as column, threshold, operation and rate. The rows of the two tables are connected via alarm_id.

The most important function in the class besides the initializer is the 

``` python

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
 ```
 
 This function is the only function the user needs to explicitly call. this function takes in as a parameter an object of the sos class signifying that the user has decided to analyze the data within thsi sos box.


   

