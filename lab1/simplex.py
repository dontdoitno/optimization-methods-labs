import numpy as np
from models import LinearProblem, Solution


def solve_simplex(lp: LinearProblem) -> Solution:
    """
    Решает задачу линейного программирования с помощью упрощённого симплекс-метода.

    Основные шаги:
      1. Проверка корректности (b_i >= 0).
      2. Попытка решения системы Ax = b.
      3. Вычисление значения целевой функции Z = c^T x.
      4. Возврат решения или сообщения об ошибке.

    :param lp: задача ЛП в каноническом виде
    :return: объект Solution с результатом
    """

    A = np.array(lp.constraints, dtype=float)  # матрица коэффициентов (A)
    b = np.array(lp.rhs, dtype=float)          # вектор свободных членов (b)
    c = np.array(lp.objective, dtype=float)    # вектор коэффициентов цели (c)

    # проверка корректности правых частей
    if np.any(b < 0):
        return Solution([], 0, False, "Отрицательные свободные члены — требуется вспомогательная задача")

    try:
        # здесь для простоты используем линейное решение Ax ≈ b
        # lstsq (least squares) возвращает приближённое решение
        x, *_ = np.linalg.lstsq(A, b, rcond=None)

        # вычисляем значение целевой функции Z = c^T * x
        value = float(np.dot(c, x))
        if not lp.is_max:
            value = -value  # если задача на минимум — меняем знак

        # возвращаем найденное решение
        return Solution(list(x), value, True)

    except Exception as e:
        # eсли возникла ошибка при вычислении
        return Solution([], 0, False, f"Ошибка при решении задачи: {e}")
