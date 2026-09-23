from .constants import FIRST_ID, ID_COLUMN, ID_TYPE, VALID_TYPES
from .decorators import confirm_action, handle_db_errors, log_time
from .utils import load_table_data


def check_table_exists(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    return True


def get_columns_text(columns):
    parts = []
    for column_name, column_type in columns.items():
        parts.append(f"{column_name}:{column_type}")
    return ", ".join(parts)


def check_value_type(column_type, value):
    if column_type == "int":
        return type(value) is int
    if column_type == "str":
        return type(value) is str
    if column_type == "bool":
        return type(value) is bool
    return False


@handle_db_errors
def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None

    table_columns = {ID_COLUMN: ID_TYPE}

    for column_name, column_type in columns:
        if column_type not in VALID_TYPES:
            raise ValueError(column_type)

        if column_name == ID_COLUMN:
            if column_type != ID_TYPE:
                raise ValueError(f"{column_name}:{column_type}")
            continue

        table_columns[column_name] = column_type

    metadata[table_name] = {"columns": table_columns}

    columns_text = get_columns_text(table_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_text}')
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    for table_name in metadata:
        print(f"- {table_name}")


@handle_db_errors
def validate_clause(metadata, table_name, clause):
    columns = metadata[table_name]["columns"]

    for column_name, value in clause.items():
        if column_name not in columns:
            raise KeyError(column_name)
        if not check_value_type(columns[column_name], value):
            raise ValueError(value)

    return True


def record_matches(record, where_clause):
    if where_clause is None:
        return True

    for column_name, value in where_clause.items():
        if record.get(column_name) != value:
            return False
    return True


def find_records(table_data, where_clause):
    found = []
    for record in table_data:
        if record_matches(record, where_clause):
            found.append(record)
    return found


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    if not check_table_exists(metadata, table_name):
        return None

    columns = metadata[table_name]["columns"]

    # ID генерируется сам, поэтому его в списке столбцов пропускаем
    column_names = []
    for column_name in columns:
        if column_name != ID_COLUMN:
            column_names.append(column_name)

    if len(values) != len(column_names):
        raise ValueError(
            f"нужно {len(column_names)} значений, а передано {len(values)}"
        )

    for i in range(len(column_names)):
        column_type = columns[column_names[i]]
        if not check_value_type(column_type, values[i]):
            raise ValueError(values[i])

    table_data = load_table_data(table_name)

    new_id = FIRST_ID
    for record in table_data:
        if record[ID_COLUMN] >= new_id:
            new_id = record[ID_COLUMN] + 1

    new_record = {ID_COLUMN: new_id}
    for i in range(len(column_names)):
        new_record[column_names[i]] = values[i]

    table_data.append(new_record)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    return find_records(table_data, where_clause)


@handle_db_errors
def update(table_data, set_clause, where_clause):
    for record in table_data:
        if record_matches(record, where_clause):
            for column_name, value in set_clause.items():
                record[column_name] = value
    return table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    new_data = []
    for record in table_data:
        if not record_matches(record, where_clause):
            new_data.append(record)
    return new_data


def table_info(metadata, table_name, table_data):
    columns_text = get_columns_text(metadata[table_name]["columns"])
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns_text}")
    print(f"Количество записей: {len(table_data)}")
