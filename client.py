import requests
import json


json_data_list = [
    {
        "table_name": "date_dim",
        "exprs": [
            {
                "col": "d_moy",
                "op": "=",
                "value": "11"
            }
        ]
    },
    {
        "table_name": "item",
        "exprs": [
            {
                "col": "i_manufact_id",
                "op": "=",
                "value": "816"
            }
        ]
    }
]

url = 'http://127.0.0.1:5000/api' 
headers = {'Content-Type': 'application/json'}

for json_data in json_data_list:
    response = requests.post(url, data=json.dumps(json_data), headers=headers)

    if response.status_code == 200:
        result = response.json()["result"]
        print("Cardinality:", result)
    else:
        print('Failure:', response.status_code, response.text)