INSERT 
INTO FIS_CONED.sos.AlarmTypes(Name,AlarmType,Description,DateCreated,CreatedBy,Active) 
VALUES 
	('Temperature','Flat','Check if any reading has exceed 122F',CONVERT(DATE,GETDATE()),'vilajetid@coned.com',1)
   ,('CO','Flat','Check if any reading has exceed 35 PPM',CONVERT(DATE,GETDATE()),'vilajetid@coned.com',1)
   ,('StrayVoltage','Flat','Check if any reading has exceed 5V',CONVERT(DATE,GETDATE()),'vilajetid@coned.com',1)
   ,('Humidity0','Constraint','Constraint check to flag a reading with a humidity value of 0',CONVERT(DATE,GETDATE()),'vilajetid@coned.com',1)
   ,('Humidity100','Constraint','Constraint check to flag a reading with a humidity value of 100',CONVERT(DATE,GETDATE()),'vilajetid@coned.com',1)
   ,('Temperature0','Constraint','Constraint check to flag a reading with a temperature value lees than 0',CONVERT(DATE,GETDATE()),'vilajetid@coned.com',1)
   ,('Temperature264','Constraint','Constraint check to flag a reading with a temperature value of 264.2',CONVERT(DATE,GETDATE()),'vilajetid@coned.com',1)
   ,('Barometer800','Constraint','Constraint check to flag a reading with a barometer reading less than 800',CONVERT(DATE,GETDATE()),'vilajetid@coned.com',1)
   ,('Barometer1200','Constraint','Constraint check to flag a reading with a barometer reading greater than 1200',CONVERT(DATE,GETDATE()),'vilajetid@coned.com',1)
   ,('Flood','Constraint','Constraint check to flaf a reading with a flood reading of True',CONVERT(DATE,GETDATE()),'vilajetid@coned.com',1);
							   
