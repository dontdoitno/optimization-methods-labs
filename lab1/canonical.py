from models import LinearProblem


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
    slack_count = 0

    for row, sign, r in zip(lp.constraints, lp.signs, lp.rhs):
        extra_vars = [0] * len(lp.constraints)  # вектор для добавчных переменных
        if sign == '<=':
            extra_vars[slack_count] = 1
        elif sign == '>=':
            extra_vars[slack_count] = -1

        # объединяем основное ограничение с добавочными переменными
        row_canon = row + extra_vars
        canonical_constraits.append(row_canon)
        canonical_rhs.append(r)
        canonical_signs.append('=')
        slack_count += 1

    # новые имена переменных: исходные + добавочные (s1, ...)
    var_names = lp.var_names + [f's{i + 1}' for i in range(slack_count)]

    # Целевая функция тоже должна быть расширена нулями для новых переменных
    extended_obj = lp.objective + [0] * slack_count

    return LinearProblem(
        extended_obj,
        canonical_constraits,
        canonical_rhs,
        canonical_signs,
        var_names,
        lp.is_max
    )
