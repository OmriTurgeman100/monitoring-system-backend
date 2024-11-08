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
    "alphacorp 8.8.4.4",
    "securecloud 1.0.0.1",
    "fastdns 208.67.220.220",
    "nextgen 9.9.9.10",
    "loopback 127.0.0.2",
    "linuxhub 127.0.8.1",
    "techsoft 13.107.43.16",
    "cloudgiant 13.248.119.2",
    "skynet 20.45.17.4",
    "fruittech 17.253.145.11"
]


data = []

if __name__ == "__main__":
    while True:
        processes = []
        for address in addresses:
            title, ip = address.split(" ")
            report_name = title + ip
            process = Process(target=ping, args=(report_name, ip))
            process.start()
            processes.append(process)

            totoal_report = f'"{address}, {ip}",'
            print(totoal_report)
            
            data.append(totoal_report)

        for process in processes:
            process.join()





