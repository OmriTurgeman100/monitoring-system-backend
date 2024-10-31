import os
from multiprocessing import Process
import requests
import json
import logging
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")

def ping(report_name, ip):
    try:
        response = os.system("ping " + ip)

        if response == 0:
            value = 100
        else:
            value = 50

        reportId = report_name
        title = report_name
        description = 'ping test' 
        value = value

        send_data(reportId, title, description, value)
    except Exception as e:
        logging.error(f"Error in ping: {e}")

def send_data(reportId, title, description, value):
    try:
        api = "http://localhost/api/v1/post/reports"
        headers = {
            "Content-Type": "application/json"
        }
        body = {
            "report_id": reportId,
            "title": title,
            "description": description,
            "value": value
        }

        response = requests.post(api, data=json.dumps(body), headers=headers)
        current_time = datetime.now()
        logging.info(f"Sent report {reportId}: {title}, {description}, {value}, Status: {response.status_code}, Time: {current_time}")
        print("sent")
    except Exception as e:
        logging.error(f"Error in send_data: {e}")

addresses = [
    "google 8.8.8.8",
    "cloudflare 1.1.1.1",
    "opendns 208.67.222.222",
    "quad9 9.9.9.9",
    "localhost 127.0.0.1",
    "ubuntu 127.0.7.1",
    "microsoft 13.107.42.14",
    "aws 13.248.118.1",
    "azure 20.44.16.3",
    "apple 17.253.144.10"
]

if __name__ == "__main__":
    while True:
        processes = []
        for address in addresses:
            title, ip = address.split(" ")
            report_name = title + ip
            process = Process(target=ping, args=(report_name, ip))
            process.start()
            processes.append(process)

        for process in processes:
            process.join()
