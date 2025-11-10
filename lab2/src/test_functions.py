"""
Тестовые функции для глобальной оптимизации.
Одномерные версии классических многомерных функций.
"""
import math
import numpy as np
from typing import Callable


def rastrigin_1d(x: float, A: float = 10.0, n: float = 2.0) -> float:
    """
    Одномерная функция Растригина.
    f(x) = A*n + x^2 - A*cos(2*pi*x)

    Имеет много локальных минимумов. Глобальный минимум в x=0, f(0)=0.

    :param x: аргумент
    :param A: параметр функции (по умолчанию 10)
    :param n: параметр функции (по умолчанию 2)
    :return: значение функции
    """
    return A * n + x**2 - A * math.cos(2 * math.pi * x)


def ackley_1d(x: float, a: float = 20.0, b: float = 0.2, c: float = 2.0 * math.pi) -> float:
    """
    Одномерная функция Экли.
    f(x) = -a*exp(-b*sqrt(x^2)) - exp(cos(c*x)) + a + e

    Имеет много локальных минимумов. Глобальный минимум в x=0, f(0)=0.

    :param x: аргумент
    :param a: параметр функции (по умолчанию 20)
    :param b: параметр функции (по умолчанию 0.2)
    :param c: параметр функции (по умолчанию 2*pi)
    :return: значение функции
    """
    term1 = -a * math.exp(-b * math.sqrt(x**2))
    term2 = -math.exp(math.cos(c * x))
    return term1 + term2 + a + math.e


def griewank_1d(x: float) -> float:
    """
    Одномерная функция Гриванка.
    f(x) = 1 + (x^2)/4000 - cos(x)

    :param x: аргумент
    :return: значение функции
    """
    return 1 + (x**2) / 4000 - math.cos(x)


def get_test_function(name: str) -> Callable[[float], float]:
    """
    Возвращает тестовую функцию по имени.

    :param name: имя функции ('rastrigin', 'ackley', 'griewank')
    :return: функция f(x)
    """
    functions = {
        'rastrigin': rastrigin_1d,
        'ackley': ackley_1d,
        'griewank': griewank_1d,
    }

    if name.lower() not in functions:
        raise ValueError(f"Неизвестная функция: {name}. Доступны: {list(functions.keys())}")

    return functions[name.lower()]


def get_function_string(name: str) -> str:
    """
    Возвращает строковое представление тестовой функции.

    :param name: имя функции
    :return: строка функции
    """
    strings = {
        'rastrigin': '10*2 + x^2 - 10*cos(2*pi*x)',
        'ackley': '-20*exp(-0.2*sqrt(x^2)) - exp(cos(2*pi*x)) + 20 + e',
        'griewank': '1 + x^2/4000 - cos(x)',
    }

    return strings.get(name.lower(), 'x^2')
