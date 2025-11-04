from src.models import LinearProblem


def to_canonical(lp: LinearProblem) -> LinearProblem:
    '''
    Приводит ЗЛП к каноническому виду:
    - заменяет неравенства на равенства
    - все переменные неотрицательные
    - добавляет дополнительные переменные (если потребуется)
    '''

    canonical_constraits = []
    canonical_rhs = []
    canonical_signs = []

    # Шаг 0: учтём знаки переменных, чтобы перейти к неотрицательным переменным
    base_var_count = len(lp.var_names)
    transformed_constraints = []
    for row in lp.constraints:
        transformed_row = [row[j] * (lp.var_signs[j] if j < base_var_count else 1) for j in range(base_var_count)]
        transformed_constraints.append(transformed_row)
    transformed_objective = [lp.objective[j] * (lp.var_signs[j] if j < base_var_count else 1) for j in range(base_var_count)]

    # Сначала подсчитаем, сколько slack переменных понадобится
    num_slack_vars = sum(1 for sign in lp.signs if sign != '=')

    slack_count = 0

    for row, sign, r in zip(transformed_constraints, lp.signs, lp.rhs):
        extra_vars = [0] * num_slack_vars  # вектор для дополнительных переменных
        if sign == '<=':
            extra_vars[slack_count] = 1
            slack_count += 1
        elif sign == '>=':
            extra_vars[slack_count] = -1
            slack_count += 1

        # объединяем основное ограничение с добавочными переменными
        row_canon = row + extra_vars
        canonical_constraits.append(row_canon)
        canonical_rhs.append(r)
        canonical_signs.append('=')

    # новые имена переменных: исходные + добавочные (s1, ...)
    var_names = lp.var_names + [f's{i + 1}' for i in range(num_slack_vars)]

    # Целевая функция тоже должна быть расширена нулями для новых переменных
    extended_obj = transformed_objective + [0] * num_slack_vars

    # Все переменные теперь неотрицательные; добавочные тоже неотрицательные
    new_var_signs = [1] * len(var_names)

    return LinearProblem(
        extended_obj,
        canonical_constraits,
        canonical_rhs,
        canonical_signs,
        var_names,
        lp.is_max,
        var_signs=new_var_signs,
        n_original_vars=lp.n_original_vars,
    )
