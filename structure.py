# -*- coding: utf-8 -*-
"""
name:structure.py

description: Contains structure class

author:Daniel Vilajeti

email: vilajetid@coned.com

maintained by: Daniel Vilajeti,Steven Barrios(barrioss@coned.com)

python-version: 2.7
"""
from sos import sos

class structure(object):
    def __init__(self,IMEINumber,Borough,MSPlate,StructureType,StructureNumber
                 ,FacilityCode,SerialNo,isVented,Network,FacilityName
                 ,Longitude,Latitude,FacilityKey,AssetId,Inspection):
     
        '''
        Initialize an object of type structure which represents a physical structure
        in the secondary system.
    
        Class Attributes:
        
            self.sos = object of class sos that represent the sos box loocated in
            the structure. There may be no sos box in a given structure
        
            self.StructureType = The type of the structure could be SB(Service Box), MH(Manhole) or VLT(Vault)
            self.StructureNumber = The structure number though this is not a unique indentifier
            self.Borough = Borough in which structure is located in
            self.MSPlate = MSPlate assosiated with structure
            self.Network = Network associated with structure
            self.FacilityName = Facility Name of the structure
            self.isVented = Determines if the structure has a vented cover or not
            self.Inspection = The latest incpection performed on the structure
            self.FacilityCode = The facility Code of the structure used at times as a unique identifier
            self.FacilityKey = Like facility code but used as a unique idetifier in other tables 
            self.AssetId = Same as Facility Code or Facility Key
            self.Longitude = The longitude gps coordinate
            self.Latitude = The longitude gps coordinate
    
        Parameters:
        
            All the parameters are str type values that represent all the listed class attributes above
        '''
        #If there is a valid IMEINumber then create an object of the class sos
        #signifying that the structure does have an sos box
        if IMEINumber != 'nan' and IMEINumber != 'None':
            structure_info = [StructureType,StructureNumber,Borough,MSPlate,Network,FacilityName,isVented,Inspection]
            self.sos = sos(IMEINumber,SerialNo,structure_info)
        
        self.StructureType = StructureType
        self.StructureNumber = StructureNumber
        self.Borough = Borough
        self.MSPlate = MSPlate
        self.Network = Network
        self.FacilityName = FacilityName
        self.isVented = isVented
        self.Inspection = Inspection
        self.FacilityCode = FacilityCode
        self.FacilityKey = FacilityKey.strip('.0')
        self.AssetId = AssetId
        self.Longitude = Longitude
        self.Latitude = Latitude
        
    def get_structure_type(self):
        return self.StructureType
    
    def get_structure_number(self):
        return self.StructureNumber
    
    def get_borough(self):
        return self.Borough
    
    def get_msplate(self):
        return self.MSPlate
    
    def get_network(self):
        return self.Network
    
    def get_facility_name(self):
        return self.FacilityName
    
    def get_isVented(self):
        return self.isVented
    
    def get_latest_inspection(self):
        return self.Inspection
    
    def get_facility_code(self):
        return self.FacilityCode
    
    def get_facility_key(self):
        return self.FacilityKey
    
    def get_assetid(self):
        return self.AssetId
    
    def get_longitude(self):
        return self.Longitude
    
    def get_latitude(self):
        return self.Latitude
    
    def get_sos(self):
        return self.sos
    
    def has_sos(self):
        return True if self.sos is not None else False
    
        