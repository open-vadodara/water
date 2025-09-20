import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
from datetime import datetime
import os

URL = "https://vmc.gov.in/RainFallLevelSensor/RainLevel.aspx"
JSON_FILE = "rainfall_data.json"

def scrape_table():
    # Get the HTML page
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the rainfall table
    table = soup.find("table", {"id": "ContentPlaceHolder1_GridView1"})
    if not table:
        raise Exception("Could not find table on the page")

    # Parse into DataFrame
    df = pd.read_html(str(table))[0]

    # Convert to JSON records
    records = df.to_dict(orient="records")

    # Add a timestamp to each row
    timestamp = datetime.utcnow().isoformat()
    for r in records:
        r["scraped_at"] = timestamp

    return records

def append_to_json(new_records, file_path=JSON_FILE):
    # Load existing data
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Append new records
    data.extend(new_records)

    # Save back
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    new_data = scrape_table()
    append_to_json(new_data)
    print(f"Appended {len(new_data)} rows to {JSON_FILE}")
