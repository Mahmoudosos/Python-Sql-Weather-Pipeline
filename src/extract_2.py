from dotenv import load_dotenv
import pyodbc
import os
import json
import logging
from datetime import datetime
from pathlib import Path
def load_data(transformed_data_file = None):
    logging.info("Starting the Load process")

    if Path(transformed_data_file).exists() is False:
        logging.warning("The transformed data file is not there")
        return

    # Reading the Transforming data
    with open(transformed_data_file, "r") as r:
        str_data = r.read()
    transformed_data_json = json.loads(str_data)

    # Reading the environment variables
    load_dotenv()
    try:
        My_DRIVER = os.environ["My_DRIVER"]
        My_SERVER = os.environ["My_SERVER"]
        My_DATABASE = os.environ["My_DATABASE"]
    except KeyError as e:
        logging.warning(f"The {e} is missing!")
        return

    # connect to the DB:
    conn_str = (
        fr'DRIVER={{{My_DRIVER}}};'
        fr'SERVER={My_SERVER};'
        fr'DATABASE={My_DATABASE};'
        r'Trusted_Connection=yes;'
        r'Encrypt=no;'
    )
    try:
        cnxn = pyodbc.connect(conn_str)
    except pyodbc.Error as e:
        logging.warning(f"There's a problem with connection to the database. The problem is {e}")
        return

    cursor = cnxn.cursor()

    # Creating the tables:
    try:
        cursor.execute(""" IF OBJECT_ID('DAILY_WEATHER') IS NULL CREATE TABLE DAILY_WEATHER(
              ID INT IDENTITY CONSTRAINT PK_City_WEATHER_ID PRIMARY KEY,
              CITY NVARCHAR(25),
              COUNTRY NVARCHAR(25),
              REGION NVARCHAR(25),
              TEMPERATURE INT,
              DATE DATE,
              [OBSERVATION TIME] TIME,
              [WEATHER CONDITION] NVARCHAR(25),
              CONSTRAINT UQ_DATE_CITY_WEATHER UNIQUE (CITY,DATE)
              )
              """)
        cursor.execute("""IF OBJECT_ID('DAILY_OBJECT_TIME') IS NULL CREATE TABLE DAILY_OBJECT_TIME(
              ID INT CONSTRAINT UQ_ID_City_OBJECT_TIME UNIQUE,
              CITY NVARCHAR(25),
              SUNRISE TIME,
              SUNSET TIME,
              MOONRISE TIME,
              MOONSET TIME,
              Date Date,
              CONSTRAINT UQ_DATE_CITY_OBJECTS UNIQUE (CITY,DATE))
              """)
    except pyodbc.Error as e:
        cursor.rollback()
        logging.warning(f"Something happened while creating the tables. Which is: {e} ")
        return
    else:
        cursor.commit()
        d = cursor.execute("""select 1 from daily_weather;""").fetchone()
        return d
transformed_file_path = Path("C:\Interests\projects\Python-Sql-Weather-Pipeline\data\processed\Cairo_weather_2026-09-17_transformed.json")
load_data(transformed_file_path)