from dotenv import load_dotenv
import pyodbc
import os
import json
import logging
from datetime import datetime
def load_data(transformed_data_file = None):
    # Reading the Transforming data
    logging.info("Starting the Load process")
    with open(fr"..\data\processed\{transformed_data_file}", "r") as r:
        str_data = r.read()
    transformed_data_json = json.loads(str_data)

    # Reading the environment variables
    load_dotenv()
    My_DRIVER = os.environ.get("My_DRIVER")
    My_SERVER = os.environ.get("My_SERVER")
    My_DATABASE = os.environ.get("My_DATABASE")

    # connect to the DB:
    conn_str = (
        fr'DRIVER={{{My_DRIVER}}};'
        fr'SERVER={My_SERVER};'
        fr'DATABASE={My_DATABASE};'
        r'Trusted_Connection=yes;'
        r'Encrypt=no;'
    )
    cnxn = pyodbc.connect(conn_str)
    cursor = cnxn.cursor()

    # Creating the tables:
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
    d = cursor.execute("""SELECT * FROM DAILY_EGYPT_WEATHER WHERE DATE = ?""", transformed_data_json[0]["date"]).fetchone()
    cursor.commit()

    if d is not None:
        logging.warning("You are loading duplicated data")
        return "You are loading duplicated data"
    else:
        # Importing Data:
        cursor.execute("""INSERT INTO DAILY_EGYPT_WEATHER(CITY,COUNTRY,REGION,TEMPERATURE,DATE,[OBSERVATION TIME]) 
                           VALUES(?,?,?,?,?,?)""",list(transformed_data_json[0].values())
                       )
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
        ,list(transformed_data_json[1].values()))
        cursor.commit()
        logging.info(f"The insertion date is {datetime.now()} for DAILY_EGYPT_OBJECT_TIME")
        logging.info(f"the load process is done")
        return "The Load process is finished successfully"