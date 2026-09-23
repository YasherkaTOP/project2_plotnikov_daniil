from .constants import FALSE_VALUE, QUOTE, TRUE_VALUE


def split_outside_quotes(text, separator):
    parts = []
    current = ""
    in_quotes = False

    for char in text:
        if char == QUOTE:
            in_quotes = not in_quotes

        if char == separator and not in_quotes:
            parts.append(current)
            current = ""
        else:
            current += char

    parts.append(current)
    return parts


def parse_value(text):
    text = text.strip()

    if text == "":
        raise ValueError("пустое значение")

    if len(text) >= 2 and text[0] == QUOTE and text[-1] == QUOTE:
        return text[1:-1]

    if text.lower() == TRUE_VALUE:
        return True
    if text.lower() == FALSE_VALUE:
        return False

    try:
        return int(text)
    except ValueError:
        raise ValueError(text)


def parse_columns(column_args):
    columns = []

    for column in column_args:
        if ":" not in column:
            raise ValueError(column)

        column_name, column_type = column.split(":", 1)
        if column_name == "" or column_type == "":
            raise ValueError(column)

        columns.append((column_name, column_type))

    return columns


def parse_values(text):
    text = text.strip()

    if not text.startswith("(") or not text.endswith(")"):
        raise ValueError(text)

    inside = text[1:-1]
    if inside.strip() == "":
        return []

    values = []
    for part in split_outside_quotes(inside, ","):
        values.append(parse_value(part))

    return values


def parse_condition(text):
    equal_index = text.find("=")
    if equal_index == -1:
        raise ValueError(text.strip())

    column_name = text[:equal_index].strip()
    if column_name == "" or " " in column_name:
        raise ValueError(text.strip())

    value = parse_value(text[equal_index + 1:])
    return column_name, value


def parse_where(text):
    if text.strip() == "":
        raise ValueError("пустое условие where")

    column_name, value = parse_condition(text)
    return {column_name: value}


def parse_set(text):
    if text.strip() == "":
        raise ValueError("пустое условие set")

    set_clause = {}
    for part in split_outside_quotes(text, ","):
        column_name, value = parse_condition(part)
        set_clause[column_name] = value

    return set_clause


def parse_insert(user_input):
    parts = user_input.split(maxsplit=3)
    if len(parts) < 4 or parts[1] != "into":
        raise ValueError(user_input)

    table_name = parts[2]
    rest = parts[3].strip()
    if not rest.startswith("values"):
        raise ValueError(rest)

    values = parse_values(rest[len("values"):])
    return table_name, values


def parse_select(user_input):
    parts = user_input.split(maxsplit=3)
    if len(parts) < 3 or parts[1] != "from":
        raise ValueError(user_input)

    table_name = parts[2]
    if len(parts) == 3:
        return table_name, None

    rest = parts[3].strip()
    if not rest.startswith("where "):
        raise ValueError(rest)

    where_clause = parse_where(rest[len("where"):])
    return table_name, where_clause


def parse_update(user_input):
    parts = user_input.split(maxsplit=2)
    if len(parts) < 3:
        raise ValueError(user_input)

    table_name = parts[1]
    rest = parts[2].strip()
    if not rest.startswith("set "):
        raise ValueError(rest)

    rest = rest[len("set"):]
    where_index = rest.find(" where ")
    if where_index == -1:
        raise ValueError("не указано условие where")

    set_clause = parse_set(rest[:where_index])
    where_clause = parse_where(rest[where_index + len(" where "):])
    return table_name, set_clause, where_clause


def parse_delete(user_input):
    parts = user_input.split(maxsplit=3)
    if len(parts) < 4 or parts[1] != "from":
        raise ValueError(user_input)

    table_name = parts[2]
    rest = parts[3].strip()
    if not rest.startswith("where "):
        raise ValueError(rest)

    where_clause = parse_where(rest[len("where"):])
    return table_name, where_clause
