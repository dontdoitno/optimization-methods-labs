"""
Реализация метода Пиявского (Piyavskii-Shubert) для глобальной оптимизации
липшицевых функций.
"""
import time
from typing import List, Tuple, Callable
import numpy as np


class OptimizationResult:
    """Результат оптимизации."""

    def __init__(
        self,
        x_min: float,
        f_min: float,
        iterations: int,
        elapsed_time: float,
        broken_line_points: List[Tuple[float, float]],
        function_points: List[Tuple[float, float]],
    ):
        self.x_min = x_min
        self.f_min = f_min
        self.iterations = iterations
        self.elapsed_time = elapsed_time
        self.broken_line_points = broken_line_points  # точки ломаной линии
        self.function_points = function_points  # точки функции


def piyavskii_shubert(
    func: Callable[[float], float],
    a: float,
    b: float,
    L: float,
    eps: float,
    max_iterations: int = 10000
) -> OptimizationResult:
    """
    Метод Пиявского для поиска глобального минимума липшицевой функции.

    Алгоритм:
    1. Начинаем с двух точек: a и b
    2. На каждой итерации строим ломаную линию (нижнюю оценку функции)
    3. Находим точку минимума ломаной
    4. Вычисляем значение функции в этой точке
    5. Обновляем ломаную
    6. Повторяем до достижения точности

    :param func: функция для минимизации
    :param a: левый конец отрезка
    :param b: правый конец отрезка
    :param L: константа Липшица
    :param eps: требуемая точность
    :param max_iterations: максимальное число итераций
    :return: результат оптимизации
    """
    start_time = time.time()

    # Начальные точки
    points = [(a, func(a)), (b, func(b))]
    function_points = points.copy()

    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Сортируем точки по x
        points.sort(key=lambda p: p[0])

        # Находим точку минимума ломаной линии
        x_min, f_min_lower = find_broken_line_minimum(points, L)

        # Вычисляем значение функции в найденной точке
        f_min_actual = func(x_min)
        function_points.append((x_min, f_min_actual))

        # Добавляем новую точку
        points.append((x_min, f_min_actual))

        # Проверяем условие остановки
        # Останавливаемся, когда разница между нижней оценкой и фактическим значением
        # в точке минимума ломаной меньше eps
        if abs(f_min_actual - f_min_lower) < eps:
            break

    # Находим глобальный минимум среди всех вычисленных точек
    best_point = min(function_points, key=lambda p: p[1])
    x_min = best_point[0]
    f_min = best_point[1]

    elapsed_time = time.time() - start_time

    # Строим финальную ломаную линию для визуализации
    points.sort(key=lambda p: p[0])
    broken_line_points = build_broken_line(points, L, a, b)

    return OptimizationResult(
        x_min=x_min,
        f_min=f_min,
        iterations=iteration,
        elapsed_time=elapsed_time,
        broken_line_points=broken_line_points,
        function_points=sorted(function_points, key=lambda p: p[0]),
    )


def find_broken_line_minimum(points: List[Tuple[float, float]], L: float) -> Tuple[float, float]:
    """
    Находит точку минимума ломаной линии (нижней оценки функции).

    Ломаная линия строится как:
    phi(x) = max_i (f(x_i) - L * |x - x_i|)

    Минимум ломаной находится в точке пересечения двух "конусов".

    :param points: список точек (x, f(x))
    :param L: константа Липшица
    :return: (x_min, f_min) - точка и значение минимума ломаной
    """
    if len(points) < 2:
        return points[0]

    points = sorted(points, key=lambda p: p[0])
    min_x = points[0][0]
    min_f = float('inf')

    # Проверяем минимумы в точках пересечения конусов
    for i in range(len(points) - 1):
        x1, f1 = points[i]
        x2, f2 = points[i + 1]

        # Точка пересечения двух конусов
        # f1 - L*(x - x1) = f2 - L*(x2 - x)
        # Решаем: f1 - L*x + L*x1 = f2 - L*x2 + L*x
        # 2*L*x = f1 - f2 + L*(x1 + x2)
        # x = (f1 - f2 + L*(x1 + x2)) / (2*L)

        if abs(x2 - x1) > 1e-10:  # избегаем деления на ноль
            x_intersect = (f1 - f2 + L * (x1 + x2)) / (2 * L)

            # Проверяем, что точка пересечения между x1 и x2
            if x1 <= x_intersect <= x2:
                f_intersect = f1 - L * abs(x_intersect - x1)
                if f_intersect < min_f:
                    min_f = f_intersect
                    min_x = x_intersect

    # Также проверяем значения в самих точках
    for x, f in points:
        # Вычисляем значение ломаной в точке x
        broken_value = max(f_i - L * abs(x - x_i) for x_i, f_i in points)
        if broken_value < min_f:
            min_f = broken_value
            min_x = x

    return min_x, min_f


def build_broken_line(
    points: List[Tuple[float, float]],
    L: float,
    a: float,
    b: float,
    n_samples: int = 1000
) -> List[Tuple[float, float]]:
    """
    Строит ломаную линию (нижнюю оценку функции) для визуализации.

    :param points: список точек (x, f(x))
    :param L: константа Липшица
    :param a: левый конец отрезка
    :param b: правый конец отрезка
    :param n_samples: количество точек для построения
    :return: список точек ломаной линии
    """
    x_samples = np.linspace(a, b, n_samples)
    broken_line = []

    for x in x_samples:
        # Ломаная линия: максимум по всем конусам
        value = max(f - L * abs(x - x_i) for x_i, f in points)
        broken_line.append((x, value))

    return broken_line
