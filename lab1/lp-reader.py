from typing import List
from models import LinearProblem


def read_lp_file(filename: str) -> LinearProblem:
    '''
    Считывает задачу линейного программирования из текстового файла.
    Формат:
        max/min
        Z = 1x1 + 2x2 + 3x3
        1x1 + 1x2 <= 5
        2x1 + 3x2 >= 8
        ...

    :param filename: путь к файлу
    :return: объект LinearProblem
    '''
    with open(filename, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()]

    # определяем тип задачи (максимизация/миниманизация)
    is_max = lines[0].lower().startswith('max')

    # целевая функция Z
    objective_str = lines[1].split('=')[1].strip()
    obj_coeffs: List[float] = []

    for part in objective_str.replace('-', '+-').split('+'):
        part = part.strip()
        if not part:
            continue
        coeff = part.split('x')[0]
        obj_coeffs.append(float(coeff))

    # ограничения
    constraints, rhs, signs = [], [], []

    for line in lines[2:]:
        if any(sign in line for sign in ['<=', '>=', '=']):
            if '<=' in line:
                sign = '<='
            elif '>=' in line:
                sign = '>='
            else:
                sign = '='

        left, right = line.split(sign)
        rhs.append(float(right.strip()))
        signs.append(sign)

        row = []
        for part in left.replace('-', '+-').split('+'):
            part.split()
            if not part:
                continue
            coeff = part.split('x')[0]
            row.append(float(coeff))
        constraints.append(row)

    var_names = [f"x{i+1}" for i in range(len(constraints[0]))]
    return LinearProblem(obj_coeffs, constraints, rhs, signs, var_names, is_max)
