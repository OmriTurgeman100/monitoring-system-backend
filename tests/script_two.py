import requests
import time
import logging
import json
from datetime import datetime
from multiprocessing import Process
import os

logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")

def ping(report_id,title, ip, description):
    output = os.system(f"ping {ip}")

    if output == 0:
        value = 100
    else:
        value = 50

    send_to_api(report_id, title, description, value)

def send_to_api(report_id, title, description, value):
    try:

        api = "http://localhost/api/v1/post/reports"

        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "report_id": report_id,
            "title": title,
            "description": description,
            "value": value
        }

        response = requests.post(api, data=json.dumps(body), headers=headers)
        print(response.status_code)

        current_time = datetime.now()
        logging.info(f"sent report, report id: {report_id}, title: {title}, description: {description}, value: {value}, time: {current_time}, status_code: {response.status_code}")

    except Exception as e:
        current_time = datetime.now()
        logging.error(f"error is {e}, time: {current_time}")
        print(e)

if __name__ == "__main__":
    with open("data.json") as pings: # * open the json file once.
        pings_data = json.load(pings)

        processes = []
        while True:
            for item in pings_data:
                title = item["title"]
                ip = item["ip"]
                description = "pinging servers"
                report_id = f"{title} {ip}"

                process = Process(target=ping, args=(report_id, title, ip, description))
                process.start()
                processes.append(process)

            # Join processes after starting all of them
            for process in processes:
                process.join()



              

       

