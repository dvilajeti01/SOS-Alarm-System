# Structure Observation System (SOS) Alarm Tool
#### Development: Daniel Vilajeti
#### Documentation: Daniel Vilajeti, Steven Barrios


## Context

The SOS serves as an integrated environmental monitoring tool for underground structures. The system is comprised of devices (also known as SOS boxes) that contain sensors and cameras that collects ambient data. The data that is captured is important because it provides a way to remotely check if an underground structure presents a safety hazard, based on insight on the condition of the structure itself . 

The SOS alarm tool will analyze the data from the SOS boxes, and will determine if the data recorded at a specfic time requires followup by appropiate personnel. In such event, an email alert will be sent that will provide information about the alarm triggered, the data collected by the SOS box, and the structure that the box is located in.

## Technologies
  
 * Python
    - [Pandas](https://pandas.pydata.org/)
 * Microsoft SQL Server 2014

## Logistics

Roughly 4 thousand SOS boxes have been installed, with about 3 thousand in †continuous communication at any given time. The boxes are manufactored by an outside vendor, who also handles the communication between the SOS boxes and ConEd. The data that is collected by all active SOS boxes are uploaded hourly as a .csv file located in ```\\m020diseng1\datadirs2\Secondary Analysis\RDX\CNIGuard ```. 

From here, the file is parsed and appended to a Microsoft SQL Server table named ```FIS_CONED.sos.SensorData``` via an SQL SISS(Service Integration Services Package) Job created by a former intern(Mikhail Foemko) and currently maintained by Srini Budatis. The job is scheduled to run everyday in 30 minute intervals. 
> The photographic data (still and infared photos) the box can provide is also stored on the Con Edison side. However, the SOS alarm tool currently *does not support analysis of this data*. 

The vendor also sends a .csv file specifying the locations of all the boxes. All this data is stored to ```FIS_CONED.sos.SensorData``` and ```FIS_CONED.sos.SensorLocations``` respectively.

From here, we will use Pandas to help analyze the data and determine if any row of the tabular data represents a condition that needs to be further analyzed by appropiate personnel. 

## Justification

The original tool was written in SQL by creating multiple stored procedures. However, there is limited (and sometimes no) documentation on the procedures. It would be extremely difficult to edit without breaking the code. The plan with the new Alarm tool is that it be built to be future proof since it is so difficult to append to the code. 

Daniel Vilajeti decided to rebuild the alarm tool using python and supplement the solution with extensive documentation. He chose python for its readability, low learning curve, and its enormous library of data analysis tools.

## The Alarm System
  
The alarm system may look complicated at first glance due to all the files in the backend folder, though it is quite the opposite. To understand the alarm system, let us begin by first establishing fundamental concepts of the SOS as a process, and relating this back to the backend files.
   
#### Structures

The SOS is responsible for monitoring secondary structures, particularly manholes and service boxes. A structure can be seen as a class with attributes that describe each class instance. The attributes that make each instance of said class unique are StructureType, StructureNumber, MSPlate. Otherwise, the class has multiple member functions that are mostly getter functions. This introduces the first file of importance, `structure.py`.  

#### SOS Boxes
Another attribute of the **structure** class that is of importance is `sos`, which itself is an attribute of type **sos** class. Here is the context: a particular structure may have an SOS box installed. This is the device that will collect the data to later to determine risks in the system. 
> Thus we can say that the SOS box is a property (attribute) of the more general structure *explained later* 
These two main concepts drive the functionality of the email tool, thus we begin with explaining each python file.

 ### structure.py
   
   To initialize the class you must pass all the necessary attributes listed in the parameter list of the __init__ method, as shown below: 
   
   ```python  
   def __init__(self,IMEINumber,Borough,MSPlate,StructureType,StructureNumber
                 ,FacilityCode,SerialNo,isVented,Network,FacilityName
                 ,Longitude,Latitude,FacilityKey,AssetId,Inspection): 
   ```
All parameters must be of type str and in the case that info is missing just pass 'NULL' or 'nan'. It's best to initialize new objects using data retrived from sql via a pandas [Dataframe](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) to ensure lower risk of type mismatching. An example of this can be seen in 
   ```python 
   __main__.py
   ```
This file searches the sql database for all SOS boxes and their associated structure info. Then it passes the info as parameters to initialize each **structure** class instance. As explained earlier, since not all structures have an SOS box installed, 
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
From this implementation, one can see that composition between the sos and structure classes is favored over having an sos object inherit from the structure class. But why does the SOS box not inherit from the structure class? Because the structure **has a** SOS box, it is **NOT A** SOS box. This is the main difference between the composition and inheritance OOP patterns. The diagram below helps visualize this difference.
   
   ![alt text](https://github.com/dvilajeti01/SOS-Alarm-System/blob/version-1.1/README_pictures/Structure-SOS_Diagram.PNG)
   
   
   
   ### sos.py
   
   The sos class is initilized by passing three parameters to the `__init__()` method as seen below
   ```python
   
   def __init__(self,IMEINumber,SerialNo,structure_info):
   ```
   The three parameters are the IMEI Number and Serial Number of the SOS box, and the information about the structure where the SOS box is installed. This is a list of attributes: 
   StructureType,StructureNumber,Borough,MSPlate,Network,FacilityName,isVented,Inspection all of which belong to the structure class.      There is no practical use of declaring an object of the sos class alone. The intended use is for the class to be initialized inside      the structure `__init__()` method. MENTION THE DATABSE ATTRIBUTE
   
   The class has two primary member function aside from the normal getter functions one for each attribute.The first being
   ```python
   def get_recent_data(self):
   ```
   
   Which retrives all the unanalyzed data in the past month for an sos box with a given IMEINumber ordered by MeasuremenTime to ensure the data measurement times are consistent. The other member function is 
   ```python
   def mark_as_analyzed(self,data):
   ```
   which takes a dataframe representing data reaings for the given sos box and updates the 'Analyzed' column to 1 from 0 in the sql database. This signifies that the program has analyzed the data and prevents duplicate alarms or wasted computation.
   
   
   
