# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 08:55:03 2019

@author: VILAJETID
"""
import os
import pyodbc
import datetime
import pandas
import matplotlib.pyplot as plot
from matplotlib.backends.backend_pdf import PdfPages
import re
import time


class SOSAlarm:
    
    def __init__(self, mail_list = ['ALL'], list_of_tests = ['ALL']):
        """
         Initializer function for the SOS_Alarm class which creates a connection to the SQL database,
         specifies the email sender, the mailing list and the list of tests to be ran
         
         Parameters:
             
             Mail_List: list, The list of all recipients you wish to send the alarms to (Defaults to everyone 
             in the sos.Users table)
             
             ListOFTests: list, The list of all tests you wish to apply to the data
        """
        
        #Create connection to database
        self.conn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};'
                      'SERVER=disengsqlpr1;'
                      'DATABASE=FIS_CONED;'
                      'UID=netstorm_ro;'
                      'PWD=netstorm_ro', autocommit=True)

        #Creates cursor object to query the database
        self.cursor = self.conn.cursor()
        
        #Query the database to retrieve the sender name
        sql_servername = "SELECT @@SERVERNAME;"
        
        #Store the servername (creates a list of lists i.e [[row1],[row2]])
        dataframe_servername = pandas.read_sql(sql_servername,self.conn)
        
        self.sender = dataframe_servername.astype(str).values[0][0]
        
        
        if mail_list[0] == 'ALL':
            
            sql_mail_list = 'SELECT Email FROM FIS_CONED.sos.Users;'
            
            dataframe_mail_list = pandas.read_sql_query(sql_mail_list,self.conn)
    
            self.mail_list = ';'.join(email[0] for email in dataframe_mail_list.values)
        else:
            
            self.mail_list = ';'.join(mail_list)
                
        if list_of_tests[0] == 'ALL':
            
            self.list_of_tests = ['Flat_Temp','Flat_Tamper','Flat_StrayVoltage']
        else:
            self.list_of_tests = list_of_tests
       
    def isEmpty(self,list):
        '''
        Retruns a boolean signifying whether a list has an empty element
        
        Parameters:
            
            list: list, any list
            
        Return: boolean, True if empty else False
        '''
        for elem in list:
            if elem == ' ' or elem is None:
                return True
        
        return False 
    
    def _border(self,width=80):
        
        TOT_PIXEL = 1920
        LEFT_RATIO = .4
        RIGHT_RATIO = .6
        
        m_left = int((TOT_PIXEL * (1-width/float(100))) * LEFT_RATIO)
        m_right = int((TOT_PIXEL * (1-width/float(100))) * RIGHT_RATIO)
        
        return dict(selector="table",
                    props=[("border-collapse","collapse"),
                           ("width",str(width)+'%'),
                           ("margin-left",str(m_left)),
                           ("margin-right",str(m_right))])

    def _border_style(self,size="1px", density="solid", color="black",orientation="Left",pixels="2px"):
        return dict(selector="td, th",
                    props=[("border","%s" % (str(size) + ' ' + str(density) + ' ' + str(color))),
                           ("text-align",str(orientation)),
                           ("padding",str(pixels))])
    
    def _header_color(self,back_color="#4286f4",text_color="white"):
        return dict(selector="th",props=[("background-color",str(back_color)),
                                         ("color",str(text_color))])
    
    def _highlight_odd_rows(self, row):
	# Return array of booleans that apply a shaded color for odd rows in our DataFrame  
   
        return ['background-color: #F2F2F2' for cell in row]
            
    def _highlight_trigger_reading(self,row,color):
        #Apply style to the row to signal issue or alarm trigger
        style = 'background-color: %s' % color
        return [style for cell in row]
      
    
    def _draw_table(self,dataframe,trigger_reading = None,title = '', figure_text = '', kolor = 'darkorange'): 
        
        """
        Function draws the table for a given sql query
        
        Parameters:
            
            dataframe: <class 'pandas.core.frame.DataFrame'>, Out put from an sql query stored in a Pandas DataFrame
            trigger_reading: str, Identifying ID for the reading that triggered the alarm (optional)
            title: str, The title of the table (Defaults to no title)
            fig_text: str, The text you wish to be posted alongsdie the table figure
            which will appear in pdf file'
        
        Return:
            A list of:
            
            html_string: str, Contains the html code which represents the table created as a string 
            fig: matplotlib.figure.Figure, The figure object which contains the graph
        """
        
        #Figure size in inches
        WIDTH = 10
        HEIGHT = 5
        
        #Table colors
        PRIMARY_CELL_COLOR = 'white'
        SECONDARY_CELL_COLOR = 'lightgrey'
        HEADER_COLOR = 'burlywood'
        
        #Create the figure and axes where table will be displayed
        fig, ax = plot.subplots(figsize=(WIDTH, HEIGHT))

        #Set the title
        ax.set_title(title)
        
        #Remove the axis from the table so you will only see the table
        ax.set_axis_off()
        
        #Store the data from the query in a matrix 
        cell_text = dataframe.values
        
        #Store the column names
        columns = dataframe.columns
        
        #Create the Table in the axes 'ax'
        table =  ax.table(
                    cellText = cell_text, 
                    colLabels = columns, 
                    colColours = [HEADER_COLOR] * len(columns), 
                    #Primary color for even rows and secondary color for odd rows
                    cellColours = [[PRIMARY_CELL_COLOR if row % 2 == 0 else SECONDARY_CELL_COLOR for cell in range(len(columns))] for row in range(len(cell_text))],
                    loc = 'center') 
        
        #Store the index of each column name 
        column_indecies = []
        
        for index in range(0,len(columns)):
            column_indecies.append(index)
        
        #Assignt proportionate column widths for each column name
        table.auto_set_column_width(column_indecies)
        
        #Scale the table so it looks better (otherwise it is too small to view)
        table.scale(2,2)
        
        #Attach styles to pandas table
        styles = [
                self._border(),
                self._border_style(),
                self._header_color()
        ]
        
        
        html_string = dataframe.style.\
                          apply(self._highlight_odd_rows, subset = pandas.IndexSlice[1::2]).\
                          apply(self._highlight_trigger_reading, color = kolor, subset = pandas.IndexSlice[trigger_reading]).\
                          set_table_styles(styles).\
                          hide_index().\
                          render()
    
        #UGLY FIX TO THE TABLE PROBLEM
        html_string = re.sub("\s{4}#{1}[a-z|A-Z|0-9|_]{1,} table","table",html_string)
        
        #Supresses the figure output since it is not necessary
        plot.close()
        
        return [html_string,fig] 

    def _get_alarm_info_table(self,alarm_id):
        
        """
        Retrieves the alarm info from sos.AlarmsMK2 to be used to create AlarmInfo table
        
        Parameters:
            
            alarm_id: str, The identifing id for the current alarm
            pdf: str, the file path and name of the PDF file you wish to append the table to i.e. 'C:\file\path\fileName.pdf'
            
        Return:
            A list of:
            
            html_string: str, Contains the html code which represents the table created as a string 
            fig: matplotlib.figure.Figure, The figure object which contains the graph 
        """
        #Store SQL query
        sql_alarm_info = (""" SELECT A.AlarmID, A.IMEINumber, L.SerialNo, A.AlarmType, A.CreateTime
               FROM FIS_CONED.sos.AlarmsMK2 as A
               JOIN FIS_CONED.sos.SensorLocations as L
               ON A.IMEINumber = L.IMEINumber 
               WHERE AlarmID = ?;""")
  
        #Read the results of the query to DataFrame
        dataframe_alarm_info = pandas.read_sql(sql_alarm_info, self.conn, params = alarm_id)    
        
        #Return the html string
        return self._draw_table(dataframe_alarm_info,title = 'Alarm Info')
    
    def _get_structure_info_table(self,sensor_info):
        """
        Retrieves the structure info for a given IMEINumber
        
        Parameters:
            
            sensor_info: list, A list comprised of FacilityCode, Borough, MSPlate, StructureType, and StructureNumber
            
        Return:
            A list of:
            
            html_string: str, Contains the html code which represents the table created as a string 
            fig: matplotlib.figure.Figure, The figure object which contains the graph
        """
        
        
        sql_structure_info = """ SELECT StructureType, StructureNumber, Borough, MSPlate, Network, FacilityName, isVented as Vented, CAST(LastPostedInspectionDate AS DATE) as LastInspection
                                FROM (SELECT TOP 1 ssa.*, CASE WHEN crs.VentedCover IS NULL OR crs.VentedCover = 'N' THEN 'NO' ELSE 'YES' END AS isVented,
                                      rs.[Priority] AS RebuildPriority,
                                      rs.[ListYear] AS RebuildYear,
                                      CASE WHEN tp.YearTargeted IS NULL THEN 'NO' ELSE 'YES' END AS isTargetted,
                                      CAST(vdc.[Date] AS DATE) VDCdate,
                                      CASE WHEN cycle3.COMPLETEDATETIME IS NULL THEN CAST(cycle2.LastPostedInspectionDate AS DATE) ELSE CAST(cycle3.COMPLETEDATETIME AS DATE) END AS InspectionDate,
                                      cycle2.LastPostedInspectionDate,
                                      cycle3.COMPLETEDATETIME
                                      FROM (SELECT TOP 1 * 
                                            FROM WMS.ventyx.Facilities_SSA ssa
                                            WHERE ssa.Borough = ?
                                            AND ssa.MSPlate = ?
                                            AND ssa.StructureType = ?
                                            AND ssa.StructureNumber = ?) ssa
                                      LEFT JOIN (
                                              SELECT CASE Region WHEN 'MANHATTAN' THEN 'M'
                                                                 WHEN 'QUEENS' THEN 'Q' 
							                                     WHEN 'BROOKLYN' THEN 'B' 
							                                     WHEN 'BRONX' THEN 'X' 
							                                     WHEN 'WESTCHESTER' THEN 'W' 
							                                     WHEN 'STATEN ISLAND' THEN 'S'
                                                     END AS Borough,
                                                     [Network],
                                                     [MSPlate],
                                                     [StructureType],
                                                     [StructureNumber],
                                                     [VentedCover],
                                                     CompletedDate
                                     FROM [UG_Testing].[dbo].[CoverReplacedStructures]
                                         WHERE StructureType IN ('MH','SB','VLT') AND CompletedDate IS NOT NULL) as crs
                                      ON ssa.Borough = crs.Borough AND ssa.MSPlate = crs.MSPlate AND ssa.StructureType = crs.StructureType AND ssa.StructureNumber = crs.StructureNumber
                                      LEFT JOIN (
                                              SELECT * FROM FIS_CONED.dbo.RebuildStructures
                                              WHERE ListYear = (SELECT MAX(ListYear) FROM FIS_CONED.dbo.RebuildStructures)
                                        ) AS rs ON ssa.Borough = rs.Boro AND ssa.MSPlate = rs.MSPlate AND ssa.StructureType = rs.StructureType AND ssa.StructureNumber = rs.StructureNumber
                                      LEFT JOIN(
                                      SELECT * FROM [SVTracking].[dbo].[TargetedPlates]
		                              WHERE YearTargeted = 2017
		                              ) AS tp ON ssa.Borough = tp.Borough ANd ssa.MSPlate = tp.MSPlates
		                              LEFT JOIN (
			                              SELECT FacilityKey, MAX([Date]) AS [Date] FROM [WMS].[vdc].[Inspections]
			                              GROUP BY FacilityKey
		                              ) AS vdc ON ssa.FacilityKey=vdc.FacilityKey
		                              LEFT JOIN(
			                              SELECT DVSN_IND, MS_PLAT_NMBR, ASST_STYP_SHRT_NAME, ASST_NMBR, LastPostedInspectionDate
			                              FROM [EDIS_Feed].[dbo].[cycle_ii_inspections_static_list_wms_6_3_2014]
		                              ) AS cycle2 ON ssa.Borough = cycle2.DVSN_IND AND ssa.MSPlate = cycle2.MS_PLAT_NMBR AND ssa.StructureType = cycle2.ASST_STYP_SHRT_NAME AND ssa.StructureNumber = cycle2.ASST_NMBR
		                              LEFT JOIN(
			                              SELECT EXTERNAL_FACILITY_ID, FACILITYTYPECODE, COMPLETEDATETIME
			                              FROM wms.ventyx.WMS_SIP_CYCLE3_GROSS_INSPECTIONS_VW
		                              ) AS cycle3 ON ssa.FacilityCode = cycle3.EXTERNAL_FACILITY_ID AND ssa.StructureType = CASE WHEN FACILITYTYPECODE IN ('BOXSERVCUS', 'BOXSERVICE') THEN 'SB' 
																								                                 WHEN FACILITYTYPECODE IN ('MANHOLE', 'MANHOLECUS') THEN 'MH'
																								                                 WHEN FACILITYTYPECODE IN ('VAULT' , 'VAULTIB') THEN  'VLT' END 
	
		                              ORDER BY InspectionDate DESC) as StructureInfo;"""
        dataframe_structure_info = pandas.read_sql(sql_structure_info,self.conn,params = sensor_info)
        
        return self._draw_table(dataframe_structure_info,title = 'Structure Info')
        
        
    def _get_cable_info_table(self,sensor_info):
        """
        Retrieves all cable info for a given SOS sensor
        
        Parameters:
            sensor_info: list, A list comprised of FacilityCode, Borough, MSPlate, StructureType, and StructureNumber
            
        Return:
            A list of:
            
            html_string: str, Contains the html code which represents the table created as a string 
            fig: matplotlib.figure.Figure, The figure object which contains the graph
        """
        
        sql_cable_info = """ SELECT CableType, DateBuilt, NumSets AS [Sets], 
                            CONCAT(NumPhase, '-', PhaseConductorSize) AS [Phase],
                            CONCAT(NumNeutral, '-', NeutralConductorSize) AS [Neutral],
                            ToBoro AS [ToBorough],
                            ToMSPlate AS [ToMSPlate],
                            CONCAT(ToStructureType, ToStructureNumber) AS [ToStructure]
                            FROM FIS_CONED.vision.AllUGCablesByStructure
                            WHERE Boro = ?
                            AND MSPlate = ?
                            AND StructureType = ?
                            AND StructureNumber = ?;"""
        
        dataframe_cable_info = pandas.read_sql(sql_cable_info,self.conn,params = sensor_info)
        
        return self._draw_table(dataframe_cable_info,title = 'Cable Info')
        
    def _create_mk2_alarm(self,imeinumber,alarm_type): #WORKS 
        
        """
        Updates the sos.AlarmsMK2 table by appending the new lamr info as a new entry
        
        Parameter:
            
            imeinumber: str, The IMEINumber of the sos sensor which triggered the alarm
            alarm_type: str, The type of test which triggered the Alarm
            
        Return:
            alarm_id : str, The identifying ID of the entry just created
        
        """
        #Store the current time as the time which the alarm was created
        create_time = datetime.datetime.now()
        
        #Excecute the query to update table
        self.cursor.execute("""INSERT INTO FIS_CONED.sos.AlarmsMK2 (IMEINumber,AlarmType,CreateTime) 
                            VALUES (?,?,?);""",
                            imeinumber,alarm_type,create_time)
        self.conn.commit()
        
        #Query to retrieve AlarmID of the newly created alarm
        sql_alarm_id = """SELECT TOP 1 AlarmID FROM FIS_CONED.sos.AlarmsMK2 
                       WHERE IMEINumber = ? AND AlarmType = ? ORDER BY CreateTime desc;"""
        
        #Store the query results
        dataframe_alarm_id = pandas.read_sql(sql_alarm_id,self.conn, params = [imeinumber,alarm_type])
        
        #Return the AlarmID
        return dataframe_alarm_id.astype(str).values[0]
        
    
    def _send_email(self, subject, body, attachment = '', body_format = 'HTML', importance = 'High'):
        
        """
        This function sends an email using the sql sstored procedure 'sp_send_dbmail' from the SQL server
        
        Parameters:
            
            subject: str, subject of the email
            body: str, All the contents of the body this will contain mostly the tables created
            body_format: str, Either 'TEXT' or 'HTML' defaults to HTML
            importance: str, The importance level of the email either 'Low', 'Normal' or 'High' defaults to 'High'
            attachment: str, The absolute file path of the file you wish to attach. File size must be <= 1MB 
            
        """
        
        #Tuple containing all the parameter values required to send email
        email_info = (self.sender,self.mail_list,subject,body,body_format,importance,attachment)
        
        #SQL Query to be executed which sends the email
        self.cursor.execute("""EXEC msdb.dbo.sp_send_dbmail 
                            @profile_name = ?, 
                            @recipients = ?, 
                            @subject = ?, 
                            @body = ?, 
                            @body_format = ?, 
                            @importance = ?,
                            @file_attachments = ?"""
                            , email_info)
        self.conn.commit()
    
    def _trigger_alarm(self,dataframe,imeinumber,sensor_info,subject,alarm_type,trigger_index,alarm_color):
        
        '''
        Prepare and send email for a given alarm 
        
        Parameters:
            dataframe: <class 'pandas.core.frame.DataFrame'>, A DataFrame container from the Pandas module
            which holds the latest 12 readings to be analyzed for a given imeinumber
            imeinumber: string, The IMEINumber of the SOS Device
            sensor_info: list, List containg the Borough, MSPlate, StructureType, StructureNumber of a 
            given SOS Device
            subject: str, subject of the email
            alarm_type: str, The type of alarm triggered i.e Tamper or Temperature 
        '''
        
        body = ''
        table_list = []
        TABLE_CAPTIONS = ['Alarm Info','Structure Info','Recent Readings','Cable Info']
        DATE = str(datetime.date.today())
        
        #create a new entry for the alarm in the sos.AlarmsMK2 table
        alarm_id = self._create_mk2_alarm(imeinumber,alarm_type)
                
        #Draw tables
        table_list.append(self._get_alarm_info_table(alarm_id))
        table_list.append(self._get_structure_info_table(sensor_info))
        table_list.append(self._draw_table(dataframe,title = 'Recent Readings',trigger_reading=trigger_index,kolor=alarm_color))
        table_list.append(self._get_cable_info_table(sensor_info))
        
        os.chdir('Reports')
        pdf_file_name = "Tamper"+imeinumber+DATE+".pdf"
        pdf = PdfPages(pdf_file_name)
        
        for table in table_list:
            #Append table html to the body of the paragraph
            body += "<h1>",TABLE_CAPTIONS[table_list.index(table)],"</h1>","\n"
            body += table[0]+"\n" 
            pdf.savefig(table[1])

        pdf.close()                    
        os.chdir('..')
        
        #Send email
        self._send_email(subject,body,attachment = pdf_file_name)
        clear_time,last_notification_sent = datetime.datetime.now()
        self.cursor.execute("UPDATE FIS_CONED.sos.AlarmsMK2 SET ClearTime = ?,LastNotificationSent = ? WHERE AlarmID = ?",[alarm_id,clear_time,last_notification_sent])        
        
        #MARK DATA ANALYZED (ADD ONCE SCRIPT PASSES TESTING)
    
    def _flat_temp_test(dataframe,threshold = 0):
    
        pass
    
        
        
    def _flat_tamper_test(self,dataframe):
        
        """
        Conducts the flat tamper test which checks if there have been two consecutive 'True' reading 
        and the humidity is lower than 80
        
        Parameters:
            
            dataframe: <class 'pandas.core.frame.DataFrame'>, A DataFrame container from the Pandas module
            which holds the latest 12 readings to be analyzed for a given imeinumber
        """
        
        imeinumber = str(dataframe.loc[0]['IMEINumber'])
        subject = 'Tamper Alarm Notification_' + imeinumber
        alarm_type = 'Tamper'
        
        #Itirate through all 12 readings        
        for row in range(len(dataframe) - 1):
           
            #and check if the current reading and the next one are both 'True' AND the humidity of the current reading is below 80
            if(dataframe.loc[row,'Tamper'] == True and dataframe.loc[row + 1,'Tamper'] == True) and dataframe.loc[row,'Humidity'] < 85:
               
                #Retrieve sensor info for the IMEINumber
                sql_sensor_info = """ SELECT Borough, MSPlate, StructureType, StructureNumber
                                      FROM FIS_CONED.sos.SensorLocations
                                      WHERE IMEINumber = ?"""
                dataframe_sensor_info = pandas.read_sql(sql_sensor_info,self.conn,params = [imeinumber])
                sensor_info = dataframe_sensor_info.astype(str).values[0]
                
                if(self.isEmpty(sensor_info)):
                    #Send special email detailing the missing info
                    
                    body = self._draw_table(dataframe,title = 'Recent Readings')
                    body_text = """'Hey Joe,\nHere is an SOS sensor with missing structure info.
                    It triggered the Tamper alarm.(This is a test the body of this
                    email is not final :)\n\n' """
                    
                    self._send_email('Missing StructureInfo--' +imeinumber, body_text + body[0])
                    break
                    
                else:
                    #Send regular alarm email    
                    self._trigger_alarm(dataframe,imeinumber,sensor_info,subject,alarm_type)
                    break
                       
    
    def _flat_stray_volatage_test(data_frame):
        pass
    def analyze(self):
