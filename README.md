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

''' fdfdgdf '''

