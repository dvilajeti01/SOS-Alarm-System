# SOS(Structure Observation System) Alarms

  The goal of the sos alarms is primarily to analyze incoming data and alert the specified members of the DE(Distributed Enineering) team. The Alerts will provide information about the structure in which the sos box is located and a snapshot of the latest data including the reading that triggered the alarm.  

  To understand the code behind the alarms an explanation of SOS system is required.

## SOS Background

  SOS boxes are a predictive attempt at reducing structure events such as manhole explosions. SOS boxes take measurements of the environmet in which they reside. These measurements include but are not limited to Temperature, CO (carbon monoxide), and Stray Voltage. Given the SOS box capabilities a decison was made to place them in underground structures through out the NY boroughs. Roughly 4 thousand boxes have been installed though only ~3 thousand are in continuous communication at any given time. The boxes are manufactored by CNIGuard which also handles the communication between the boxes and ConEd. The communication includes an hourly upload of new data in the form of a .csv file located in ```\\m020diseng1\datadirs2\Secondary Analysis\RDX\CNIGuard ```. Here the file is imported by an SQL SISS Job created by 
