# -*- coding: utf-8 -*-
"""
name:sos.py

description: Contains all methods used to store and or retrive all sos info

author:Daniel Vilajeti

email: vilajetid@coned.com

maintained by: Daniel Vilajeti,Steven Barrios(barrioss@coned.com)

python-version: 2.7
"""

import pandas
import datetime

class sos(object):
    def __init__(self,IMEINumber,SerialNo,structure_info,SQL_conn):
         
        '''
        Initializes an object of type sos
            
        Class Attributes:
            self.IMEINumber = IMEINumber of the box which is a unique identifier for the box
            self.SerialNo = SerialNo of the box
            self.structure_info = a list which specifies the StructureType,StructureNumber,Borough,
            MSPlate,Network,FacilityName,isVented(if cover of the structure is vented),
            Inspection(latest inspection of the structure) Structure info specifies info for the structure
            in which the sos box is located inside
            self.database = connection to the database
       
        Parameters:
            
            IMEINumber: str, The IMEINumber of the structure
            SerialNo: str, The SerialNO of the sos box
            structure_info: list, The structure info specified above all element of the list must be strings
        '''
        self.IMEINumber = IMEINumber
        self.SerialNo = SerialNo
        self.structure_info = structure_info
        self.database = SQL_conn
        

    def get_imein(self):
        '''
        Retrieves the IMEINumber of the box
        '''
        return self.IMEINumber
    def get_serialno(self):
        '''
        Retrieves the SerialNo of the box
        '''
        return self.SerialNo
    
    def get_structure_info(self):
        '''
        Returns a dataframe of the structure info
        '''
        struct_info = pandas.DataFrame([self.structure_info],
                       columns =['StructureType','StructureNumber','Borough','MSPlate','Network','FacilityName','isVented','Last Inspection'])
       
        return struct_info

    def get_unanalyzed_data(self):
        '''
        Retrives the recent unanalyzed data for this box
        '''
        print('START....' + str(datetime.datetime.now()))
        SQL = """ SELECT DataID,MeasurementTime,Temperature,CO,Barometer
        ,Humidity,Flood,Battery,Methane,StrayVoltage 
        FROM FIS_CONED.sos.SensorData 
        WHERE IMEINumber = ? 
        AND Analyzed = 0 
        AND MeasurementTime >= DATEADD(MONTH,-1,GETDATE()) 
        ORDER BY MeasurementTime DESC;"""
    
        data = pandas.read_sql(SQL,self.database.get_conn(),params = [self.IMEINumber])
        print('FINISH....' + str(datetime.datetime.now()))
        return data
    
    def _mark_as_analyzed(self,data):
        '''
        Marks a group of data as analyzed by updating the column 'Analyzed' to 1 
        from 0 in the FIS_CONED.sos.SensorData table
        
        Parameters:
            data, pandas.DataFrame object
        '''
        
        #For every row(identified by column DataID) update Analyzed column
        for ID in data.loc[:,'DataID']:
            
            self.database.get_cursor().execute(""" UPDATE FIS_CONED.sos.SensorData
                                                    SET Analyzed = 1 
                                                    WHERE IMEINumber = ?
                                                    AND DataID = ?""",(self.get_imein(),ID))
            
            self.database.get_conn().commit()

    def _get_context(self,data,FILL = 20):
        '''
        Append a older data to the data passed so the total number of rows equals
        that specified in 'fill'.
        
        Parameters:
            data: <class pandas.DataFrame>, The data you would like to pad with 
            older data
            fill: int, the total number of rows you want the resulting table to be
           
         Returns:
             full_data: <class pandas.DataFrame>, a dataframe of size = fill
        '''
        
        if len(data) < FILL:
            
            latest_data = data.loc[:,'MeasurementTime'].max()
            
            SQL = """
            SELECT TOP %s DataID,MeasurementTime,Temperature,CO,Barometer
            ,Humidity,Flood,Battery,Methane,StrayVoltage 
            FROM FIS_CONED.sos.SensorData
            WHERE MeasurementTime <= ?
            AND IMEINumber = ?
            ORDER BY MeasurementTime DESC;
            """ % str(FILL)
            
            context_data = pandas.read_sql(SQL,self.database.get_conn(),params = [latest_data,self.IMEINumber])
            
            return context_data
             
        else:
            return data