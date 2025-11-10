"""
Парсер и вычислитель функций из строкового представления.
Поддерживает основные математические функции и операции.
"""
import math
import numpy as np
from typing import Callable


def safe_eval(expr: str, x: float) -> float:
    """
    Безопасное вычисление выражения с переменной x.

    :param expr: строка с выражением (например, "x + sin(3.14159*x)")
    :param x: значение переменной
    :return: значение функции в точке x
    """
    # Создаём безопасное пространство имён для eval
    safe_dict = {
        'x': x,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'exp': math.exp,
        'log': math.log,
        'log10': math.log10,
        'sqrt': math.sqrt,
        'abs': abs,
        'fabs': math.fabs,
        'pi': math.pi,
        'e': math.e,
        'pow': pow,
        '__builtins__': {},
    }

    try:
        return float(eval(expr, safe_dict))
    except Exception as e:
        raise ValueError(f"Ошибка при вычислении выражения '{expr}' в точке x={x}: {e}")


def parse_function(func_str: str) -> Callable[[float], float]:
    """
    Парсит строку функции и возвращает callable объект.

    :param func_str: строка функции (например, "x + sin(3.14159*x)" или "f(x) = x^2")
    :return: функция f(x)
    """
    # Убираем "f(x) = " если есть
    func_str = func_str.strip()
    if '=' in func_str:
        func_str = func_str.split('=')[-1].strip()

    # Заменяем ^ на ** для возведения в степень
    func_str = func_str.replace('^', '**')

    # Создаём функцию
    def f(x: float) -> float:
        return safe_eval(func_str, x)

    return f


def estimate_lipschitz_constant(func: Callable[[float], float], a: float, b: float, n_samples: int = 1000) -> float:
    """
    Оценивает константу Липшица функции на отрезке [a, b].

    :param func: функция для оценки
    :param a: левый конец отрезка
    :param b: правый конец отрезка
    :param n_samples: количество точек для оценки
    :return: оценка константы Липшица
    """
    x_samples = np.linspace(a, b, n_samples)
    f_samples = np.array([func(x) for x in x_samples])

    # Оцениваем производную через конечные разности
    dx = (b - a) / (n_samples - 1)
    df = np.diff(f_samples)
    derivatives = np.abs(df / dx)

    # Константа Липшица - максимум модуля производной
    L = np.max(derivatives) if len(derivatives) > 0 else 1.0

    # Добавляем небольшой запас для надёжности
    return L * 1.1 if L > 0 else 1.0
