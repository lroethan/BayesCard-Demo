import pandas as pd
from Schemas.graph_representation import SchemaGraph, Table

def gen_job_light_imdb_schema(csv_path):
    """
    Just like the full IMDB schema but without tables that are not used in the job-light benchmark.
    """

    schema = SchemaGraph()

    # tables

    # title
    schema.add_table(Table('title', attributes=['id', 'title', 'imdb_index', 'kind_id', 'production_year', 'imdb_id',
                                                'phonetic_code', 'episode_of_id', 'season_nr', 'episode_nr',
                                                'series_years', 'md5sum'],
                           irrelevant_attributes=['episode_of_id', 'title', 'imdb_index', 'phonetic_code', 'season_nr',
                                                  'imdb_id', 'episode_nr', 'series_years', 'md5sum'],
                           no_compression=['kind_id'],
                           csv_file_location=csv_path.format('title'),
                           table_size=3486660))
    return schema

def count_rows_with_condition(csv_file):
    # 读取CSV文件
    schema = gen_job_light_imdb_schema(csv_file)
    df = pd.read_csv(csv_file, header=None, error_bad_lines=False)
    df.columns = schema.tables[0].attributes
    # 设置条件
    condition = (df['production_year'] == 2011) & (df['kind_id'] == 7)

    # 使用条件筛选数据
    filtered_df = df[condition]

    # 计算满足条件的行数
    row_count = len(filtered_df)

    return row_count

dataset = "/home/ubuntu/yygs-projects/BayesCard/dataset/"
table_name = "title"
table_num = count_rows_with_condition(dataset + table_name + ".csv")
print(table_num)