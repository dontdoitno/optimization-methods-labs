from models import LinearProblem


def build_auxiliary(lp: LinearProblem) -> LinearProblem:
    """
    Формирует вспомогательную задачу.

    Алгоритм:
      1. Если правая часть (r_i) отрицательная — умножаем строку на -1.
      2. Добавляем искусственную переменную a_i для каждого ограничения.
      3. Формируем новую целевую функцию:
         → минимизировать сумму всех искусственных переменных.

    :param lp: задача в каноническом виде
    :return: вспомогательная задача для первого этапа симплекс-метода
    """

    # копируем данные, чтобы не менять исходный объект
    constraints = [row[:] for row in lp.constraints]
    rhs = lp.rhs[:]
    var_names = lp.var_names[:]

    artificial_vars = []  # искусственные переменные

    # идём по всем ограничениям
    for i, r in enumerate(rhs):
        if r < 0:
            # если правая часть отрицательная, то умножаем всю строку на -1
            constraints[i] = [-x for x in constraints[i]]
            rhs[i] = -r

        # создаём столбец для искуственной переменной a_i
        artificial_col = [0] * len(rhs)
        artificial_col[i] = 1  # единица только в одной строке

        # добавляем столбец искусственной переменной к матрице ограничений
        for j, row in enumerate(constraints):
            row.extend([artificial_col[j]])

        artificial_vars.append(f'a{i + 1}')

    # формируем целевую функцию для вспомогательной задачи
    objective = [0] * len(constraints[0])
    for i in range(len(artificial_vars)):
        objective[-(i + 1)] = 1  # последние коэффициенты = 1 (для a_i)

    # добавляем имена искусственных переменных
    var_names += artificial_vars

    # озвращаем вспомогательную задачу
    return LinearProblem(
        objective,
        constraints,
        rhs,
        ['='] * len(rhs),   # все ограничения в виде равенств
        var_names,
        is_max=False        # вспомогательная задача — это задача минимума
    )
