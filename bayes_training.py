import argparse
import logging
import os
import time
import shutil
import numpy as np
import pandas as pd
import sys
sys.path.append('/home/ubuntu/yygs-projects/BayesCard')
from DataPrepare.join_data_preparation import prepare_sample_hdf
from DataPrepare.prepare_single_tables import prepare_all_tables
from Schemas.imdb.schema import gen_job_light_imdb_schema
from Testing.BN_training import train_DMV, train_Census, train_imdb, train_imdb_one
from Testing.BN_testing import evaluate_cardinality_imdb_one, evaluate_cardinality_single_table, evaluate_cardinality_imdb

table_names = ['catalog_page']
model_path = "/home/ubuntu/yygs-projects/BayesCard/new_model"
learning_algo = "chow-liu"
if __name__ == '__main__':
    table_csv_path = "/home/ubuntu/yygs-projects/tpcds/data"
    schema = gen_job_light_imdb_schema(table_csv_path)
    for table in schema.tables:
        train_imdb_one(table, model_path, learning_algo, sample_size=table.table_size)