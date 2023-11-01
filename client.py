import requests
import json

# 定义JSON数据
json_data = {
    "table_name": "catalog_page",
    "exprs": [
        {
            "col": "cp_start_date_sk",
            "op": "=",
            "value": "2450815"
        },
        {
            "col": "cp_catalog_page_number",
            "op": ">=",
            "value": "30"
        }
    ]
}


url = 'http://127.0.0.1:5000/api' 
headers = {'Content-Type': 'application/json'}
response = requests.post(url, data=json.dumps(json_data), headers=headers)


if response.status_code == 200:
    result = response.json()["result"]
    print("Cardinality:", result)
else:
    print('请求失败:', response.status_code, response.text)