import requests
import logging
from dotenv import load_dotenv
from datetime import datetime
import os
from extract import extract_data
from transform import transform_data
from load import load_data
logging.basicConfig(filename="..\logs\ETL.log",format="%(asctime)s - %(levelname)s - %(message)s",level=logging.INFO)
logging.info("Starting the ETL process")

raw_file_name = extract_data()
transformed_file_name = transform_data(raw_file_name)
load_data(transformed_file_name)

