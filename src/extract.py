import requests
import logging
from dotenv import load_dotenv
from datetime import datetime
import json
import os
def extract_data():
    load_dotenv()
    API_KEY = os.environ.get("API_KEY")

    url_1 = f"http://api.weatherstack.com/current?access_key={API_KEY}&query=Cairo"

    User_Agent = os.environ.get("My_User_Agent")
    report = requests.get(url = url_1, headers = {"User-Agent":User_Agent}, timeout = 60)

    if report.status_code != 200:
        logging.Warning("Extract Problem: status code is not equal to 200")
        return

    data = report.json()

    # extracting the data into a file:
    datetime_extracted = str.replace(str(datetime.now()),":","-")
    with open(rf"..\data\raw\{datetime_extracted}_extracted.json","w",encoding="utf-8") as input_file:
        input_file.write(json.dumps(data))

    with open(rf"..\data\raw\{datetime_extracted}_extracted.json","r") as reading_input_file:
        r = reading_input_file.read(1)
        if not r:
            logging.warning("Extract Problem: The input file is empty")
            os.remove(rf"..\data\raw\{datetime_extracted}_extracted.json")
            logging.info("Extract: The empty input file has been deleted")
            return
        else:
            logging.info(rf"The Extract process is done. Here's the input file name: {datetime_extracted}_extracted.json")
    return f"{datetime_extracted}_extracted.json"