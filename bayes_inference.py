import argparse
import logging
import os
import time
import shutil
import numpy as np
import pandas as pd
import sys
from flask import Flask, request
sys.path.append('/home/ubuntu/yygs-projects/BayesCard')
from DataPrepare.join_data_preparation import prepare_sample_hdf
from DataPrepare.prepare_single_tables import prepare_all_tables
from Schemas.imdb.schema import gen_job_light_imdb_schema
from Testing.BN_training import train_DMV, train_Census, train_imdb, train_imdb_one
from Testing.BN_testing import evaluate_cardi, evaluate_cardinality_imdb_one, evaluate_cardinality_single_table, evaluate_cardinality_imdb
import json

app = Flask(__name__)
# table_names = ['catalog_page']
query_file_location = "/home/ubuntu/yygs-projects/BayesCard/new_sql/new_sql.json"

def construct_sql(table_name, exprs):
    sql = f"SELECT COUNT(*) FROM {table_name} WHERE "
    for i, expr in enumerate(exprs):
        col = expr["col"]
        op = expr["op"]
        value = expr["value"]
        sql += f"{col} {op} {value}"
        if i != len(exprs) - 1:
            sql += " AND "
    return sql
    
def inference(json_query):
    model_path = "/home/ubuntu/yygs-projects/BayesCard/new_model/"
    table_csv_path = "/home/ubuntu/yygs-projects/tpcds/data/"
    schema = gen_job_light_imdb_schema(table_csv_path)
    table_name = json_query["table_name"]
    exprs = json_query["exprs"]
    
    table = schema.table_dictionary[table_name]
    model = model_path + table_name + ".pkl"
    query_str = construct_sql(table_name, exprs)
    return evaluate_cardi(table, model, "exact", query_str)


@app.route('/api', methods=['POST'])
def handle_request():
    json_query = request.get_json()
    result = inference(json_query)
    return json.dumps({"result": result})

if __name__ == '__main__':
    app.run()