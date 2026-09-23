import shlex

import prompt
from prettytable import PrettyTable

from .constants import ID_COLUMN, META_FILE, PROMPT_TEXT
from .core import (
    check_table_exists,
    create_table,
    delete,
    drop_table,
    find_records,
    insert,
    list_tables,
    select,
    table_info,
    update,
    validate_clause,
)
from .decorators import create_cacher, handle_db_errors
from .parser import (
    parse_columns,
    parse_delete,
    parse_insert,
    parse_select,
    parse_update,
)
from .utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    print("\n***База данных***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. "
        "- создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_records(column_names, records):
    table = PrettyTable()
    table.field_names = column_names

    for record in records:
        row = []
        for column_name in column_names:
            row.append(record.get(column_name))
        table.add_row(row)

    print(table)


@handle_db_errors
def run_create_table(metadata, args):
    if len(args) < 3:
        raise ValueError(" ".join(args))

    table_name = args[1]
    columns = parse_columns(args[2:])

    new_metadata = create_table(metadata, table_name, columns)
    if new_metadata is not None:
        save_metadata(META_FILE, new_metadata)


@handle_db_errors
def run_drop_table(metadata, args):
    if len(args) != 2:
        raise ValueError(" ".join(args))

    table_name = args[1]
    if not check_table_exists(metadata, table_name):
        return False

    new_metadata = drop_table(metadata, table_name)
    if new_metadata is None:
        return False

    save_metadata(META_FILE, new_metadata)
    delete_table_data(table_name)
    return True


@handle_db_errors
def run_insert(metadata, user_input):
    table_name, values = parse_insert(user_input)
    if not check_table_exists(metadata, table_name):
        return False

    table_data = insert(metadata, table_name, values)
    if table_data is None:
        return False

    save_table_data(table_name, table_data)
    return True


@handle_db_errors
def run_select(metadata, user_input, cache_result):
    table_name, where_clause = parse_select(user_input)

    if not check_table_exists(metadata, table_name):
        return
    if where_clause is not None:
        if not validate_clause(metadata, table_name, where_clause):
            return

    def get_records():
        table_data = load_table_data(table_name)
        return select(table_data, where_clause)

    cache_key = f"{table_name}:{where_clause}"
    records = cache_result(cache_key, get_records)
    if records is None:
        return

    column_names = list(metadata[table_name]["columns"].keys())
    print_records(column_names, records)


@handle_db_errors
def run_update(metadata, user_input):
    table_name, set_clause, where_clause = parse_update(user_input)

    if not check_table_exists(metadata, table_name):
        return False
    if not validate_clause(metadata, table_name, set_clause):
        return False
    if not validate_clause(metadata, table_name, where_clause):
        return False

    table_data = load_table_data(table_name)
    found = find_records(table_data, where_clause)
    if len(found) == 0:
        print("Записи, подходящие под условие, не найдены.")
        return False

    table_data = update(table_data, set_clause, where_clause)
    if table_data is None:
        return False

    save_table_data(table_name, table_data)
    for record in found:
        print(
            f"Запись с ID={record[ID_COLUMN]} в таблице "
            f'"{table_name}" успешно обновлена.'
        )
    return True


@handle_db_errors
def run_delete(metadata, user_input):
    table_name, where_clause = parse_delete(user_input)

    if not check_table_exists(metadata, table_name):
        return False
    if not validate_clause(metadata, table_name, where_clause):
        return False

    table_data = load_table_data(table_name)
    found = find_records(table_data, where_clause)
    if len(found) == 0:
        print("Записи, подходящие под условие, не найдены.")
        return False

    table_data = delete(table_data, where_clause)
    if table_data is None:
        return False

    save_table_data(table_name, table_data)
    for record in found:
        print(
            f"Запись с ID={record[ID_COLUMN]} успешно удалена "
            f'из таблицы "{table_name}".'
        )
    return True


@handle_db_errors
def run_info(metadata, args):
    if len(args) != 2:
        raise ValueError(" ".join(args))

    table_name = args[1]
    if not check_table_exists(metadata, table_name):
        return

    table_data = load_table_data(table_name)
    table_info(metadata, table_name, table_data)


def run():
    print_help()
    cache_result = create_cacher()

    while True:
        metadata = load_metadata(META_FILE)

        try:
            user_input = prompt.string(PROMPT_TEXT)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        if len(args) == 0:
            continue

        command = args[0]
        data_changed = False

        if command == "exit":
            break
        elif command == "help":
            print_help()
        elif command == "list_tables":
            list_tables(metadata)
        elif command == "create_table":
            run_create_table(metadata, args)
        elif command == "drop_table":
            data_changed = run_drop_table(metadata, args)
        elif command == "insert":
            data_changed = run_insert(metadata, user_input)
        elif command == "select":
            run_select(metadata, user_input, cache_result)
        elif command == "update":
            data_changed = run_update(metadata, user_input)
        elif command == "delete":
            data_changed = run_delete(metadata, user_input)
        elif command == "info":
            run_info(metadata, args)
        else:
            print(f"Функции {command} нет. Попробуйте снова.")

        if data_changed:
            cache_result = create_cacher()
