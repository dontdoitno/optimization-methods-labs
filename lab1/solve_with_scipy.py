import os
from typing import Tuple

import numpy as np
from scipy.optimize import linprog

from src.lp_reader import read_lp_file


def build_scipy_matrices() -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[Tuple[float | None, float | None]], bool]:
    base_dir = os.path.dirname(__file__)
    input_path = os.path.join(base_dir, 'examples', 'lp_input_example.txt')
    lp = read_lp_file(input_path)

    # SciPy решает задачу минимизации: min c^T x
    c = np.array(lp.objective, dtype=float)
    if lp.is_max:
        c = -c

    A_ub, b_ub, A_eq, b_eq = [], [], [], []
    for row, sign, rhs in zip(lp.constraints, lp.signs, lp.rhs):
        if sign == '<=':
            A_ub.append(row)
            b_ub.append(rhs)
        elif sign == '>=':
            A_ub.append([-v for v in row])
            b_ub.append(-rhs)
        else:
            A_eq.append(row)
            b_eq.append(rhs)

    bounds = []
    for s in lp.var_signs[:lp.n_original_vars]:
        if s >= 0:
            bounds.append((0, None))
        else:
            bounds.append((None, 0))

    return (
        np.array(A_ub, dtype=float) if A_ub else None,
        np.array(b_ub, dtype=float) if b_ub else None,
        np.array(A_eq, dtype=float) if A_eq else None,
        np.array(b_eq, dtype=float) if b_eq else None,
        bounds,
        lp.is_max,
    )


def main() -> None:
    A_ub, b_ub, A_eq, b_eq, bounds, is_max = build_scipy_matrices()
    base_dir = os.path.dirname(__file__)
    input_path = os.path.join(base_dir, 'examples', 'lp_input_example.txt')
    lp = read_lp_file(input_path)

    c = np.array(lp.objective, dtype=float)
    if is_max:
        c = -c

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    output_path = os.path.join(base_dir, 'examples', 'lp_solution_scipy.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        if not res.success:
            f.write('Решение не найдено.\n')
            f.write(str(res.message))
            return
        x = res.x
        f.write('Оптимальные значения исходных переменных (SciPy):\n')
        for name, val in zip(lp.var_names[:lp.n_original_vars], x[:lp.n_original_vars]):
            f.write(f'  {name}: {val}\n')
        val = float(res.fun)
        if is_max:
            val = -val
        f.write('Значение целевой функции (SciPy): ' + str(val) + '\n')


if __name__ == '__main__':
    main()
