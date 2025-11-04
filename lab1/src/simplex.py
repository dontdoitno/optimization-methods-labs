import numpy as np
from src.models import LinearProblem, Solution

def solve_simplex(lp: LinearProblem):
    # Симплекс-метод только для задач максимизации в каноническом виде!

    # Приводим данные к numpy-массивам
    A = np.array(lp.constraints, dtype=float)
    b = np.array(lp.rhs, dtype=float)
    c = np.array(lp.objective, dtype=float)

    m, n = A.shape

    # Добавим slack-переменные для неравенств "<="
    # (может потребоваться доработка с учетом "=", ">=")
    basis = []
    for i, sign in enumerate(lp.signs):
        if sign == "<=":
            new_col = np.zeros((m, 1))
            new_col[i, 0] = 1
            A = np.hstack((A, new_col))
            c = np.hstack((c, [0]))
            basis.append(n)
            n += 1
        elif sign == "=":
            basis.append(None)  # изначально не базисная переменная
        elif sign == ">=":
            new_col = np.zeros((m, 1))
            new_col[i, 0] = -1
            A = np.hstack((A, new_col))
            c = np.hstack((c, [0]))
            basis.append(n)
            n += 1

    # Подготовка симплекс-таблицы
    num_vars = len(lp.objective)
    tableau = np.zeros((m + 1, n + 1))
    tableau[:m, :n] = A
    tableau[:m, -1] = b
    tableau[-1, :n] = -c if lp.is_max else c

    # Симплекс-итерации
    while True:
        # Поиск ведущего столбца (самый отрицательный коэффициент в строке цели)
        obj_row = tableau[-1, :-1]
        if np.all(obj_row >= -1e-9):  # почти все >=0; финальный ответ
            break
        pivot_col = np.argmin(obj_row)

        # Проверка неограниченности
        if np.all(tableau[:m, pivot_col] <= 1e-9):
            return Solution([], float('inf'), False, "Функция не ограничена сверху")

        # Поиск ведущей строки (правило минимального отношения)
        ratios = []
        for i in range(m):
            if tableau[i, pivot_col] > 1e-9:
                ratios.append(tableau[i, -1] / tableau[i, pivot_col])
            else:
                ratios.append(np.inf)
        pivot_row = np.argmin(ratios)

        # Делим ведущую строку на ведущий элемент
        tableau[pivot_row, :] /= tableau[pivot_row, pivot_col]

        # Нулевые все остальные элементы в столбце
        for i in range(m+1):
            if i != pivot_row:
                tableau[i, :] -= tableau[i, pivot_col] * tableau[pivot_row, :]

        # Обновление базиса
        if len(basis) > pivot_row:
            basis[pivot_row] = pivot_col
        else:
            basis.append(pivot_col)

    # Извлечение решения
    x = np.zeros(n)
    for i in range(m):
        if basis[i] is not None and basis[i] < n:
            x[basis[i]] = tableau[i, -1]
    val = tableau[-1, -1]
    # Оставь только исходные переменные
    x = x[:num_vars]

    return Solution(list(x), val if lp.is_max else -val, True, "Симплекс: решение найдено")
