from src.models import LinearProblem


def build_auxiliary(lp: LinearProblem) -> LinearProblem:
    """
    Формирует вспомогательную задачу (первый этап симплекс-метода):
    - Меняет знак строк с отрицательными правыми частями.
    - Добавляет искусственные переменные (a1, a2, ...).
    - Целевая функция: минимизировать сумму искусственных переменных.
    """

    # копируем исходные данные, чтобы не менять оригинал
    constraints = [row[:] for row in lp.constraints]
    rhs = lp.rhs[:]
    var_names = lp.var_names[:]
    var_signs = lp.var_signs[:]

    artificial_vars = []

    # сначала нормализуем строки, чтобы у всех одинаковая длина
    n_constraints = len(rhs)
    n_vars = len(constraints[0])

    # добавляем искусственные переменные
    for i in range(n_constraints):
        b = rhs[i]
        if b < 0:
            # меняем знак у строки и свободного члена
            constraints[i] = [-x for x in constraints[i]]
            rhs[i] = -b

    # добавляем искусственные переменные
    for i in range(n_constraints):
        for j in range(n_constraints):
            constraints[j].append(1 if i == j else 0)
        artificial_vars.append(f"a{i+1}")

    # целевая функция: минимизировать сумму искусственных переменных
    # исходные коэффициенты = 0, коэффициенты при искусственных = 1
    objective = [0] * (n_vars + len(artificial_vars))
    for i in range(len(artificial_vars)):
        objective[n_vars + i] = 1

    var_names += artificial_vars
    var_signs += [1] * len(artificial_vars)

    return LinearProblem(
        objective=objective,
        constraints=constraints,
        rhs=rhs,
        signs=['='] * len(rhs),
        var_names=var_names,
        is_max=False,
        var_signs=var_signs,
        n_original_vars=lp.n_original_vars,
    )
