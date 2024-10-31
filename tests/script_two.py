import requests
import time
import json

def black_box_script():
    try:
        response = requests.get("https://www.udemy.com/")
        status = response.status_code

        api = "http://localhost/api/v1/post/reports"

        headers = {
            "Content-Type": "application/json"
        }

        report_id = "udemy"
        title = "udemy"
        description = "udemy"
        value = status

        body = {
            "report_id": report_id,
            "title": title,
            "description": description,
            "value": 404
        }

        response = requests.post(api, data=json.dumps(body), headers=headers)
        print(response.status_code)

    except Exception as e:
        print(e)

while True:
    black_box_script()
    time.sleep(1)