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
              CITY NVARCHAR(35),
              COUNTRY NVARCHAR(35),
              REGION NVARCHAR(35),
              TEMPERATURE INT,
              DATE DATE,
              [OBSERVATION TIME] TIME,
              [WEATHER CONDITION] NVARCHAR(25),
              CONSTRAINT UQ_DATE_CITY_WEATHER UNIQUE (CITY,DATE)
              )
              """)
        cursor.execute("""IF OBJECT_ID('DAILY_OBJECT_TIME') IS NULL CREATE TABLE DAILY_OBJECT_TIME(
              ID INT CONSTRAINT UQ_ID_City_OBJECT_TIME UNIQUE CONSTRAINT FK_FK_OBJECT_WEATHER_ID  FOREIGN KEY REFERENCES DAILY_WEATHER(ID),
              CITY NVARCHAR(35),
              SUNRISE TIME,
              SUNSET TIME,
              MOONRISE TIME,
              MOONSET TIME,
              Date Date,
              CONSTRAINT UQ_DATE_CITY_OBJECTS UNIQUE (CITY,DATE)
              )
              """)
    except pyodbc.Error as e:
        cursor.rollback()
        logging.warning(f"Something happened while creating the tables. Which is: {e} ")

    else:
        cursor.commit()
    # Checking duplicates
    dup_val = cursor.execute("""SELECT * FROM DAILY_WEATHER WHERE DATE = ? AND CITY = ?""", transformed_data_json["date"],transformed_data_json["city"]).fetchone()
    cursor.commit()

    if dup_val is not None:
        logging.warning("You are loading duplicated data")
        return
    else:
        try:
            # Importing Data:
            cursor.execute("""
            DECLARE @@ID TABLE (num INT);
            
            INSERT INTO DAILY_WEATHER(CITY,COUNTRY,REGION,TEMPERATURE,DATE,[OBSERVATION TIME],[WEATHER CONDITION])
            OUTPUT INSERTED.ID INTO @@ID(num)
            VALUES(?,?,?,?,?,?,?);
                        
            INSERT INTO DAILY_OBJECT_TIME(ID,CITY,SUNRISE,SUNSET,MOONRISE,MOONSET,Date) 
            SELECT num,?,?,?,?,?,? FROM @@ID;""",[transformed_data_json["city"],
                                                 transformed_data_json["country"],
                                                 transformed_data_json["region"],
                                                 transformed_data_json["temperature"],
                                                 transformed_data_json["date"],
                                                 transformed_data_json["observation_time"],
                                                 transformed_data_json["condition"],
                                                 transformed_data_json["city"],
                                                 transformed_data_json["sunrise"],
                                                 transformed_data_json["sunset"],
                                                 transformed_data_json["moonrise"],
                                                 transformed_data_json["moonset"],
                                                 transformed_data_json["date"]])
        except pyodbc.Error as e:
            cursor.rollback()
            logging.warning(f"The insertion to a table have the problem: {e}")
            return
        else:
            cursor.commit()
            cursor.close()
            cnxn.close()
            logging.info(f"The insertion date is {datetime.now()}")
        logging.info(f"the load process is done")
        return "The load process is finished successfully"