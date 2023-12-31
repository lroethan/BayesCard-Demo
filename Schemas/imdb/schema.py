from Schemas.graph_representation import SchemaGraph, Table


def gen_job_light_imdb_schema(csv_path):
    """
    Just like the full IMDB schema but without tables that are not used in the job-light benchmark.
    """

    schema = SchemaGraph()

    schema.add_table(Table('catalog_page', attributes=['cp_catalog_page_sk', 'cp_catalog_page_id', 'cp_start_date_sk', 'cp_end_date_sk', 'cp_department', 'cp_catalog_number',
                                                'cp_catalog_page_number', 'cp_description', 'cp_type'],
                           irrelevant_attributes=['cp_catalog_page_sk', 'cp_catalog_page_id', 'cp_description'],
                           csv_file_location='/home/ubuntu/yygs-projects/tpcds/data/catalog_page.csv',
                           table_size=12000))

    schema.add_table(Table('date_dim', attributes=["d_date_sk", "d_date_id", "d_date", "d_month_seq", "d_week_seq", "d_quarter_seq", "d_year", "d_dow", "d_moy", "d_dom", "d_qoy", "d_fy_year", "d_fy_quarter_seq", "d_fy_week_seq", "d_day_name", "d_quarter_name", "d_holiday", "d_weekend", "d_following_holiday", "d_first_dom", "d_last_dom", "d_same_day_ly", "d_same_day_lq", "d_current_day", "d_current_week", "d_current_month", "d_current_quarter", "d_current_year"],
                           irrelevant_attributes=['d_date_sk', 'd_date_id', 'd_date', 'd_dom'],
                           csv_file_location='/home/ubuntu/yygs-projects/tpcds/data/date_dim.csv',
                           table_size=12000))

    schema.add_table(Table('item', attributes=["i_item_sk", "i_item_id", "i_rec_start_date", "i_rec_end_date",
                                               "i_item_desc", "i_current_price", "i_wholesale_cost", "i_brand_id",
                                               "i_brand", "i_class_id", "i_class", "i_category_id",
                                               "i_category", "i_manufact_id", "i_manufact", "i_size",
                                               "i_formulation", "i_color", "i_units", "i_container",
                                               "i_manager_id", "i_product_name"],

                           irrelevant_attributes=['i_item_sk', 'i_item_id', 'i_item_desc', 'i_brand', 'i_manufact', 'i_formulation', 'i_product_name'],
                           csv_file_location='/home/ubuntu/yygs-projects/tpcds/data/item.csv',
                           table_size=12000))
    
    # tables

    # title
    # schema.add_table(Table('title', attributes=['id', 'title', 'imdb_index', 'kind_id', 'production_year', 'imdb_id',
    #                                             'phonetic_code', 'episode_of_id', 'season_nr', 'episode_nr',
    #                                             'series_years', 'md5sum'],
    #                        irrelevant_attributes=['episode_of_id', 'title', 'imdb_index', 'phonetic_code', 'season_nr',
    #                                               'imdb_id', 'episode_nr', 'series_years', 'md5sum'],
    #                        no_compression=['kind_id'],
    #                        csv_file_location=csv_path.format('title'),
    #                        table_size=3486660))

    # # movie_info_idx
    # schema.add_table(Table('movie_info_idx', attributes=['id', 'movie_id', 'info_type_id', 'info', 'note'],
    #                        csv_file_location=csv_path.format('movie_info_idx'),
    #                        irrelevant_attributes=['info', 'note'],
    #                        no_compression=['info_type_id'],
    #                        table_size=3147110))

    # # movie_info
    # schema.add_table(Table('movie_info', attributes=['id', 'movie_id', 'info_type_id', 'info', 'note'],
    #                        csv_file_location=csv_path.format('movie_info'),
    #                        irrelevant_attributes=['info', 'note'],
    #                        no_compression=['info_type_id'],
    #                        table_size=24988000))

    # # cast_info
    # schema.add_table(Table('cast_info', attributes=['id', 'person_id', 'movie_id', 'person_role_id', 'note', 'nr_order',
    #                                                 'role_id'],
    #                        csv_file_location=csv_path.format('cast_info'),
    #                        irrelevant_attributes=['nr_order', 'note', 'person_id', 'person_role_id'],
    #                        no_compression=['role_id'],
    #                        table_size=63475800))

    # # movie_keyword
    # schema.add_table(Table('movie_keyword', attributes=['id', 'movie_id', 'keyword_id'],
    #                        csv_file_location=csv_path.format('movie_keyword'),
    #                        no_compression=['keyword_id'],
    #                        table_size=7522600))

    # movie_companies
    # schema.add_table(Table('movie_companies', attributes=['id', 'movie_id', 'company_id', 'company_type_id', 'note'],
    #                        csv_file_location=csv_path.format('movie_companies'),
    #                        irrelevant_attributes=['note'],
    #                        no_compression=['company_id', 'company_type_id'],
    #                        table_size=4958300))


    # relationships
    # schema.add_relationship('movie_info_idx', 'movie_id', 'title', 'id')
    # schema.add_relationship('movie_info', 'movie_id', 'title', 'id')
    # schema.add_relationship('cast_info', 'movie_id', 'title', 'id')
    # schema.add_relationship('movie_keyword', 'movie_id', 'title', 'id')
    # schema.add_relationship('movie_companies', 'movie_id', 'title', 'id')

    return schema


