import requests
import time
import logging
import json
from datetime import datetime
from multiprocessing import Process

logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")

def black_box_script(report_id, title, description, value):
    try:
        response = requests.get("https://www.udemy.com/")
        status = response.status_code

        api = "http://localhost/api/v1/post/reports"

        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "report_id": report_id,
            "title": title,
            "description": description,
            "value": 404
        }

        response = requests.post(api, data=json.dumps(body), headers=headers)
        print(response.status_code)
        current_time = datetime.now()
        logging.info(f"sent report, report id: {report_id}, title: {title}, description: {description}, value: {value}, time: {current_time}")

    except Exception as e:
        print(e)



if __name__ == "__main__":
    with open("data.json") as pings: # * open the json file once.
        pings_data = json.load(pings)

        processes = []
        while True:
            for item in pings_data:
                title = item["title"]
                ip = item["ip"]

                print(title, ip)

       

