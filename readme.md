# ChargePoint API database
Esther Ling, 2018

## Overview
This is a script to pull usage data from ChargePoint API and save it into an SQL database.

## Instructions
1. Insert your organization's username and password in the main() function.
2. Set the startTime and endTime as the beginning of the day, i.e. midnight 00:00:00. Example: datetime(2018, 1, 01, 00, 00, 00).
3. Edit the "startTime" and "endTime" parameters to the time range that you want to pull data from.
4. ChargePoint's API limits each call to a maximum of 100 sessions. I've coded this under the assumption that there are no more than 100 sessions per day (which you will need to modify if usage in your area is higher than this).

## Table Schema
The database schema can be found in a Google Slide (here)[https://docs.google.com/presentation/d/1P1bULtDGcgMSYChIWzFjT7LfT-BbQs-qWxjKsioeGKc/edit?usp=sharing].

## Example
(Todo: populate the Notebooks folder with a Jupyter notebook)

## Package Dependencies
1. zeep
2. sqlite3

## ChargePoint API Doc
https://na.chargepoint.com/UI/downloads/en/ChargePoint_Web_Services_API_Guide_Ver4.1_Rev4.pdf





