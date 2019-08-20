# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 13:27:47 2019

@author: VILAJETID
"""

import pandas
import re
from db import db

if __name__ == '__main__':
    
    db_conn = db()

    cni_sos_locations = pandas.read_csv('SOS_Locations.csv')

    DISCREPENCY_BOXES_SQL = """
    SELECT DISTINCT SD.IMEINumber AS DISCREPENCY_BOXES
    FROM FIS_CONED.sos.SensorData AS SD
    INNER JOIN FIS_CONED.sos.SensorLocations AS SL
    ON SD.IMEINumber = SL.IMEINumber
    WHERE SD.MeasurementTime >= DATEADD(MONTH,-1,GETDATE()) 
    AND SL.FacilityCode = 0;
    """

    conn = db_conn.get_conn()
    cursor = db_conn.get_cursor()

    discrepency_boxes = pandas.read_sql(DISCREPENCY_BOXES_SQL,conn)


    for row in cni_sos_locations.values:
    
        if str(row[0]) in discrepency_boxes.values and 'nan' not in str(row):
            IMEIN = str(row[0])
            Facility = str(row[4]).strip('.0')
            Borough = ''.join(re.findall("[a-zA-Z]+",str(row[5])))
            MS = str(row[6])
            StructureType = str(row[7])
            StructNum = str(row[8])
            Serial = str(row[11])
       
       
            cursor.execute("""UPDATE FIS_CONED.sos.SensorLocations
                       SET FacilityCode = ?,Borough = ?,MSPlate = ?,StructureType = ?,
                       StructureNumber = ?,InstallDate = NULL, SerialNo = ?
                       WHERE IMEINumber = ?""",(Facility,Borough,MS,StructureType,StructNum,Serial,IMEIN))
            conn.commit()
        
        conn.close()
