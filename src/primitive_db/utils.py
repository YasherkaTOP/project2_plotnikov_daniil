import json
import os

from .constants import DATA_DIR, DATA_FILE_EXTENSION


def load_metadata(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_table_path(table_name):
    return os.path.join(DATA_DIR, table_name + DATA_FILE_EXTENSION)


def load_table_data(table_name):
    try:
        with open(get_table_path(table_name), "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    with open(get_table_path(table_name), "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def delete_table_data(table_name):
    table_path = get_table_path(table_name)
    if os.path.exists(table_path):
        os.remove(table_path)
