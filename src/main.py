import logging
from pathlib import Path
from extract import extract_data
from transform import transform_data
from load import load_data

if __name__ == "__main__":
    log_path = Path(__file__).parent.parent/"logs"
    log_path.mkdir(exist_ok=True)
    logging.basicConfig(filename=Path(log_path)/"ETL.log",format="%(asctime)s - %(levelname)s - %(message)s",level=logging.INFO)

    logging.info("Starting the ETL process")

    raw_file_path = extract_data(city="Cairo")
    transformed_file_path = transform_data(raw_file_path)
    load_data(transformed_file_path)