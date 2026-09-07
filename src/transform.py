import json
import logging
import os
from datetime import datetime
import ast
# Reading the data:

def transform_data(filename = None):
    with open(rf"..\data\raw\{filename}","r") as r:
        data = json.load(r)

    # Data Conversion
    daily_weather_data = {"city":data['location']['name'],
                          "country": data['location']['country'],
                          "region": data['location']['region'],
                          "temperature":data['current']['temperature'],
                          "date":data['location']['localtime'][:-6],
                          "observation_time":data['location']['localtime'][-5:]}

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
            print(f"Error happens {type(e)} because of {i}")
            objects_time_formated.append('NULL')
        continue

    str_format = '%H:%M'
    objects_str_formated = []
    for i in objects_time_formated:
        try:
            objects_str_formated.append(i.strftime(str_format))
        except AttributeError as e:
            objects_str_formated.append('NULL')
            print(f"Error happens {type(e)} because of {i}")
        continue
    objects_str_formated.append(objects_time[-1])

    objects_str_formated_dic = {"sunraise":objects_str_formated[0],
                                "sunset":objects_str_formated[1],
                                "moonraise":objects_str_formated[2],
                                "moonset":objects_str_formated[3],
                                "observation_time":objects_time[-1]}
    transformed_date = str.replace(str(datetime.now()),":","-")
    try:
        with open (rf"..\data\processed\{transformed_date}_transformed_data.json","w") as write_transformed_data:
            transformed_data = [daily_weather_data,objects_str_formated_dic]
            write_transformed_data.write(json.dumps(transformed_data))
        with open(rf"..\data\processed\{transformed_date}_transformed_data.json","r") as read_transformed_data:
            r = read_transformed_data.read(1)
        if not r:
            raise ValueError("The transformed data file is empty")
        else:
            logging.info(f"The transformation process finished successfully. here is the transformed file:{transformed_date}_transformed_data.json")
    except ValueError as e:
        logging.warning(f"{e}")
        os.remove(rf"..\data\processed\{transformed_date}_transformed_data.json")
        logging.info("The empty transformed data file is removed")
    return f"{transformed_date}_transformed_data.json"