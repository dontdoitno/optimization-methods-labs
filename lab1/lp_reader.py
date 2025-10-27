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
        if not part or not part.strip():
            continue
        if 'x' in part:
            parts = part.split('x')
            coeff = float(parts[0])
            var_index = int(parts[1]) - 1  # x1 -> index 0, x2 -> index 1, etc.
            # расширяем obj_coeffs до нужного размера
            while len(obj_coeffs) <= var_index:
                obj_coeffs.append(0.0)
            obj_coeffs[var_index] = coeff

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
            part = part.strip()
            if not part or not part.strip():
                continue
            if 'x' in part:
                parts = part.split('x')
                coeff = float(parts[0])
                var_index = int(parts[1]) - 1  # x1 -> index 0, x2 -> index 1, etc.
                # расширяем row до нужного размера
                while len(row) <= var_index:
                    row.append(0.0)
                row[var_index] = coeff
        constraints.append(row)

    # Убеждаемся что все строки имеют одинаковую длину
    max_vars = max(len(obj_coeffs), max(len(row) for row in constraints) if constraints else 0)
    # Расширяем obj_coeffs до максимального размера
    while len(obj_coeffs) < max_vars:
        obj_coeffs.append(0.0)
    # Расширяем каждую строку constraints до максимального размера
    for row in constraints:
        while len(row) < max_vars:
            row.append(0.0)

    var_names = [f"x{i+1}" for i in range(max_vars)]
    return LinearProblem(obj_coeffs, constraints, rhs, signs, var_names, is_max)
