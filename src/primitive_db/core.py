ALLOWED_TYPES = {"int", "str", "bool"}


def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    for _, column_type in columns:
        if column_type not in ALLOWED_TYPES:
            print(f"Некорректное значение: {column_type}. Попробуйте снова.")
            return metadata

    table_columns = [("ID", "int"), *columns]

    metadata[table_name] = {
        "columns": dict(table_columns)
    }

    columns_text = ", ".join(
        f"{column_name}:{column_type}"
        for column_name, column_type in table_columns
    )

    print(
        f'Таблица "{table_name}" успешно создана '
        f"со столбцами: {columns_text}"
    )

    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]

    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata


def list_tables(metadata):
    for table_name in metadata:
        print(f"- {table_name}")