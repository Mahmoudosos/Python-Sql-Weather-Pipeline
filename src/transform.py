import json
import logging
import os
from datetime import datetime
from pathlib import Path
import re
# Reading the data:

def transform_data(filepath = None,data_file = "data",process_data_file ="processed"):
    logging.info("Starting the transformation process")
    if Path(filepath).exists() is False:
        logging.warning("The file path is not correct. Please re-inter the file path")
        return
    with open(filepath,"r") as r:
        data = json.load(r)
    # Data Validation:
    try:
        for i in ["location","current"]:
            if i not in data.keys():
                raise ValueError(f"{i} is not here")
        for i in ["name","country","region","localtime"]:
            if i not in data["location"].keys():
                raise ValueError(f"{i} is not herer")
        for i in ["astro","temperature"]:
            if i not in data["current"].keys():
                raise ValueError(f"{i} is not here")
        for i in ["sunrise","sunset","moonrise","moonset"]:
            if i not in data["current"]["astro"].keys():
                raise ValueError(f"{i} is not here")
    except ValueError as e:
        logging.warning(f"The {e}")
        return

    # Data Conversion
    objects_time = [data['current']['astro']['sunrise'],
                    data['current']['astro']['sunset'],
                    data['current']['astro']['moonrise'],
                    data['current']['astro']['moonset'],
                    data['location']['localtime'][:-6]]

    time_format = '%I:%M %p'
    objects_time_formatted = []

    for i in objects_time[:-1]:
        try:
            objects_time_formatted.append(datetime.strptime(i, time_format))
        except ValueError as e:
            logging.warning(f"Error happens {type(e)} because of {i}")
            objects_time_formatted.append(None)

    str_format = '%H:%M'
    objects_str_formatted = []
    for i in objects_time_formatted:
        try:
            objects_str_formatted.append(i.strftime(str_format))
        except AttributeError as e:
            objects_str_formatted.append(None)
            logging.warning(f"Error happens {type(e)} because of {i}")
    objects_str_formatted.append(objects_time[-1])
    daily_weather_data = {"city":data['location']['name'],
                          "country": data['location']['country'],
                          "region": data['location']['region'],
                          "temperature":data['current']['temperature'],
                          "date":data['location']['localtime'][:-6],
                          "observation_time":data['location']['localtime'][-5:],
                          "sunrise":objects_str_formatted[0],
                          "sunset":objects_str_formatted[1],
                          "moonrise":objects_str_formatted[2],
                          "moonset":objects_str_formatted[3],
                          }
    temp = daily_weather_data["temperature"]
    if temp <= 10:
        daily_weather_data["condition"] = "cold"
    elif temp > 10 and temp <= 30:
        daily_weather_data["condition"] ="good"
    elif temp > 30 and temp <= 40:
        daily_weather_data["condition"] ="hot"
    elif temp > 40:
        daily_weather_data["condition"] ="very hot"
    else:
        logging.warning("The temperature field is not correct ")
        return

    parent_path = Path(__file__).resolve().parent.parent/data_file/process_data_file

    if Path(parent_path).exists() is False:
        parent_path.mkdir(parents=True,exist_ok=True)

    extract_date= re.findall("....-..-..",Path(filepath).name)[0]
    extract_city =re.findall("^.*?(?=_)",Path(filepath).name)[0]
    transform_file_name = f"{extract_city}_weather_{extract_date}_transformed.json"
    transform_file_path = Path(parent_path)/transform_file_name

    with open (transform_file_path,"w") as write_transformed_data:
            write_transformed_data.write(json.dumps(daily_weather_data))

    logging.info("The processed file have been written.")
    logging.info("The transformation process is done")

    return transform_file_path