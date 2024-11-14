import requests
import time
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")
def black_box_script():
    try:

        api = "http://localhost/api/v1/post/reports"

        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "report_id": 'sample report id',
            "title": 'sample report title',
            "description": 'sample report description',
            "value": 100
        }

        response = requests.post(api, data=json.dumps(body), headers=headers)
        print(response.status_code)

        print(body["report_id"], body["title"], body["description"], body["value"])

    except Exception as e:
        print(e)

while True:
    black_box_script()
    # time.sleep(1)