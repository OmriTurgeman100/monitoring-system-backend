import os
import requests
import json

class ping:
    def __init__(self, report_name, ip):
        self.report_name = report_name
        self.ip = ip
        self.value = None

        self.ping_method()

        self.send_results()

    def ping_method(self):
        try:
            response = os.system(f"ping {self.ip}")

            if response == 0:
                self.value = 100
            else:
                self.value = 50
        except Exception as e:
            print(e)

    def send_results(self):
        try:
            api = "http://localhost/api/v1/post/reports"

            headers = {
                "Content-Type": "application/json"
            }

            body = {
                "report_id": self.report_name,
                "title": self.report_name,
                "description": self.report_name,
                "value": self.value
            }

            response = requests.post(api, data=json.dumps(body), headers=headers)
            print("sent")
            print(response.status_code)
        except Exception as e:
            print(e)

addresses = [
    "Google 8.8.8.8",
    "Localhost 127.0.0.1",
    "Router 192.168.1.1",
    "Yahoo yahoo.com",
    "Cloudflare 1.1.1.1",
    "Ubuntu 127.0.16",
    "Example example.com",
    "DNS 8.8.4.4",
    "Network 192.168.0.1",
    "TestServer 120.133.31.1"
]

for address in addresses:
    dns, ip = address.split(" ")
    report_name = dns + ip

    ping(report_name, ip)
  
