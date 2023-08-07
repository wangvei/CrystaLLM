import gzip
import pandas as pd
import numpy as np
from tqdm import tqdm
from lib import extract_data_formula, extract_space_group_symbol, extract_volume, extract_numeric_property, \
    get_unit_cell_volume
from sklearn.metrics import r2_score, mean_absolute_error
try:
    import cPickle as pickle
except ImportError:
    import pickle

import warnings
warnings.filterwarnings("ignore")


def get_metrics(df, col1, col2):
    df = df.dropna(subset=[col1, col2])
    r2 = r2_score(df[col1], df[col2])
    mae = mean_absolute_error(df[col1], df[col2])
    return r2, mae


def print_metrics(col1, col2, r2, mae):
    print(f"{col1} - {col2}: r2: {r2:.3f}, mae: {mae:.3f}")


if __name__ == '__main__':
    true_cifs_fname = "../out/orig_cifs_mp_2022_04_12+oqmd_v1_5+nomad_2023_04_30__comp-sg_augm.test.pkl.gz"
    # this should be a list of lists of k generation attempts, in the same order as the file above
    generated_cifs_fname = "../out/cif_model_32.evalcifs-sg.pkl.gz"
    gen_attempts = 3
    out_fname = "../out/cif_model_32.evalresults-sg.csv"

    with gzip.open(true_cifs_fname, "rb") as f:
        true_cifs = pickle.load(f)

    with gzip.open(generated_cifs_fname, "rb") as f:
        generated_cifs = pickle.load(f)

    results = {
        "formula": [],
        "sg": [],

        "true_vol": [],
        "true_a": [],
        "true_b": [],
        "true_c": [],
        "true_alpha": [],
        "true_beta": [],
        "true_gamma": [],
    }
    for k in range(gen_attempts):
        results[f"gen{k+1}_vol_generated"] = []
        results[f"gen{k+1}_vol_implied"] = []
        results[f"gen{k+1}_a"] = []
        results[f"gen{k+1}_b"] = []
        results[f"gen{k+1}_c"] = []
        results[f"gen{k+1}_alpha"] = []
        results[f"gen{k+1}_beta"] = []
        results[f"gen{k+1}_gamma"] = []

    for i, true_cif in tqdm(enumerate(true_cifs), total=len(true_cifs)):
        generated = generated_cifs[i]

        results["formula"].append(extract_data_formula(true_cif))
        results["sg"].append(extract_space_group_symbol(true_cif))

        results["true_vol"].append(extract_volume(true_cif))
        results["true_a"].append(extract_numeric_property(true_cif, "_cell_length_a"))
        results["true_b"].append(extract_numeric_property(true_cif, "_cell_length_b"))
        results["true_c"].append(extract_numeric_property(true_cif, "_cell_length_c"))
        results["true_alpha"].append(extract_numeric_property(true_cif, "_cell_angle_alpha"))
        results["true_beta"].append(extract_numeric_property(true_cif, "_cell_angle_beta"))
        results["true_gamma"].append(extract_numeric_property(true_cif, "_cell_angle_gamma"))

        for k in range(gen_attempts):
            if type(generated) == list:
                gen_cif = generated[k]
            else:
                # if generated is not a list, then `gen_attempts` should be 1, and `generated` is a CIF
                gen_cif = generated

            try:
                vol = extract_volume(gen_cif)
            except:
                vol = np.nan
            results[f"gen{k+1}_vol_generated"].append(vol)

            try:
                a = extract_numeric_property(gen_cif, "_cell_length_a")
            except:
                a = np.nan
            results[f"gen{k+1}_a"].append(a)

            try:
                b = extract_numeric_property(gen_cif, "_cell_length_b")
            except:
                b = np.nan
            results[f"gen{k+1}_b"].append(b)

            try:
                c = extract_numeric_property(gen_cif, "_cell_length_c")
            except:
                c = np.nan
            results[f"gen{k+1}_c"].append(c)

            try:
                alpha = extract_numeric_property(gen_cif, "_cell_angle_alpha")
            except:
                alpha = np.nan
            results[f"gen{k+1}_alpha"].append(alpha)

            try:
                beta = extract_numeric_property(gen_cif, "_cell_angle_beta")
            except:
                beta = np.nan
            results[f"gen{k+1}_beta"].append(beta)

            try:
                gamma = extract_numeric_property(gen_cif, "_cell_angle_gamma")
            except:
                gamma = np.nan
            results[f"gen{k+1}_gamma"].append(gamma)

            try:
                gen_vol_implied = get_unit_cell_volume(a, b, c, alpha, beta, gamma)
            except:
                gen_vol_implied = np.nan
            results[f"gen{k+1}_vol_implied"].append(gen_vol_implied)

    df = pd.DataFrame(results)
    df.to_csv(out_fname, index=False)

    for k in range(gen_attempts):
        col1, col2 = "true_vol", f"gen{k + 1}_vol_generated"
        r2, mae = get_metrics(df, col1, col2)
        print_metrics(col1, col2, r2, mae)

        col1, col2 = "true_a", f"gen{k+1}_a"
        r2, mae = get_metrics(df, col1, col2)
        print_metrics(col1, col2, r2, mae)

        col1, col2 = "true_b", f"gen{k + 1}_b"
        r2, mae = get_metrics(df, col1, col2)
        print_metrics(col1, col2, r2, mae)

        col1, col2 = "true_c", f"gen{k + 1}_c"
        r2, mae = get_metrics(df, col1, col2)
        print_metrics(col1, col2, r2, mae)

        col1, col2 = "true_alpha", f"gen{k + 1}_alpha"
        r2, mae = get_metrics(df, col1, col2)
        print_metrics(col1, col2, r2, mae)

        col1, col2 = "true_beta", f"gen{k + 1}_beta"
        r2, mae = get_metrics(df, col1, col2)
        print_metrics(col1, col2, r2, mae)

        col1, col2 = "true_gamma", f"gen{k + 1}_gamma"
        r2, mae = get_metrics(df, col1, col2)
        print_metrics(col1, col2, r2, mae)

        col1, col2 = f"gen{k + 1}_vol_implied", f"gen{k + 1}_vol_generated"
        r2, mae = get_metrics(df, col1, col2)
        print_metrics(col1, col2, r2, mae)

        print("- - - - -")
