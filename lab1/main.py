"""
main.py
-------
Главная точка входа программы для решения задачи линейного программирования (ЗЛП).
"""

from lp_reader import read_lp_file
from canonical import to_canonical
from auxiliary import build_auxiliary
from simplex import solve_simplex
from utils import write_solution


def main():
    print("=== Решение задачи линейного программирования ===")

    # 1. Считывание задачи
    problem = read_lp_file('examples/lp_input_example.txt')
    print("[1] Задача считана")

    # 2. Приведение к каноническому виду
    canonical_problem = to_canonical(problem)
    print("[2] Приведена к каноническому виду")

    # 3. Построение вспомогательной задачи
    auxiliary_problem = build_auxiliary(canonical_problem)
    print("[3] Вспомогательная задача сформирована")

    # 4. Решение вспомогательной задачи
    aux_solution = solve_simplex(auxiliary_problem)
    print("[4] Вспомогательная задача решена")

    if not aux_solution.found:
        print("Вспомогательная задача несовместна.")
        write_solution('examples/lp_solution.txt', aux_solution)
        return

    # 5. Переход к основной задаче
    solution = solve_simplex(canonical_problem)
    print("[5] Основная задача решена")

    # 6. Запись результата
    write_solution('examples/lp_solution.txt', solution)
    print("[6] Решение записано в файл examples/lp_solution.txt")


if __name__ == '__main__':
    main()
