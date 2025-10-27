# utils.py

from models import Solution, LinearProblem

def write_solution(filename: str, solution: Solution, problem: LinearProblem = None):
    with open(filename, 'w', encoding='utf-8') as f:
        if solution.found:
            f.write("ОПТИМАЛЬНОЕ РЕШЕНИЕ\n")
            f.write("Переменная : Значение\n")
            varnames = problem.varnames if problem else [f"x{i+1}" for i in range(len(solution.point))]
            for name, val in zip(varnames, solution.point):
                f.write(f"{name:10}: {val:15.8f}\n")
            f.write("\n")
            f.write(f"Значение целевой функции: {solution.value:.8f}\n\n")

            if problem:
                f.write("Проверка ограничений:\n")
                for i, (row, sign, rhs) in enumerate(zip(problem.constraints, problem.signs, problem.rhs)):
                    left = sum(val*x for val, x in zip(row, solution.point))
                    f.write(f"Ограничение {i+1}: {left:.8f} {sign} {rhs}\n")
        else:
            f.write("Решение не найдено.\n")
            f.write(solution.reason)
