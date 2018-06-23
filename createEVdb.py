""" 
@author: lingesther

Last Modified:5 June 2018

Overview:
This script creates an SQL database of EV Charge Data using data collected from the ChargePoint API.
Note: dates recorded are in UTC.

Instructions:
- Insert your organization's username and password in the main() function
- To update the database with new data, modify the "startTime" and "endTime" parameters.
- Each call returns a maximum of 100 sessions.
- Set the startTime as the beginning of the day. Currently assumes no more than 100 sessions per day

Dependencies:
1. Uses functions from lib/dblib.py.

Additional Package Requirements:
1. zeep (https://github.com/mvantellingen/python-zeep)
2. sqlite3 (https://docs.python.org/2/library/sqlite3.html?highlight=sqlite3#module-sqlite3)


"""
import sqlite3
from sqlite3 import Error
import os
import sys
sys.path.append("lib/")

from zeep import Client
from zeep.wsse.username import UsernameToken
from datetime import datetime, timedelta

from dblib import create_connection, create_table
from dblib import makeStationAPIcall, makeUsageAPIcall



def main():
	### Note 1 to user: If database already exists, set boolUpdateStations to False
	boolUpdateStations = True
	boolUpdateSessions = True

	### Note 2 to user: Adjust startTime below. Make sure to set it to be after the most recent record in the database.
	startTime = datetime(2014, 1, 01, 00, 00, 00)
	endTime   = datetime(2014, 1, 10, 00, 00, 00) 

	#### Preliminaries ####
	### Note 3 to user: Adjust path to database below.
	database = "chargePoint.db"

	### Note 4: insert your organization's username and password below
	username = ""
	password = ""

	wsdl_url = "https://webservices.chargepoint.com/cp_api_5.0.wsdl"
	client = Client(wsdl_url, wsse=UsernameToken(username, password))


	#### Define tables in database
	user_table_sql = """ CREATE TABLE IF NOT EXISTS
						user(
								userID integer PRIMARY KEY
							);"""
	payment_table_sql = """ CREATE TABLE IF NOT EXISTS
						payment(
								credentialID text PRIMARY KEY
						);"""
	pricing_table_sql = """ CREATE TABLE IF NOT EXISTS
						pricing(
								pricingID integer PRIMARY KEY AUTOINCREMENT,
								Type text,
								startTime text,
								endTime text,
								minPrice numeric,
								maxPrice numeric,
								initialUnitPriceDuration text,
								unitPricePerHour numeric,
								unitPricePerHourThereafter text,
								unitPricePerSession numeric,
								unitPricePerKWh numeric
						);"""
	station_table_sql = """ CREATE TABLE IF NOT EXISTS
						station(
								stationID text PRIMARY KEY,
								stationModel text,
								stationActivationDate text,
								numPorts integer,
								Address text,
								City text,
								State text,
								postalCode text,
								pricingID integer,
								FOREIGN KEY (pricingID) REFERENCES pricing(pricingID)
						);"""
	port_table_sql = """ CREATE TABLE IF NOT EXISTS
						port(
								portID integer PRIMARY KEY,
								stationID text,
								portNumber integer,
								Level text,
								Connector text,
								Voltage integer,
								Current integer,
								Power numeric,
								FOREIGN KEY (stationID) REFERENCES station(stationID)
						);"""
	session_table_sql = """ CREATE TABLE IF NOT EXISTS
						session(
								sessionID integer PRIMARY KEY,
								startTime text,
								endTime text,
								Energy numeric,
								stationID text,
								userID integer,
								credentialID text,
								portNumber integer,
								FOREIGN KEY (stationID) REFERENCES station(stationID),
								FOREIGN KEY (userID) REFERENCES user(userID),
								FOREIGN KEY (credentialID) REFERENCES payment(credentialID)
						);"""


	#### Create tables if not already created
	conn = create_connection(database)
	if conn is not None:
		## create the USER table
		create_table(conn, user_table_sql)
		## create the PAYMENT table
		create_table(conn, payment_table_sql)
		## create the SESSION table
		create_table(conn, session_table_sql)
		## create the STATION table
		create_table(conn, station_table_sql)
		## create the PRICING table
		create_table(conn, pricing_table_sql)
		## create the PORT table
		create_table(conn, port_table_sql)
		print ("Tables Created")
	else:
		print("Error: unable to create database")

	#### Populate / update tables
	with conn:
		if boolUpdateStations == True:
			makeStationAPIcall(conn, client) ## can make some check: if len(getStations)

		if boolUpdateSessions == True:
			currTime = startTime
			while(currTime!=endTime):
				makeUsageAPIcall(conn, client, currTime)
				currTime += timedelta(days=1)

	#### Finish and close connection
	conn.commit() # save (commit) the changes
	conn.close()
	print "Completed task, saved to: ", database


if __name__== '__main__':
	main()
