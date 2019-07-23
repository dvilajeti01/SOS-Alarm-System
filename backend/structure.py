# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 15:13:08 2019

@author: VILAJETID
"""

from sos import sos

class structure(object):
    def __init__(self,IMEINumber,Borough,MSPlate,StructureType,StructureNumber
                 ,FacilityCode,SerialNo,isVented,Network,FacilityName
                 ,Longitude,Latitude,FacilityKey,AssetId,Inspection):
        
        if IMEINumber is not None:
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
    
        