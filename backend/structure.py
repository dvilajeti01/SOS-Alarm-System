# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 15:13:08 2019

@author: VILAJETID
"""

import pandas
from sos import sos


class structure(object):
    def __init__(self,IMEINumber,Borough,MSPlate,StructureType,StructureNumber
                 ,FacilityCode,Network,FacilityKey,AssetId,SerialNo
                 ,FacilityName,Longitude,Latitude,isVented,Inspection):
        
        if IMEINumber is not None:
            self.Box = sos(IMEINumber,Borough,MSPlate,StructureType,StructureNumber,SerialNo)
        
        self.StructureType = StructureType
        self.StructureNumber = StructureNumber
        self.Borough = Borough
        self.MSPlate = MSPlate
        self.Network = Network
        self.FacilityName = FacilityName
        self.isVented = isVented
        self.Inspection = Inspection
        self.FacilityCode = FacilityCode
        self.FacilityKey = FacilityKey
        self.AssetId = AssetId
        self.Longitude = Longitude
        self.Latitude = Latitude
        
    def get_structure_type(self):
        pass
    def get_structure_number(self):
        pass
    def get_borough(self):
        pass
    def get_msplate(self):
        pass
    def get_network(self):
        pass
    def get_facility_name(self):
        pass
    def get_isVented(self):
        pass
    def get_latest_inspection(self):
        pass
    def get_facility_code(self):
        pass
    def get_facility_key(self):
        pass
    def get_assetid(self):
        pass
    def get_longitude(self):
        pass
    def get_latitude(self):
        pass
    
    pass
        