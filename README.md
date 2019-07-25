# SOS(Structure Observation System) Alarm System

  The goal of the sos alarms is primarily to analyze incoming data and alert the specified members of the DE(Distributed Enineering) team. The Alerts will provide information about the structure in which the sos box is located and a snapshot of the latest data including the reading that triggered the alarm.  

  To understand the code behind the alarms an explanation of SOS system is required.

## SOS Background

  SOS boxes are a predictive attempt at reducing structure events such as manhole explosions. SOS boxes take measurements of the environmet in which they reside. These measurements include but are not limited to Temperature, CO (carbon monoxide), and Stray Voltage. Given the SOS box capabilities a decison was made to place them in underground structures through out the NY boroughs. Roughly 4 thousand boxes have been installed though only ~3 thousand are in †continuous communication at any given time. The boxes are manufactored by CNIGuard which also handles the communication between the boxes and ConEd. The communication includes an hourly upload of new data in the form of a .csv file located in ```\\m020diseng1\datadirs2\Secondary Analysis\RDX\CNIGuard ```. Here the file is imported and appended to ```FIS_CONED.sos.SensorData``` SQL table via an SQL SISS(Service Integration Services Package) Job created by a former intern(Mikhail Foemko) and currently maintained by Srini Budatis. The job is scheduled to run everyday in 30 minute intervals. The boxes also takes an IR (infrared) and digital photo of the cables and walls of the structure. Though the alarms do not analyze these photos(yet). Along side the .csv file contaning the new data readings CNIGuard also sends an additional .csv file specifying the locations of all the boxes. All this data is stored to ```FIS_CONED.sos.SensorData``` and ```FIS_CONED.sos.SensorLocations``` respectively.
  
  Now since the SOS background has been given, here comes the fun part, THE ALARM SYSTEM!. The alarms are not my idea, they were a thing before my time here at ConEd. They were created by Mikhail Foemko, written in SQL by creating multiple stored procedures. Why are they being re-done? Becasue the logic was funky,there is limited to no documentation and it is extremely difficult to edit without breaking the code. In addition to those reasons it was not built to be future proof since it is so difficult to append to the code. Given these reason I decided to re-write the alarms sytem using python and a lot of documentation. I chose python becasue of its readability and its enormous library of data analysis tools. Also becasue it is easy to learn since I learned it in my first two weeks here at ConEd. 
  
  ## The Alarm System
  
   The alarm system may look complicated at first glance due to all the files in the backend folder, though it is quite the opposite. To understand the alarm system let me draw a picture of the backend files and how they all tie in together to make life easier.
   
 ### structure.py
 
   You can generalize the entire secondary system analysis(SSA) to mean the task of monitoring all structures. A structure has an array of information attached to it that creates a unique identity, such information includes Borough, MSPlate, StructureType and StructureNumber. Though there is many other attributes associated to a structure these four mentioned above can be used to get the remainig info. Given this generalization I created the structure class which has many attributes of which the most important are Borough, MSPlate, StructureType, StructureNumber, isVented(if the structure cover is vented), inspection(last performed inspection) and sos(object of the sos class). The class has multiple member function mainly a bunch of getter function to retrive all the class attributes.  
   
   To initialize a class you must pass all the necessary attributes listed in the parameter list of the 
   ```python  
   def __init__(self,IMEINumber,Borough,MSPlate,StructureType,StructureNumber
                 ,FacilityCode,SerialNo,isVented,Network,FacilityName
                 ,Longitude,Latitude,FacilityKey,AssetId,Inspection): 
   ```
   method. All parameters must be of type str and in the case that info is missing just pass 'NULL' or 'nan'. It's best to initialize new objects using data retrived from sql via a pandas.DataFrame to ensure lower risk of type mismatching. An example of this can be seen in 
   ```python 
   __main__.py
   ```
   where I search the sql databse for all sos boxes and their structure info and pass the info as parameters for initializing an obect of type ```structure```. Equally as important as the other attributes but a bit more complex is the attribute 
   ```python 
   self.sos
   ``` 
   which is an object of the sos class. Going back to the generalization part of the monotoring tools an analyst of the secondary system has to determine risks in the system is SOS data via an sos box located inside a structure. As mentioned earlier not all structures have an sos box there fore the `python self.sos`
   
   ![alt text](https://github.com/dvilajeti01/SOS-Alarm-System/blob/version-1.1/README_pictures/structure_sos_diagram.PNG)
