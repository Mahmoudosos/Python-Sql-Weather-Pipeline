# Python-Sql-Weather-Pipeline

It's a Python pipeline that extracts the weather data of a city using the API from the Weatherstack website by the request library in the `extract.py` and saves it in raw data in the `raw` folder and then does the validation and transformation using the regular Python in `transformation.py` and saves the output in the `processed` folder and finally loads the data in `load.py` using the pyodbc library to load the transformed weather data to the 2 tables to the SQL server. There is the `main.py` that runs the whole pipeline.

<img width="1079" height="476" alt="image" src="https://github.com/user-attachments/assets/68ce21a5-72ef-406b-b07a-788c9b6762ee" />

## Project Structure:

```
weather-pipeline/
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── main.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── logs/
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Pipeline Structure:

```
extract.py
    |

CityName_weather_Date_extracted.json
    |

transform.py
    |

CityName_weather_Date_transformed.json
    |

load.py
    |

- Creating DAILY_WEATHER and  DAILY_OBJECT_TIME tables (Optional)

- Inserting the data
```

## How to run the pipeline:

First, create a Weatherstack account and add enter your API KEY in the env file.

Second, you should enter your server, driver, and database in the env file.

Regarding this project, since I used the pyodbc library, it has different formats regarding the database and the driver that you are using. I used `Sql Server` with `ODBC Driver 18 for SQL Server`.

If you are going to use a different driver or database, it's better to have a look at the below website: <br/>

https://www.connectionstrings.com/

Third, just provide main.py with the city name, then run the script to start the pipeline.

## database schema:

```
Table DAILY_WEATHER:
  ID (PK)
  CITY
  COUNTRY
  REGION
  TEMPERATURE
  DATE
  [OBSERVATION TIME]
  [WEATHER CONDITION]

Table DAILY_OBJECT_TIME:
  ID (QK) (FK)
  CITY
  SUNRISE
  SUNSET
  MOONRISE
  MOONSET
  Date
```

A unique key will be created based on the Date and City columns in both tables to prevent duplicates.

## Possible Future Improvements

- Create some statistics based on the weather data.
