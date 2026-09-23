import prompt
import shlex

from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata

METADATA_FILE = "db_meta.json"


def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n") 


def run():
    print_help()
    while True:
        metadata = load_metadata(METADATA_FILE)

        user_input = prompt.string("Введите команду: ")

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Некорректное значение. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0]

        if command == "exit":
            break
        elif command == "help":
            print_help()
        elif command == "list_tables":
            list_tables(metadata)
        elif command == "drop_table":
            if len(args) != 2:
                print("Некорректное значение. Попробуйте снова.")
                continue

            table_name = args[1]

            metadata = drop_table(metadata, table_name)
            save_metadata(METADATA_FILE, metadata)
        elif command == "create_table":
            if len(args) < 3:
                print("Некорректное значение. Попробуйте снова.")
                continue

            table_name = args[1]
            columns = []

            for column in args[2:]:
                if ":" not in column:
                    print(
                        f"Некорректное значение: {column}. "
                        "Попробуйте снова."
                    )
                    break

                column_name, column_type = column.split(":", 1)

                if not column_name or not column_type:
                    print(
                        f"Некорректное значение: {column}. "
                        "Попробуйте снова."
                    )
                    break

                columns.append((column_name, column_type))
            else:
                metadata = create_table(
                    metadata,
                    table_name,
                    columns,
                )
                save_metadata(METADATA_FILE, metadata)
        else:
            print(
                f"Функции {command} нет. "
                "Попробуйте снова."
            )