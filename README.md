# fronius-json-tools
Python tools to work with the json data of the Fronius Solar API


# Goals
* Python cron script that fetches all available live data of the datalogger and saves it into a sqlite db
* Python script that import the datalogger archive data into the sqlite db
* Generate relevant graphs from db
* iOS app and today widget that shows live data from datalogger

# Relevant Graphs
* Battery Charge throughout the day
* 


# API Links
http://fronius/solar_api/v1/GetActiveDeviceInfo.cgi?DeviceClass=System
http://fronius/solar_api/v1/GetInverterInfo.cgi
http://fronius/solar_api/v1/GetInverterRealtimeData.cgi?Scope=System
http://fronius/solar_api/v1/GetLoggerInfo.cgi
http://fronius/solar_api/v1/GetLoggerLEDInfo.cgi
http://fronius/solar_api/v1/GetMeterRealtimeData.cgi?Scope=System
http://fronius/solar_api/v1/GetPowerFlowRealtimeData.fcgi
http://fronius/solar_api/v1/GetStorageRealtimeData.cgi?Scope=System

# Notes on Data
* ActiveDeviceInfo: Dependent on the hardware, should never change
* InverterInfo: Mostly dependend on Hardware, Configuration, should seldome change, except status and error code
* InverterRealtimeData: All data also available from PowerFlowRealtimeData.
  PAC = abs(P_Load + P_Grid)
* LoggerInfo: Mostly dependend on Hardware, Configuration, should seldom change
* LoggerLEDInfo: Some minor status infos, should seldom change
* MeterRealimeData: Interesting Data is here
* PowerFlowRealtimeData: More interesting stuff
* StorageRealtimeData: Interesting stuff about the battery