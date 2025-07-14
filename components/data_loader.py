import pandas as pd
import os

DATA_PATH = "data/models/"

def list_available_datasets(path=DATA_PATH):
    """Lista los nombres de los datasets disponibles sin la extensión .csv"""
    return [file.replace(".csv", "") for file in os.listdir(path) if file.endswith(".csv")]

def load_selected_datasets(selected_datasets, path=DATA_PATH):
    """Carga los datasets seleccionados y los devuelve en un diccionario de DataFrames."""
    datasets = {}
    for dataset in selected_datasets:
        file_path = os.path.join(path, f"{dataset}.csv")
        datasets[dataset] = pd.read_csv(file_path)
    return datasets


def select_columns(df, columns):
    "Select columns of the DataFrame"
    return df[columns]


def merge_datasets(datasets, selected_columns):
    """Merge all Dataframe models"""
    return pd.concat([select_columns(df, selected_columns) for df in datasets.values()])



