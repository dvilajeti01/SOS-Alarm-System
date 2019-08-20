USE FIS_CONED;

CREATE TABLE sos.AlarmTypes(
	ID int NOT NULL IDENTITY(1,1),
	Name varchar (50) NOT NULL,
	AlarmType varchar (50) NOT NULL,
	Description varchar (255),
	DateCreated date NOT NULL,
	CreatedBy varchar (64) NOT NULL,
	Active bit NOT NULL,
	PRIMARY KEY(ID),
	FOREIGN KEY (CreatedBy) REFERENCES FIS_CONED.sos.Users(Email)
);

CREATE TABLE sos.TestTypes(
	ID int NOT NULL IDENTITY(1,1),
	AlarmID int NOT NULL,
	TestType varchar (50) NOT NULL,
	ColumnCheck varchar (50) NOT NULL,
	Operation varchar (50) NOT NULL,
	Threshold varchar (50) NOT NULL,
	Rate int,
	PRIMARY KEY(ID),
	FOREIGN KEY (AlarmID) REFERENCES FIS_CONED.sos.AlarmTypes(ID),
	CONSTRAINT CHK_TestType CHECK (TestType  in ('Main','Conditional')),
	CONSTRAINT CHK_Operation CHECK (Operation in ('>','<','>=','<=','==','!=')),
	CONSTRAINT CHK_Rate CHECK (Rate >= 0)
);

CREATE TABLE sos.Alarms(
	ID int NOT NULL IDENTITY(1,1),
	AlarmID int NOT NULL,
	DateCreated datetime NOT NULL,
	IMEINumber varchar(48) NOT NULL,
	ReadingsStart datetime NOT NULL,
	ReadingsEnd datetime NOT NULL,
	PRIMARY KEY (ID),
	FOREIGN KEY(AlarmID) REFERENCES FIS_CONED.sos.AlarmTypes(ID),
	FOREIGN KEY(IMEINumber) REFERENCES FIS_CONED.sos.SensorLocations(IMEINumber)
);

CREATE TABLE sos.AlarmsTracked(
	DecisionID int NOT NULL IDENTITY(1,1),
	AlarmID int NOT NULL UNIQUE,
	ReviewedBy varchar(64) NOT NULL,
	ReviewedOn date NOT NULL,
	Decision varchar(5) NOT NULL,
	Reason varchar(255),
	PRIMARY KEY (DecisionID),
	FOREIGN KEY (AlarmID) REFERENCES FIS_CONED.sos.Alarms(ID),
	FOREIGN KEY (ReviewedBy) REFERENCES FIS_CONED.sos.Users(Email),
	CONSTRAINT CHK_Decision CHECK (Decision in ('True','False')),
);

CREATE TABLE sos.AlarmsTEST(
	ID int NOT NULL IDENTITY(1,1),
	AlarmID int NOT NULL,
	DateCreated datetime NOT NULL,
	IMEINumber varchar(48) NOT NULL,
	ReadingsStart datetime NOT NULL,
	ReadingsEnd datetime NOT NULL,
	PRIMARY KEY (ID),
	FOREIGN KEY(AlarmID) REFERENCES FIS_CONED.sos.AlarmTypes(ID),
	FOREIGN KEY(IMEINumber) REFERENCES FIS_CONED.sos.SensorLocations(IMEINumber)
);

CREATE TABLE sos.AlarmsTrackedTEST(
	DecisionID int NOT NULL IDENTITY(1,1),
	AlarmID int NOT NULL UNIQUE,
	ReviewedBy varchar(64) NOT NULL,
	ReviewedOn date NOT NULL,
	Decision varchar(5) NOT NULL,
	Reason varchar(255),
	PRIMARY KEY (DecisionID),
	FOREIGN KEY (AlarmID) REFERENCES FIS_CONED.sos.Alarms(ID),
	FOREIGN KEY (ReviewedBy) REFERENCES FIS_CONED.sos.Users(Email),
	CONSTRAINT CHK_DecisionTEST CHECK (Decision in ('True','False')),
);






