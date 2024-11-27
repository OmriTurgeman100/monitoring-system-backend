import requests
import time
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")
def black_box_script():
    try:
        response = requests.get("https://example.com/")
        status = response.status_code

        api = "http://localhost/api/v1/post/reports"

        headers = {
            "Content-Type": "application/json"
        }

        report_id = "example"
        title = "example"
        description = "example"
        value = status

        body = {
            "report_id": report_id,
            "title": title,
            "description": description,
            "value": value
        }

        response = requests.post(api, data=json.dumps(body), headers=headers)
        print(response.status_code)
        current_time = datetime.now()
        # logging.info(f"sent report, report id: {report_id}, title: {title}, description: {description}, value: {value}, time: {current_time}")

    except Exception as e:
        print(e)

while True:
    black_box_script()
    # time.sleep(1)