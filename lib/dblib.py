""" 
@author: lingesther
- functions for creating, defining and populating the ChargePoint EV Data database
- use with createEVdb.py
"""

import sqlite3
from sqlite3 import Error
from zeep import Client
from zeep.wsse.username import UsernameToken
from datetime import timedelta

###########################################################################
###### Auxillary functions for creating and connecting to database ########
def create_connection(db_file):
	""" create a database connection to a SQLite database specfied by db_file 
		param: db_file: database file
		return: Connection object or None
	"""
	try:
		conn = sqlite3.connect(db_file)
		return conn
	except Error as e:
		print(e)
		return None

def create_table(conn, create_table_sql):
	""" create a table from the create_table_sql statement
		params: conn: Connection Object
				create_table_sql: a CREATE TABLE statement
	"""
	try:
		c = conn.cursor()
		c.execute(create_table_sql)
	except Error as e:
		print(e)

def execute_cmd(conn, sqlcmd):
	""" Execute the sqlcmd statement
		params: conn: Connection Object
				sqlcmd: An sql statement
		returns the rows returned by executing the statement
	"""	
	with conn:
		cur = conn.execute(sqlcmd)
		rows = cur.fetchall()
		return rows


###############################################################
###### Functions for pulling data from ChargePoint API ########
def makeUsageAPIcall(conn, client, tStart):
	"""
	Inputs:    tStart: Start time for API call in datetime format. 
						E.g. tStart=datetime(2018, 5, 30, 00, 00, 00)
	Note: the tEnd parameter will be set to the end of the day, e.g. datetime(2018, 5, 30, 23, 59, 59)
	"""
	print("Making usage API query..")
	tEnd = tStart + timedelta(hours=23, minutes=59, seconds=59)
	usageSearchQuery = {
		'fromTimeStamp': tStart,
		'toTimeStamp': tEnd,
	}
	data = client.service.getChargingSessionData(usageSearchQuery)
	# print("Number of records in time-frame: ", len(data.ChargingSessionData))

	## Fill Sessions Table
	for d in data.ChargingSessionData:
		## enclose in try-except to avoid TypeError: int() argument must be a string or a number, not 'NoneType'
		## when userID is None, and other errors
		try:
			row_session = [int(d.sessionID), d.startTime.strftime('%Y-%m-%d %H:%M:%S'), 
							d.endTime.strftime('%Y-%m-%d %H:%M:%S'), float(d.Energy), 
							str(d.stationID), int(d.userID), str(d.credentialID), int(d.portNumber)]
			add_rows_session_table(conn, row_session)
			row_user = [int(d.userID)]
			add_rows_user_table(conn, row_user)
			row_payment = [str(d.credentialID)]
			add_rows_payment_table(conn, row_payment)
		except:
			pass


def makeStationAPIcall(conn, client):
	print("Making station API query..")
	## Get station data
	searchQuery = {}
	stationData = client.service.getStations(searchQuery)
	numStations = len(stationData.stationData)

	## Fill Pricing Table Rows - assumes only one pricing model exists currently
	price = stationData.stationData[0].Pricing[0]
	row_pricing = [str(price.Type), str(price.startTime), str(price.endTime), 
					float(price.minPrice), float(price.maxPrice), str(price.initialUnitPriceDuration), 
					float(price.unitPricePerHour), str(price.unitPricePerHourThereafter),
					float(price.unitPricePerSession), float(price.unitPricePerKWh)]
	add_rows_pricing_table(conn, row_pricing)

	portCtr = 0
	priceID = 1
	for (idx,st) in enumerate(stationData.stationData):
		## Fill Station Table Rows
		row_station = [str(st.stationID), str(st.stationModel), 
						st.stationActivationDate.strftime('%Y-%m-%d %H:%M:%S'), int(st.numPorts), 
						str(st.Address), str(st.City), str(st.State), str(st.postalCode), priceID]
		add_rows_station_table(conn, row_station)

		## Fill Port Table Rows
		for (p,pt) in enumerate(st.Port):
			portCtr = portCtr+1
			row_port = [portCtr, str(st.stationID), p, str(pt.Level), str(pt.Connector), int(pt.Voltage), int(pt.Current), float(pt.Power)]
			add_rows_port_table(conn, row_port)

		## Checking for more than one pricing model
		if st.Pricing != stationData.stationData[idx-1].Pricing:
			print ("Warning: more than one pricing model!")

	# print("Finished filling station, port and pricing model!")




###############################################################
######### Functions for adding rows into each table ###########
def add_rows_user_table(conn, row):
	sql = ''' INSERT OR IGNORE INTO user(userID) 
					VALUES(?)'''
	cur = conn.cursor()
	cur.execute(sql, row)
	return cur.lastrowid	

def add_rows_payment_table(conn, row):
	sql = ''' INSERT OR IGNORE INTO payment(credentialID) 
				VALUES(?)'''
	cur = conn.cursor()
	cur.execute(sql, row)
	return cur.lastrowid	

def add_rows_session_table(conn, row):
	sql = ''' INSERT OR IGNORE INTO session(sessionID, startTime, endTime, Energy, 
								stationID, userID, credentialID, portNumber) 
				VALUES(?,?,?,?,?,?,?,?)'''
					 ##1 2 3 4 5 6 7 8
	cur = conn.cursor()
	cur.execute(sql, row)
	return cur.lastrowid

def add_rows_station_table(conn, row):
	sql = """ INSERT OR IGNORE INTO station(stationID, stationModel, stationActivationDate, 
								numPorts, Address, City, State, postalCode, pricingID) 
				VALUES(?,?,?,?,?,?,?,?,?) """
					 ##1 2 3 4 5 6 7 8 9
	cur = conn.cursor()
	cur.execute(sql, row)
	return cur.lastrowid	

def add_rows_pricing_table(conn, row):
	sql = ''' INSERT INTO pricing(Type, startTime, endTime,
								minPrice, maxPrice, initialUnitPriceDuration, 
								unitPricePerHour, unitPricePerHourThereafter,
								unitPricePerSession, unitPricePerKWh) 
				VALUES(?,?,?,?,?,?,?,?,?,?)'''
					 ##2 3 4 5 6 7 8 9 10 11
					 ## don't inlcude the AUTOINCREMENT ID
	cur = conn.cursor()
	cur.execute(sql, row)
	return cur.lastrowid	

def add_rows_port_table(conn, row):
	sql = ''' INSERT OR IGNORE INTO port(portID, stationID, portNumber, Level, Connector, Voltage, Current, Power) 
				VALUES(?,?,?,?,?,?,?,?)'''
					 ##1 2 3 4 5 6 7 8
	cur = conn.cursor()
	cur.execute(sql, row)
	return cur.lastrowid	


###### End functions for adding rows into each table ######
###########################################################














