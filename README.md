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
  
The alarm system may look complicated at first glance due to all the files in the backend folder, though it is quite the opposite. To understand the alarm system, let us begin by first establishing fundamental concepts of the SOS as a process, and relating this back to the backend files.
   
#### Structures

The SOS is responsible for monitoring secondary structures, particularly manholes and service boxes. A structure can be seen as a class with attributes that describe each class instance. The attributes that make each instance of said class unique are StructureType, StructureNumber, MSPlate. Otherwise, the class has multiple member functions that are mostly getter functions. This introduces the first file of importance, `structure.py`.  

#### SOS Boxes
Another attribute of the **structure** class that is of importance is `sos`, which itself is a class of type **sos**. Here is the context: a particular structure may have an SOS box installed. This is the device that will collect the data to later to determine risks in the system. 
> Thus we can say that the SOS box is a property (attribute) of the more general structure (*explained later*). These two main concepts drive the functionality of the email tool, thus we begin with explaining each python file.

 ### structure.py
   
   To initialize the class you must pass all the necessary attributes listed in the parameter list of the `__init__()` method, as shown below: 
   
   ```python  
   def __init__(self,IMEINumber,Borough,MSPlate,StructureType,StructureNumber
                 ,FacilityCode,SerialNo,isVented,Network,FacilityName
                 ,Longitude,Latitude,FacilityKey,AssetId,Inspection): 
   ```
All parameters must be of type str and in the case that info is missing just pass 'NULL' or 'nan'. It's best to initialize new objects using data retrived from sql via a pandas [Dataframe](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) to ensure lower risk of type mismatching. An example of this can be seen in 
   ```python 
   __main__.py
   ```
This file searches the sql database for all SOS boxes and their associated structure info. Then it passes the info as parameters to initialize each **structure** class instance. As explained earlier, not all structures have an SOS box installed, and 
   ```python 
   structure.py
   ...
   self.sos
   ``` 
may not alaways exist. This is realized by an if statement that checks to see if there is an valid IMEI Number retrieved from the database for the current structure in being read:
   ```python
   #If there is a valid IMEINumber then create an object of the class sos
        #signifying that the structure does have an sos box
        if IMEINumber != 'nan' and IMEINumber != 'None':
            structure_info = [StructureType,StructureNumber,Borough,MSPlate,Network,FacilityName,isVented,Inspection]
            self.sos = sos(IMEINumber,SerialNo,structure_info)
   ```
From this implementation, one can see that composition between the sos and structure classes is favored over inheritance. But why does the SOS box not inherit from the structure class? Because the structure **has a** SOS box, an SOS box **is not** a structure. The difference in relationships described is the main difference between the composition and inheritance OOP patterns. The diagram below helps visualize this difference.
   
   #### Diagram 1
   ![alt text](https://github.com/dvilajeti01/SOS-Alarm-System/blob/version-1.1/README_pictures/Structure-SOS_Diagram.PNG)
   
   
   
   ### sos.py
   
The sos class is initilized by passing three parameters to the `__init__()` method as seen below
 ```python

 def __init__(self,IMEINumber,SerialNo,structure_info):
 ```
 The three parameters are the IMEI Number and Serial Number of the SOS box, and the information about the structure where the SOS box is installed. This is a list of attributes: 
 * StructureType
 * StructureNumber
 * Borough
 * MSPlate 
 * Network 
 * FacilityName 
 * isVented 
 * Inspection 

All of which belong to the structure class as well. There is no practical use of declaring an object of the sos class alone. The intended use is for the class to be initialized inside the structure `__init__()` method. MENTION THE DATABSE ATTRIBUTE

The class has a few primary member function aside from the normal getter methods that need an explanation: 

```python
def get_structure_info(self):
```
###### The method retrives the structure info list but instead of returning it as a list it returns a [DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) instead so that you may be able to display this info as a table. This is very useful when displaying the structure info on the body of the email. 
 
 ```python
 def get_unanalyzed_data(self):
 ```
###### This method retrieves all unanalyzed data which is defined as all rows where the 'Analyzed' values is 0 signifying that the program has not checked this data. The data is returned as a [DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) of unknown size. The size depends on the number of rows CNIGuard has sent over via the .csv file which, as mentioned above is imported to ```FIS_CONED.sos.SensorData``` SQL table. 

```python
 def _mark_as_analyzed(self,data):
 ```
###### In order to avoid duplicate emails and wasted computations the ```FIS_CONED.sos.SensorData``` table has a column named Analyzed which was mentioned above. The value can either be 1 or 0. 1 signifying analyzed and 0 unanalyzed. When the data comes in the from CNIGuard the value is 0 allowing the script to find the new data that just came in. Here the data is analyzed but to make sure this data is not picked up again by the script you need to mark it unanalyzed. This is precisely the functiion of the method. Given the data you want marked analyzed the method changes the value of 'Analyzed' to 1. It uses the DataID of every row which is a unique identifier to find those rows in the database.

```python
def _get_context(self,data):
```
###### As proposed by the recipients of the emails(Zhou) it would be best that the number of rows in the table displayed on the email would be a fixed number. Specifically 20 rows of readings since it provides a sufficient picture of the sos box reading days prior. The method accepts the data you want to append context to. Currently there is an assumtion that the data passed is a subset of the top 20 rows in the total data and that the data passed is the top most data of the top 20 just retieved. These assumptions simplify the implementation of this method though it is only a temporary fix. 

#### Diagram 2

![alt text](https://github.com/dvilajeti01/SOS-Alarm-System/blob/version-1.1/README_pictures/Data_plus_context_padding.PNG)

You may have noticed that these methods run queries to obtain or alter info in the SQL databse. This is accomplished by connecting to the database and excecuting the queries. This task is done using the 
```python
self.database
```
attribute inside the **sos** class. This attribute (as pictured in diagram 1) is an object of **db** class. 


