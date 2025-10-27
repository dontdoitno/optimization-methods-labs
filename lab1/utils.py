from models import Solution


def write_solution(filename: str, solution: Solution) -> None:
    """
    Записывает решение в файл в удобном формате.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        if solution.found:
            f.write("Оптимальная точка: " + ', '.join(map(str, solution.point)) + '\n')
            f.write("Значение целевой функции: " + str(solution.value) + '\n')
        else:
            f.write("Решение не найдено.\nПричина: " + solution.reason + '\n')
