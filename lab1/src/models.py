from typing import List


class LinearProblem:
    '''
    Класс для хранения параметров задачи линейного программирования (ЗЛП)
    '''

    def __init__(
            self,
            objective: List[float],
            constraints: List[List[float]],
            rhs: List[float],
            signs: List[str],
            var_names: List[str],
            is_max: bool = True,
            var_signs: List[int] | None = None,
            n_original_vars: int | None = None,
        ):
        '''
        :param objective: коэффициенты целевой функции
        :param constraints: матрица коэффициентов ограничений
        :param rhs: правая часть ограничений (b)
        :param signs: знаки ограничений ('<=', '>=', '=')
        :param var_names: имена переменных ['x1', 'x2', ...]
        :param is_max: True если max, False если min
        '''
        self.objective = objective
        self.constraints = constraints
        self.rhs = rhs
        self.signs = signs
        self.var_names = var_names
        self.is_max = is_max
        # var_signs: +1 если переменная неотрицательная (x >= 0), -1 если неположительная (x <= 0)
        # Длина соответствует количеству переменных на текущем этапе
        self.var_signs = var_signs if var_signs is not None else [1] * len(var_names)
        # число исходных переменных до расширений (slack/artificial)
        self.n_original_vars = n_original_vars if n_original_vars is not None else len(var_names)


class Solution:
    '''

    '''

    def __init__(
            self,
            point: List[float],
            value: float,
            found: bool,
            reason: str = ''
    ):
        self.point = point
        self.value = value
        self.found = found
        self.reason = reason


    def __repr__(self) -> str:
        if self.found:
            return f'Оптимальная точка: {self.point}, значение целевой функции: {self.value}'
        else:
            return f'Решение не найдено: {self.reason}'
