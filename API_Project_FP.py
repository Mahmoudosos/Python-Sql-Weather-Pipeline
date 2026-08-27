# 1. Import libraries
import requests
import pyodbc
from datetime import datetime


# 2. Getting the Data:
API_KEY = "Enter_your_weatherstack_API"
My_DRIVER =  "Enter_your_Driver"
My_SERVER = r"Enter_your_Server"
My_DATABASE = "Enter_your_database"


url_1 = f"http://api.weatherstack.com/current?access_key={API_KEY}&query=Cairo"
User_1 = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0"
report = requests.get(url = url_1, headers = {"User-Agent":User_1})
data = report.json()
conn_str = (
    fr'DRIVER={{My_DRIVER}};'
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
                data['current']['astro']['moonset']]

time_format = '%I:%M %p'
objects_time_formated = []

for i in objects_time:
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

# 4. Creating the tables:
cursor.execute(""" IF OBJECT_ID('DAILY_Egypt_WEATHER') IS NULL CREATE TABLE DAILY_EGYPT_WEATHER(
ID INT IDENTITY CONSTRAINT PK_WEATHER_ID PRIMARY KEY,
CITY NVARCHAR(25),
COUNTRY NVARCHAR(25),
REGION NVARCHAR(25),
TEMPRATURE INT,
DATE DATE,
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
MOONSET TIME
)
""")
cursor.commit()


# 5. Importing Data:
cursor.execute("""INSERT INTO DAILY_EGYPT_WEATHER(CITY,COUNTRY,REGION,TEMPRATURE,DATE,[OBSERVATION TIME]) 
                   VALUES(?,?,?,?,?,?)""",
               [city,country,region,temperature,date,observation_time])
cursor.commit()
cursor.execute("""
UPDATE DAILY_EGYPT_WEATHER 
SET [WEATHER CONDITION] = CASE 
WHEN TEMPRATURE <= 10 THEN 'COLD' 
WHEN TEMPRATURE >10 AND TEMPRATURE <=30 THEN 'GOOD' 
WHEN TEMPRATURE >30 AND TEMPRATURE <40 THEN 'HOT'
WHEN TEMPRATURE >40 THEN 'VERY HOT'
END
""")
cursor.commit()


cursor.execute("""
INSERT INTO DAILY_EGYPT_OBJECT_TIME(ID,SUNRISE,
SUNSET,
MOONRISE,
MOONSET) 
VALUES(@@IDENTITY,?,?,?,?)
"""
,objects_str_formated)
cursor.commit()