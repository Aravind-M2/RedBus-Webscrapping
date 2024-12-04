#### assigining values from the saved files ###########

import json
with open("route_bus_detail_dict.txt", 'r') as file1:
    route_bus_detail_dict = json.load(file1)
with open("route_travel_date_dict.txt", 'r') as file2:
    route_travel_date_dict = json.load(file2)



####################################### Pre-processing the data before inserting data into DB ###########################################

route_bus_prep = []
for r,i in route_bus_detail_dict.items():

    for j in i:
        tem = {}
        sr_present = 0
        for k,l in j.items():
            # primary key(id) ----- to be added in DB and it should be series type (self_incremental)
            
            tem['Bus Route Name'] = r
            tem['Bus Routes Link'] = route_travel_date_dict[r]['link']
            tem['Travel Date'] = route_travel_date_dict[r]['travel_date']

            if 'travels lh-24' in k:
                tem['Bus Name'] = l
            
            elif 'bus-type' in k:
                tem['Bus Type'] = l
            
            elif 'dp-time' in k:
                tem['Departing Time'] = l         #### change it as time --- data type
            
            elif 'dur l-color' in k:
                tem['Duration'] = l

            elif 'bp-time' in k:
                tem['Reaching Time'] = l         #### change it as time --- data type
                
            elif 'rating-sec' in k:
                tem['Star Rating'] = l
                
            elif 'rating' in k:
                tem['Star Rating'] = l
                    
            elif 'fare d-block' in k:
                tem['Price'] = l
                
            elif 'seat-left' in k:
                tem['Seat Availability'] = int(l.split()[0])  ##### use split and take the 1st value alone
    
        
        route_bus_prep.append(tem)


import pandas as pd

df_bus = pd.DataFrame(route_bus_prep) # list of dictionaries of bus details is conerted to dataframe


df_bus_backup = df_bus.copy()

from datetime import datetime, timedelta

df_bus["Travel Date"] = pd.to_datetime(df_bus["Travel Date"] + " 2024", format="%d %b %Y")

df_bus["Departing Time"] = pd.to_timedelta(df_bus["Departing Time"].str.extract(r"(\d{2}:\d{2})")[0] + ":00")

# df_bus["Duration"] = df_bus["Duration"].apply(lambda x: timedelta(hours=int(x.split("h")[0]), minutes=int(x.split("h")[1].split("m")[0])))
def parse_duration(duration):
    try:
        hours, minutes = map(int, duration.replace("h", "").replace("m", "").split()) # takes only the numbers as int and stores in hours and minutes
        return timedelta(hours=hours, minutes=minutes) # returns the time by using the extracted values
    except Exception:
        # Handle invalid values
        return timedelta(0) 

df_bus["Duration"] = df_bus["Duration"].apply(parse_duration) # changes the string to valid data type for time 

df_bus["Reaching Date"] = df_bus["Travel Date"] + df_bus["Departing Time"] + df_bus["Duration"] # calculates reaching time with date

df_bus["Starting Date"] = df_bus["Travel Date"] + df_bus["Departing Time"] # calculates starting date and time of the trip

df_bus['Star Rating'] = df_bus['Star Rating'].fillna('0')
df_bus['Star Rating'] = df_bus['Star Rating'].str.replace("New", '0')
df_bus['Star Rating'] = df_bus['Star Rating'].astype(float)
df_bus['Star Rating'] = df_bus['Star Rating'].apply(lambda x : '0' if x is None else x)
# df_bus['Star Rating'] = df_bus['Star Rating'].str.replace("New", '0')

df_bus["Price"] = df_bus["Price"].str.replace("INR ", "").astype(float)


df_bus_final = df_bus[['Bus Route Name', 'Bus Routes Link','Bus Name','Bus Type', 'Starting Date','Duration','Reaching Date', 'Star Rating', 'Price', 'Seat Availability']]

df_bus_final["Duration"] = df_bus_backup["Duration"].copy()
df_bus_final["Duration"] = df_bus_final["Duration"].astype(str)

#### inserting data into a table in Database ### postgesql

#!pip install psycopg2

import psycopg2

from psycopg2.extras import execute_values

conn = psycopg2.connect(
    database="Redbus",
    user="postgres",
    password="12345678",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

cur.execute(""" CREATE TABLE bus_routes (
id SERIAL PRIMARY KEY,
route_name TEXT not null,
route_link TEXT,
busname TEXT not null,
bustype TEXT,
departing_time TIME,
duration TEXT,
reaching_time TIME,
star_rating FLOAT,
price DECIMAL(10,2),
seats_available INT
)""") ###

#### data type --- DATETIME is not available in postgresql


conn.commit()

# Rename DataFrame columns to match the database table
df_bus_final.rename(columns={
    'Bus Route Name': 'route_name',
    'Bus Routes Link': 'route_link',
    'Bus Name': 'busname',
    'Bus Type': 'bustype',
    'Starting Date': 'departing_time',
    'Duration': 'duration',
    'Reaching Date': 'reaching_time',
    'Star Rating': 'star_rating',
    'Price': 'price',
    'Seat Availability': 'seats_available'
}, inplace=True)

columns = ', '.join(df_bus_final.columns)
table_name = 'bus_routes' ####
insert_query = f"INSERT INTO {table_name} ({columns}) VALUES %s"

# Convert DataFrame rows to a list of tuples
values = [tuple(row) for row in df_bus_final.to_numpy()]

# Use execute_values for efficient bulk inserts
execute_values(cur, insert_query, values)

conn.commit()

