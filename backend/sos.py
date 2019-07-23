# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 14:07:53 2019

@author: VILAJETID
"""

import pandas
from db import db

class sos(object):
     def __init__(self,IMEINumber,SerialNo,structure_info):
          
         self.IMEINumber = IMEINumber
         self.SerialNo = SerialNo
         self.structure_info = structure_info
         self.database = db()
         
    
     def get_imein(self):
         return self.IMEINumber

     def get_serialno(self):
         return self.SerialNo
     
     def get_structure_info(self):
         struct_info = pandas.DataFrame([self.structure_info],
                        columns =['StructureType','StructureNumber','Borough','MSPlate','Network','FacilityName','isVented','Inspection'])
        
         return struct_info
    
     def get_data(self):
        
         SQL = """ SELECT DataID,MeasurementTime,Temperature,CO,Barometer
         ,Humidity,Flood,Battery,Methane,StrayVoltage 
         FROM FIS_CONED.sos.SensorData 
         WHERE IMEINumber = ? 
         AND Analyzed = 0 
         AND MeasurementTime >= DATEADD(MONTH,-1,GETDATE());"""
     
         data = pandas.read_sql(SQL,self.database.get_conn(),params = [self.IMEINumber])
         
         return data
     
     def mark_as_analyzed(self,data):
         
         for ID in data.loc[:,'DataID']:
             
             self.database.get_cursor().execute(""" UPDATE FIS_CONED.sos.SensorData
                                                     SET Analyzed = 1 
                                                     WHERE IMEINumber = ?
                                                     AND DataID = ?""",(self.get_imein(),ID))
             
             self.database.get_conn().commit()
    