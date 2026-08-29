# 1. Import libraries
import requests
import pyodbc
import logging
from datetime import datetime
import os
from dotenv import load_dotenv


# 2. Getting the Data:
API_KEY = os.environ.get("API_KEY")
My_DRIVER = os.environ.get("My_DRIVER")
My_SERVER = os.environ.get("My_SERVER")
My_DATABASE = os.environ.get("My_DATABASE")
User_Agent = os.environ.get("My_User_Agent")

logging.basicConfig(filename="API_log.log",level=logging.INFO)
url_1 = f"http://api.weatherstack.com/current?access_key={API_KEY}&query=Cairo"
report = requests.get(url = url_1, headers = {"User-Agent":User_Agent})
data = report.json()
conn_str = (
    fr'DRIVER={{{My_DRIVER}}};'
    fr'SERVER={My_SERVER};'
    fr'DATABASE={My_DATABASE};'
    r'Trusted_Connection=yes;'
    r'Encrypt=no;'
)
cnxn = pyodbc.connect(conn_str)
cursor = cnxn.cursor()


# 3. Data Conversion
city, country, region, temperature, date, observation_time = [data['location']['name'], data['location']['country'],
                                                              data['location']['region'],
                                                              data['current']['temperature'],
                                                              data['location']['localtime'][:-6],
                                                              data['location']['localtime'][-5:]]

objects_time = [data['current']['astro']['sunrise'],
                data['current']['astro']['sunset'],
                data['current']['astro']['moonrise'],
                data['current']['astro']['moonset'],
                data['location']['localtime'][:-6]]

time_format = '%I:%M %p'
objects_time_formated = []

for i in objects_time[:-1]:
    try:
        objects_time_formated.append(datetime.strptime(i, time_format))
    except ValueError as e:
        print(type(e))
        objects_time_formated.append('NULL')
    continue

str_format = '%H:%M'
objects_str_formated = []
for i in objects_time_formated:
    try:
        objects_str_formated.append(i.strftime(str_format))
    except AttributeError as e:
        objects_str_formated.append('NULL')
        print(type(e))
    continue
objects_str_formated.append(objects_time[-1])

# 4. Creating the tables:
cursor.execute(""" IF OBJECT_ID('DAILY_Egypt_WEATHER') IS NULL CREATE TABLE DAILY_EGYPT_WEATHER(
ID INT IDENTITY CONSTRAINT PK_WEATHER_ID PRIMARY KEY,
CITY NVARCHAR(25),
COUNTRY NVARCHAR(25),
REGION NVARCHAR(25),
TEMPERATURE INT,
DATE DATE CONSTRAINT UQ_ID_Date_Weather UNIQUE,
[OBSERVATION TIME] TIME,
[WEATHER CONDITION] NVARCHAR(25)
)
""")
cursor.commit()


cursor.execute("""IF OBJECT_ID('DAILY_EGYPT_OBJECT_TIME') IS NULL CREATE TABLE DAILY_EGYPT_OBJECT_TIME(
ID INT CONSTRAINT UQ_ID_OBJECT_TIME UNIQUE ,
SUNRISE TIME,
SUNSET TIME,
MOONRISE TIME,
MOONSET TIME,
Date Date CONSTRAINT UQ_DATE_OBJECT UNIQUE
)
""")
cursor.commit()


# 5. Importing Data:
cursor.execute("""INSERT INTO DAILY_EGYPT_WEATHER(CITY,COUNTRY,REGION,TEMPERATURE,DATE,[OBSERVATION TIME]) 
                   VALUES(?,?,?,?,?,?)""",
               [city,country,region,temperature,date,observation_time])
cursor.commit()
cursor.execute("""
UPDATE DAILY_EGYPT_WEATHER 
SET [WEATHER CONDITION] = CASE 
WHEN TEMPERATURE <= 10 THEN 'COLD' 
WHEN TEMPERATURE >10 AND TEMPERATURE <=30 THEN 'GOOD' 
WHEN TEMPERATURE >30 AND TEMPERATURE <40 THEN 'HOT'
WHEN TEMPERATURE >40 THEN 'VERY HOT'
END
""")
cursor.commit()
logging.info(f"The insertion date is {datetime.now()} for DAILY_Egypt_WEATHER ")

cursor.execute("""
INSERT INTO DAILY_EGYPT_OBJECT_TIME(ID,SUNRISE,
SUNSET,
MOONRISE,
MOONSET,
Date) 
VALUES(@@IDENTITY,?,?,?,?,?)
"""
,objects_str_formated)
cursor.commit()
logging.info(f"The insertion date is {datetime.now()} for DAILY_EGYPT_OBJECT_TIME")
