import time

import prompt

from .constants import CONFIRM_ANSWER, TIME_PRECISION


def handle_db_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Некорректное значение: {e}. Попробуйте снова.")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

    return wrapper


def confirm_action(action_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            question = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            answer = prompt.string(question)

            if answer.strip().lower() != CONFIRM_ANSWER:
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()

        spent_time = end_time - start_time
        print(
            f"Функция {func.__name__} выполнилась за "
            f"{spent_time:.{TIME_PRECISION}f} секунд."
        )
        return result

    return wrapper


def create_cacher():
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]

        result = value_func()
        cache[key] = result
        return result

    return cache_result
