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
        
         SQL = """ SELECT MeasurementTime,Temperature,CO,Barometer
         ,Humidity,Flood,Battery,Methane,StrayVoltage 
         FROM FIS_CONED.sos.SensorData 
         WHERE IMEINumber = ? 
         AND Analyzed = 0;"""
     
         data = pandas.read_sql(SQL,self.database.get_conn(),params = [self.IMEINumber])
             
         return data
     
    