#        '''
#        Retrives the latest un-analyzed SOS data and breaks it up by IMEINumbers and 
#        runs the specified tests
#        
#        '''
#        
#        sql_recent_imein = """SELECT DISTINCT IMEINumber FROM FIS_CONED.sos.Sensordata
#                           WHERE ProperData = 't'
#                           AND FactoryData = 'f'
#                           AND Analyzed = 0
#                           AND MeasurementTime > '2017-03-20 00:00:00:000' """
#        dataframe_recent_imein = pandas.read_sql(sql_recent_imein,self.conn)
#        
#        for imein in dataframe_recent_imein.values:
#            
#            sql_recent_data = """SELECT TOP 12 * FROM FIS_CONED.sos.SensorData 
#                              WHERE IMEINumber = ? 
#                              ORDER BY MeasuremenTime desc;"""
#            dataframe_recent_data = pandas.read_sql(sql_recent_data,self.conn,params = [imein[0]])
#            
#            self._flat_tamper_test(dataframe_recent_data)
        
        sql = """ Select TOP 12 * FROM FIS_CONED.sos.SensorData WHERE
              IMEINumber = '13108003859994' Order by MeasurementTime desc;"""
              
        df = pandas.read_sql(sql,self.conn)
        
        self._flat_tamper_test(df)
        

if __name__ == "__main__":
    
    EntireTeam = SOSAlarm()
    
    SQL = """SELECT TOP 12 MeasurementTime, FirmwareVersion, Temperature, SmokeDetected, CO, Barometer, Humidity,Flood,Battery, Tamper,
Methane, RSSI, StrayVoltage FROM FIS_CONED.sos.SensorData 
WHERE IMEINumber = '13108003867567' and MeasurementTime BETWEEN '2019-06-23' and '2019-06-26';"""

    df = pandas.read_sql(SQL,EntireTeam.conn)
    
    table = EntireTeam._draw_table(df,trigger_reading = 1)
    file  = open('test.txt','w')
    file.write(table[0])
    
    file.close()