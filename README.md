# Примитивная база данных

## Требования

- Python 3.12+
- Poetry 2.0+

## Установка

```bash
git clone https://github.com/YasherkaTOP/project2_plotnikov_daniil.git
cd project2_plotnikov_daniil
make install
```

Установка пакета в систему:

```bash
make build
make package-install
database
```

## Запуск

```bash
make project
```

## Управление таблицами

| Команда | Описание |
|---|---|
| `create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ...` | создать таблицу |
| `list_tables` | показать список всех таблиц |
| `drop_table <имя_таблицы>` | удалить таблицу (с подтверждением) |
| `help` | справочная информация |
| `exit` | выход из программы |

Поддерживаемые типы данных: `int`, `str`, `bool`.
Столбец `ID:int` добавляется в каждую таблицу автоматически.

## CRUD-операции

| Команда | Описание |
|---|---|
| `insert into <имя_таблицы> values (<значение1>, <значение2>, ...)` | создать запись |
| `select from <имя_таблицы>` | прочитать все записи |
| `select from <имя_таблицы> where <столбец> = <значение>` | прочитать записи по условию |
| `update <имя_таблицы> set <столбец> = <новое_значение> where <столбец> = <значение>` | обновить запись |
| `delete from <имя_таблицы> where <столбец> = <значение>` | удалить запись (с подтверждением) |
| `info <имя_таблицы>` | информация о таблице |

## Декораторы и кэширование

В модуле `decorators.py` находятся:

- `handle_db_errors` — перехватывает ошибки (`KeyError`, `ValueError`,
  `FileNotFoundError`) и выводит понятное сообщение, поэтому в функциях
  `core.py` нет повторяющихся блоков `try...except`;
- `confirm_action(action_name)` — спрашивает подтверждение `[y/n]` перед
  опасными операциями (`drop_table` и `delete`). Если ввести не `y`,
  операция отменяется;
- `log_time` — выводит время выполнения функций `select` и `insert`;
- `create_cacher()` — замыкание, которое кэширует результаты одинаковых
  запросов `select`. После изменения данных кэш сбрасывается.

## Структура проекта

```
project2_plotnikov_daniil/
├── src/
│   ├── __init__.py
│   └── primitive_db/
│       ├── __init__.py
│       ├── main.py
│       ├── engine.py
│       ├── core.py
│       ├── parser.py
│       ├── utils.py
│       ├── decorators.py
│       └── constants.py
├── Makefile
├── poetry.lock
├── pyproject.toml
├── README.md
└── .gitignore
```

## Проверка кода

```bash
make lint
```
