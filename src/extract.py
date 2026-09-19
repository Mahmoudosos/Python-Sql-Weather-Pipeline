import requests
import logging
from dotenv import load_dotenv
from datetime import datetime
import json
import os
from pathlib import Path
from datetime import date

def extract_data(city = None,data_folder = "data",raw_data_folder = "raw"):
    logging.info("Starting the Extracting process.")
    if not city:
        logging.warning("City is not provided! Please enter a city")
        return

    load_dotenv()
    try:
        API_KEY = os.environ["API_KEY"]
        User_Agent = os.environ["My_User_Agent"]
    except KeyError as e:
        logging.warning(f"The {e} is missing")
        return

    url_1 = f"http://api.weatherstack.com/current?access_key={API_KEY}&query={city}"

    try:
        report = requests.get(url = url_1, headers = {"User-Agent":User_Agent}, timeout = 60)
        report.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.warning(f"Something went wrong with the connection to the website: {e}")
        return
    data = report.json()
    
    if not data:
        logging.warning("The data is empty")
        return
    # extracting the data into a file:
    date_today_extracted = date.today()
    parent_path = Path(__file__).resolve().parent.parent/data_folder/raw_data_folder
    if Path(parent_path).exists() is False:
        parent_path.mkdir(parents=True,exist_ok=True)

    datetime_extracted = f"{city}_weather_{date_today_extracted}_extracted.json"
    extracted_path = Path(parent_path)/datetime_extracted

    with open(extracted_path,"w",encoding="utf-8") as input_file:
        input_file.write(json.dumps(data))
    logging.info("The extracted file have been written")
    logging.info("The Extraction process is finished successfully")

    return extracted_path