# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 10:09:45 2019

@author: VILAJETID
"""

from structure import structure
from db import db
import pandas
from alarm import alarms
 

database = db()


#Retrieves all sos boxes that have sent data in the past month
#and their structure info
SQL = """
SELECT DISTINCT GOOD_BOXES.*, Inspection.COMPLETEDATETIME AS Inspection
FROM
(SELECT DISTINCT GOOD_BOXES.*
				,Facilities.Network
				,Facilities.FacilityName
				,Facilities.Latitude
				,Facilities.Longitude
				,Facilities.FacilityKey
                ,Facilities.AssetID
FROM (SELECT DISTINCT GOOD_BOXES.*, CASE WHEN CoverInfo.VentedCover IS NULL 
									OR CoverInfo.VentedCover = 'N' THEN 'NO' 
									ELSE 'YES' END AS isVented 
		FROM (SELECT DISTINCT SD.IMEINumber, SL.Borough,SL.MSPlate,SL.StructureType,SL.StructureNumber,SL.FacilityCode,SL.SerialNo
				FROM FIS_CONED.sos.SensorData AS SD
				INNER JOIN FIS_CONED.sos.SensorLocations AS SL
				ON SD.IMEINumber = SL.IMEINumber
				WHERE SD.MeasurementTime >= DATEADD(DAY,-35,GETDATE()) 
				AND SL.FacilityCode != 0
				AND SL.StructureNumber NOT LIKE 'Test%') as GOOD_BOXES
		LEFT JOIN
		(SELECT DISTINCT CASE Region WHEN 'MANHATTAN' THEN 'M'
                                     WHEN 'Manhattan' THEN 'M'
		                             WHEN 'QUEENS' THEN 'Q' 
			  					     WHEN 'BROOKLYN' THEN 'B' 
							         WHEN 'BRONX' THEN 'X' 
							         WHEN 'WESTCHESTER' THEN 'W'
							         WHEN 'westchester' THEN 'W' 
                                     WHEN 'STATEN ISLAND' THEN 'S'
							         WHEN 'Brooklyn' THEN 'B'
							         WHEN 'Bronx' THEN 'X'
							         WHEN 'Staten island' THEN 'S'
                                     END AS Borough,
                                            Network,
                                            MSPlate,
                                            StructureType,
                                            StructureNumber,
                                            VentedCover
			FROM [UG_Testing].[dbo].[CoverReplacedStructures]
            WHERE StructureType IN ('MH','SB')) as CoverInfo
			ON GOOD_BOXES.Borough = CoverInfo.Borough
			AND GOOD_BOXES.MSPlate = CoverInfo.MSPlate
			AND GOOD_BOXES.StructureType = CoverInfo.StructureType
			AND GOOD_BOXES.StructureNumber = CoverInfo.StructureNumber) AS GOOD_BOXES
LEFT JOIN WMS.ventyx.Facilities_SSA as Facilities
ON GOOD_BOXES.Borough = Facilities.Borough
AND GOOD_BOXES.MSPlate = Facilities.MSPlate
AND GOOD_BOXES.StructureType = Facilities.StructureType
AND GOOD_BOXES.StructureNumber = Facilities.StructureNumber) AS GOOD_BOXES
LEFT JOIN WMS.ventyx.WMS_SIP_CYCLE3_INSPECTIONS_COMBINED AS Inspection
ON GOOD_BOXES.FacilityCode = Inspection.EXTERNAL_FACILITY_ID;
"""

#Contains query results
data = pandas.read_sql(SQL,database.get_conn())

#List of objects of type structure
structures = []

for row in data.values:
    
    #Eception handling to catch error which results from attempt to convert sql results to string
    try:
        
        #Append a newly created object of type structure(the * unpacks the row into the different variables to pass as parameters)
        structures.append(structure(*row.astype(str)))
    except UnicodeEncodeError:
        
        net = []
        #Seperate the row into its seperate elements and if the element is of type unicode encode the element data
        for elem in row:
            
            if type(elem) == unicode:
                
                text = elem.encode('utf8')
                net.append(text.replace('\xe2\x80\x99','\''))
                
            else:
                
                net.append(str(elem))
        
        #After the row has been properly encoded do as above in the 'try' argument
        structures.append(structure(*net))
        
finished = False

while not finished:
    #Create alarm object
    test_alarm = alarms(['vilajetid@coned.com']) #DRAW FROM sos.Users

    #For every structure analyze the sos data
    for struct in structures:

        test_alarm.analyze(struct.sos)

    