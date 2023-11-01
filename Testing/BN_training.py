import pandas as pd
import pickle
from DataPrepare.join_data_preparation import JoinDataPreparator
from Models.Bayescard_BN import Bayescard_BN, build_meta_info

def train_DMV(csv_path, model_path, algorithm, max_parents, sample_size):
    data = pd.read_csv(csv_path)
    new_cols = []
    #removing unuseful columns
    for col in data.columns:
        if col in ['VIN', 'Zip', 'City', 'Make', 'Unladen Weight', 'Maximum Gross Weight', 'Passengers',
                   'Reg Valid Date', 'Reg Expiration Date', 'Color']:
            data = data.drop(col, axis=1)
        else:
            new_cols.append(col.replace(" ", "_"))
    data.columns = new_cols
    BN = Bayescard_BN('dmv')
    BN.build_from_data(data, algorithm=algorithm, max_parents=max_parents, ignore_cols=['id'], sample_size=sample_size)
    model_path += f"/{algorithm}_{max_parents}.pkl"
    pickle.dump(BN, open(model_path, 'wb'), pickle.HIGHEST_PROTOCOL)
    print(f"model saved at {model_path}")
    return None

def train_Census(csv_path, model_path, algorithm, max_parents, sample_size):
    df = pd.read_csv(csv_path, header=0, sep=",")
    df = df.drop("caseid", axis=1)
    df = df.dropna(axis=0)
    BN = Bayescard_BN('Census')
    BN.build_from_data(df, algorithm=algorithm, max_parents=max_parents, ignore_cols=['id'], sample_size=sample_size)
    model_path += f"/{algorithm}_{max_parents}.pkl"
    pickle.dump(BN, open(model_path, 'wb'), pickle.HIGHEST_PROTOCOL)
    print(f"model saved at {model_path}")
    return None

def train_imdb_one(table, model_folder, algorithm, sample_size = 100000, max_parents = 1):
    csv_path = table.csv_file_location
    data = pd.read_csv(csv_path, sep="|", header=None, error_bad_lines=False)
    data = data.iloc[:, :-1]
    new_cols = []
    #removing unuseful columns
    data.columns = table.attributes
    for col in data.columns:
        if col in table.irrelevant_attributes:
            data = data.drop(col, axis=1)
        else:
            new_cols.append(col.replace(" ", "_"))
    data.columns = new_cols
    BN = Bayescard_BN('imdbOne')
    BN.build_from_data(data, algorithm=algorithm, max_parents=max_parents, ignore_cols=['id'], sample_size=sample_size)
    model_folder += f"/{table.table_name}.pkl"
    print(f"{model_folder}")
    pickle.dump(BN, open(model_folder, 'wb'), pickle.HIGHEST_PROTOCOL)
    print(f"model saved at {model_folder}")
    return None

def train_imdb(schema, hdf_path, model_folder, algorithm, max_parents, sample_size):
    meta_data_path = hdf_path + '/meta_data.pkl'
    prep = JoinDataPreparator(meta_data_path, schema, max_table_data=20000000)
    print(f"BN will be trained on the full outer join of following relations")
    for relationship_obj in schema.relationships:
        print(relationship_obj.identifier)

    for i, relationship_obj in enumerate(schema.relationships):
        print("training on relationship_obj.identifier")
        df_sample_size = 10000000
        relation = relationship_obj.identifier
        df, meta_types, null_values, full_join_est = prep.generate_n_samples(
            df_sample_size, relationship_list=[relation], post_sampling_factor=10)
        meta_info = build_meta_info(df.columns, null_values)
        bn = Bayescard_BN(relation, meta_info, full_join_est)
        model_path = model_folder + f"/{i}_{algorithm}_{max_parents}.pkl"
        bn.build_from_data(df, algorithm=algorithm, max_parents=max_parents, ignore_cols=['id'],
                           sample_size=sample_size)
        pickle.dump(bn, open(model_path, 'wb'), pickle.HIGHEST_PROTOCOL)
        print(f"model saved at {model_path}")
    return None

