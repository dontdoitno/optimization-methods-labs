from src.models import Solution, LinearProblem


def write_solution(filename: str, solution: Solution, problem: LinearProblem | None = None) -> None:
    """
    Записывает решение. Если передан problem, то выводит только исходные переменные,
    учитывая их знаки (x>=0 или x<=0).
    """
    with open(filename, 'w', encoding='utf-8') as f:
        if not solution.found:
            f.write("Решение не найдено.\nПричина: " + solution.reason + "\n")
            return

        if problem is None:
            f.write("Оптимальная точка: " + ', '.join(map(str, solution.point)) + "\n")
            f.write("Значение целевой функции: " + str(solution.value) + "\n")
            return

        k = problem.n_original_vars
        y = solution.point[:k]
        signs = problem.var_signs[:k]
        x_original = [signs[i] * y[i] for i in range(k)]

        f.write("Оптимальные значения исходных переменных:\n")
        for name, val in zip(problem.var_names[:k], x_original):
            f.write(f"  {name}: {val}\n")
        f.write("Значение целевой функции: " + str(solution.value) + "\n")
