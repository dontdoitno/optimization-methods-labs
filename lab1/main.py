import os
from src.lp_reader import read_lp_file
from src.canonical import to_canonical
from src.auxiliary import build_auxiliary
from src.simplex import solve_simplex
from src.utils import write_solution

def main():
    print("=== Решение задачи линейного программирования ===")

    # 1. Считывание задачи из файла
    base_dir = os.path.dirname(__file__)
    input_path = os.path.join(base_dir, 'examples', 'lp_input_example.txt')
    output_path = os.path.join(base_dir, 'examples', 'lp_solution.txt')
    problem = read_lp_file(input_path)
    print("[1] Задача считана")

    # 2. Приведение к каноническому виду
    canonical_problem = to_canonical(problem)
    print("[2] Приведение к каноническому виду выполнено")

    # 3. Формирование вспомогательной задачи
    auxiliary_problem = build_auxiliary(canonical_problem)
    print("[3] Вспомогательная задача сформирована")

    # 4. Решение вспомогательной задачи
    aux_solution = solve_simplex(auxiliary_problem)
    print("[4] Вспомогательная задача решена")
    if not aux_solution.found:
        print("Вспомогательная задача несовместна.")
        write_solution(output_path, aux_solution)
        return

    # 5. Переход к основной задаче (если есть возможность)
    solution = solve_simplex(canonical_problem)
    print("[5] Основная задача решена")

    # 6. Запись ответа
    write_solution(output_path, solution, problem)
    print(f"[6] Решение записано в файл {output_path}")


if __name__ == '__main__':
    main()