def gen_imdb_schema(csv_path):
    """
    Specifies full imdb schema. Also tables not in the job-light benchmark.
    """
    schema = SchemaGraph()

    # tables

    # title
    schema.add_table(Table('title', attributes=['id', 'title', 'imdb_index', 'kind_id', 'production_year', 'imdb_id',
                                                'phonetic_code', 'episode_of_id', 'season_nr', 'episode_nr',
                                                'series_years', 'md5sum'],
                           irrelevant_attributes=['episode_of_id'],
                           csv_file_location=csv_path.format('title'),
                           table_size=3486660))

    # movie_info_idx
    schema.add_table(Table('movie_info_idx', attributes=['id', 'movie_id', 'info_type_id', 'info', 'note'],
                           csv_file_location=csv_path.format('movie_info_idx'),
                           table_size=3147110))

    # movie_info
    schema.add_table(Table('movie_info', attributes=['id', 'movie_id', 'info_type_id', 'info', 'note'],
                           csv_file_location=csv_path.format('movie_info'),
                           table_size=24988000))

    # info_type
    schema.add_table(Table('info_type', attributes=['id', 'info'],
                           csv_file_location=csv_path.format('info_type'),
                           table_size=113))

    # cast_info
    schema.add_table(Table('cast_info', attributes=['id', 'person_id', 'movie_id', 'person_role_id', 'note', 'nr_order',
                                                    'role_id'],
                           csv_file_location=csv_path.format('cast_info'),
                           table_size=63475800))

    # char_name
    schema.add_table(Table('char_name', attributes=['id', 'name', 'imdb_index', 'imdb_id', 'name_pcode_nf',
                                                    'surname_pcode', 'md5sum'],
                           csv_file_location=csv_path.format('char_name'),
                           table_size=4314870))

    # role_type
    schema.add_table(Table('role_type', attributes=['id', 'role'],
                           csv_file_location=csv_path.format('role_type'),
                           table_size=0))

    # complete_cast
    schema.add_table(Table('complete_cast', attributes=['id', 'movie_id', 'subject_id', 'status_id'],
                           csv_file_location=csv_path.format('complete_cast'),
                           table_size=135086))

    # comp_cast_type
    schema.add_table(Table('comp_cast_type', attributes=['id', 'kind'],
                           csv_file_location=csv_path.format('comp_cast_type'),
                           table_size=0))

    # name
    schema.add_table(Table('name', attributes=['id', 'name', 'imdb_index', 'imdb_id', 'gender', 'name_pcode_cf',
                                               'name_pcode_nf', 'surname_pcode', 'md5sum'],
                           csv_file_location=csv_path.format('name'),
                           table_size=6379740))

    # aka_name
    schema.add_table(Table('aka_name', attributes=['id', 'person_id', 'name', 'imdb_index', 'name_pcode_cf',
                                                   'name_pcode_nf', 'surname_pcode', 'md5sum'],
                           csv_file_location=csv_path.format('aka_name'),
                           table_size=1312270))

    # movie_link, is empty
    # schema.add_table(Table('movie_link', attributes=['id', 'movie_id', 'linked_movie_id', 'link_type_id'],
    #                        csv_file_location=csv_path.format('movie_link')))

    # link_type, no relationships
    # schema.add_table(Table('link_type', attributes=['id', 'link'],
    #                        csv_file_location=csv_path.format('link_type')))

    # movie_keyword
    schema.add_table(Table('movie_keyword', attributes=['id', 'movie_id', 'keyword_id'],
                           csv_file_location=csv_path.format('movie_keyword'),
                           table_size=7522600))

    # keyword
    schema.add_table(Table('keyword', attributes=['id', 'keyword', 'phonetic_code'],
                           csv_file_location=csv_path.format('keyword'),
                           table_size=236627))

    # person_info
    schema.add_table(Table('person_info', attributes=['id', 'person_id', 'info_type_id', 'info', 'note'],
                           csv_file_location=csv_path.format('person_info'),
                           table_size=4130210))

    # movie_companies
    schema.add_table(Table('movie_companies', attributes=['id', 'movie_id', 'company_id', 'company_type_id', 'note'],
                           csv_file_location=csv_path.format('movie_companies'),
                           table_size=4958300))

    # company_name
    schema.add_table(Table('company_name', attributes=['id', 'name', 'country_code', 'imdb_id', 'name_pcode_nf',
                                                       'name_pcode_sf', 'md5sum'],
                           csv_file_location=csv_path.format('company_name'),
                           table_size=362131))

    # company_type
    schema.add_table(Table('company_type', attributes=['id', 'kind'],
                           csv_file_location=csv_path.format('company_type'),
                           table_size=0))

    # aka_title
    schema.add_table(Table('aka_title', attributes=['id', 'movie_id', 'title', 'imdb_index', 'kind_id',
                                                    'production_year', 'phonetic_code', 'episode_of_id', 'season_nr',
                                                    'episode_nr', 'note', 'md5sum'],
                           irrelevant_attributes=['episode_of_id'],
                           csv_file_location=csv_path.format('aka_title'),
                           table_size=528268))

    # kind_type
    schema.add_table(Table('kind_type', attributes=['id', 'kind'],
                           csv_file_location=csv_path.format('kind_type'),
                           table_size=0))

    # relationships

    # title
    # omit self-join for now
    # schema.add_relationship('title', 'episode_of_id', 'title', 'id')
    schema.add_relationship('title', 'kind_id', 'kind_type', 'id')

    # movie_info_idx
    schema.add_relationship('movie_info_idx', 'info_type_id', 'info_type', 'id')
    schema.add_relationship('movie_info_idx', 'movie_id', 'title', 'id')

    # movie_info
    schema.add_relationship('movie_info', 'info_type_id', 'info_type', 'id')
    schema.add_relationship('movie_info', 'movie_id', 'title', 'id')

    # info_type, no relationships

    # cast_info
    schema.add_relationship('cast_info', 'movie_id', 'title', 'id')
    schema.add_relationship('cast_info', 'person_id', 'name', 'id')
    schema.add_relationship('cast_info', 'person_role_id', 'char_name', 'id')
    schema.add_relationship('cast_info', 'role_id', 'role_type', 'id')

    # char_name, no relationships

    # role_type, no relationships

    # complete_cast
    schema.add_relationship('complete_cast', 'movie_id', 'title', 'id')
    schema.add_relationship('complete_cast', 'status_id', 'comp_cast_type', 'id')
    schema.add_relationship('complete_cast', 'subject_id', 'comp_cast_type', 'id')

    # comp_cast_type, no relationships

    # name, no relationships

    # aka_name
    schema.add_relationship('aka_name', 'person_id', 'name', 'id')

    # movie_link, is empty
    # schema.add_relationship('movie_link', 'link_type_id', 'link_type', 'id')
    # schema.add_relationship('movie_link', 'linked_movie_id', 'title', 'id')
    # schema.add_relationship('movie_link', 'movie_id', 'title', 'id')

    # link_type, no relationships

    # movie_keyword
    schema.add_relationship('movie_keyword', 'keyword_id', 'keyword', 'id')
    schema.add_relationship('movie_keyword', 'movie_id', 'title', 'id')

    # keyword, no relationships

    # person_info
    schema.add_relationship('person_info', 'info_type_id', 'info_type', 'id')
    schema.add_relationship('person_info', 'person_id', 'name', 'id')

    # movie_companies
    schema.add_relationship('movie_companies', 'company_id', 'company_name', 'id')
    schema.add_relationship('movie_companies', 'company_type_id', 'company_type', 'id')
    schema.add_relationship('movie_companies', 'movie_id', 'title', 'id')

    # company_name, no relationships

    # company_type, no relationships

    # aka_title
    schema.add_relationship('aka_title', 'movie_id', 'title', 'id')
    schema.add_relationship('aka_title', 'kind_id', 'kind_type', 'id')

    # kind_type, no relationships

    return schema
