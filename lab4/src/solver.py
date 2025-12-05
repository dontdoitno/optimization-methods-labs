"""
Реализация решения задачи управления портфелем методом стохастического
динамического программирования (обратный ход, уравнения Беллмана).
"""
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
from src.models import PortfolioState, Action, Stage, Scenario


# Размеры пакетов для операций
PACKET_SIZES = {
    'cb1': 25.0,   # 1/4 от начальной стоимости ЦБ1 (100)
    'cb2': 200.0,  # 1/4 от начальной стоимости ЦБ2 (800)
    'dep': 100.0   # 1/4 от начальной стоимости Деп (400)
}

# Комиссии брокеров (в долях от суммы операции)
COMMISSION_RATES = {
    'cb1': 0.04,   # 4% для ЦБ1
    'cb2': 0.07,   # 7% для ЦБ2
    'dep': 0.05    # 5% для депозитов
}

# Минимальные ограничения на активы (в д.е.)
MIN_VALUES = {
    'cb1': 30.0,   # Минимум для ЦБ1
    'cb2': 150.0,  # Минимум для ЦБ2
    'dep': 100.0   # Минимум для депозитов
}


@dataclass
class DecisionNode:
    """
    Узел дерева решений: состояние и оптимальное действие на данном этапе.
    """
    state: PortfolioState
    action: Optional[Action]
    expected_value: float
    stage: int


class InvestmentSolver:
    """
    Решатель задачи оптимизации инвестиционного портфеля методом ДП.

    Использует обратный ход динамического программирования с кэшированием
    состояний для оптимизации производительности.
    """

    def __init__(self, stages: List[Stage], initial_state: PortfolioState):
        """
        Инициализация решателя.

        Args:
            stages: список этапов планирования (от первого к последнему)
            initial_state: начальное состояние портфеля
        """
        self.stages = stages
        self.initial_state = initial_state
        # Кэш для мемоизации: (stage, state) -> (expected_value, optimal_action)
        self.cache: Dict[Tuple[int, PortfolioState], Tuple[float, Optional[Action]]] = {}
        # История оптимальных решений для каждого состояния
        self.optimal_strategy: Dict[Tuple[int, PortfolioState], Action] = {}

    def _is_valid_state(self, state: PortfolioState) -> bool:
        """
        Проверка корректности состояния (все значения неотрицательны и
        соблюдены минимальные ограничения).

        Args:
            state: состояние для проверки

        Returns:
            True, если состояние корректно
        """
        return (state.cb1 >= MIN_VALUES['cb1'] and
                state.cb2 >= MIN_VALUES['cb2'] and
                state.dep >= MIN_VALUES['dep'] and
                state.cash >= 0)

    def _apply_action(self, state: PortfolioState, action: Action) -> Optional[PortfolioState]:
        """
        Применение действия к состоянию с проверкой ограничений и учетом комиссий.

        Ограничения:
        - Нельзя продать больше, чем есть (с учетом минимальных ограничений)
        - Нельзя купить больше, чем позволяют свободные средства (с учетом комиссий)
        - После операции активы должны быть не меньше минимальных значений

        Args:
            state: текущее состояние
            action: действие для применения

        Returns:
            Новое состояние после действия или None, если действие недопустимо
        """
        # Вычисляем изменения в активах (без учета комиссий)
        cb1_change = action.cb1_packages * PACKET_SIZES['cb1']
        cb2_change = action.cb2_packages * PACKET_SIZES['cb2']
        dep_change = action.dep_packages * PACKET_SIZES['dep']

        # Вычисляем комиссии
        total_commission = 0.0

        # Комиссия при покупке (положительное количество пакетов)
        if action.cb1_packages > 0:
            total_commission += cb1_change * COMMISSION_RATES['cb1']
        if action.cb2_packages > 0:
            total_commission += cb2_change * COMMISSION_RATES['cb2']
        if action.dep_packages > 0:
            total_commission += dep_change * COMMISSION_RATES['dep']

        # Комиссия при продаже (отрицательное количество пакетов)
        if action.cb1_packages < 0:
            total_commission += abs(cb1_change) * COMMISSION_RATES['cb1']
        if action.cb2_packages < 0:
            total_commission += abs(cb2_change) * COMMISSION_RATES['cb2']
        if action.dep_packages < 0:
            total_commission += abs(dep_change) * COMMISSION_RATES['dep']

        # Вычисляем новое состояние активов
        new_cb1 = state.cb1 + cb1_change
        new_cb2 = state.cb2 + cb2_change
        new_dep = state.dep + dep_change

        # Вычисляем изменение свободных средств
        # При покупке: тратим стоимость пакета + комиссию
        # При продаже: получаем стоимость пакета - комиссию
        cash_change = -(cb1_change + cb2_change + dep_change) - total_commission
        new_cash = state.cash + cash_change

        # Проверка ограничений
        if (new_cb1 < MIN_VALUES['cb1'] or
            new_cb2 < MIN_VALUES['cb2'] or
            new_dep < MIN_VALUES['dep'] or
            new_cash < 0):
            return None

        return PortfolioState(new_cb1, new_cb2, new_dep, new_cash)

    def _apply_scenario(self, state: PortfolioState, scenario: Scenario) -> PortfolioState:
        """
        Применение сценария (изменение стоимости активов) к состоянию.

        Доходность применяется к сумме активов ПОСЛЕ принятия решения.

        Args:
            state: состояние после принятия решения
            scenario: сценарий с коэффициентами изменения

        Returns:
            Новое состояние после применения сценария
        """
        mult_cb1, mult_cb2, mult_dep = scenario.multipliers

        new_cb1 = state.cb1 * mult_cb1
        new_cb2 = state.cb2 * mult_cb2
        new_dep = state.dep * mult_dep
        # Свободные средства не изменяются (не приносят доход)

        return PortfolioState(new_cb1, new_cb2, new_dep, state.cash)

    def _generate_actions(self, state: PortfolioState) -> List[Action]:
        """
        Генерация всех допустимых действий для данного состояния.

        Генерирует все комбинации покупок/продаж пакетов в пределах ограничений.

        Args:
            state: текущее состояние

        Returns:
            Список допустимых действий
        """
        actions = []

        # Определяем максимальное количество пакетов для продажи
        # (нельзя продать так, чтобы осталось меньше минимального значения)
        max_sell_cb1 = int((state.cb1 - MIN_VALUES['cb1']) / PACKET_SIZES['cb1'])
        max_sell_cb2 = int((state.cb2 - MIN_VALUES['cb2']) / PACKET_SIZES['cb2'])
        max_sell_dep = int((state.dep - MIN_VALUES['dep']) / PACKET_SIZES['dep'])

        # Определяем максимальное количество пакетов для покупки
        # (ограничено свободными средствами с учетом комиссий)
        # При покупке нужно заплатить: стоимость_пакета * (1 + комиссия)
        max_buy_cb1 = int(state.cash / (PACKET_SIZES['cb1'] * (1 + COMMISSION_RATES['cb1'])))
        max_buy_cb2 = int(state.cash / (PACKET_SIZES['cb2'] * (1 + COMMISSION_RATES['cb2'])))
        max_buy_dep = int(state.cash / (PACKET_SIZES['dep'] * (1 + COMMISSION_RATES['dep'])))

        # Генерируем все комбинации (ограничиваем диапазон для производительности)
        # Используем разумные ограничения: от -2 до +2 пакетов для каждого актива
        # Это покрывает большинство практических случаев
        for cb1_p in range(-min(2, max_sell_cb1), min(3, max_buy_cb1) + 1):
            for cb2_p in range(-min(2, max_sell_cb2), min(3, max_buy_cb2) + 1):
                for dep_p in range(-min(2, max_sell_dep), min(3, max_buy_dep) + 1):
                    action = Action(cb1_p, cb2_p, dep_p)
                    # Проверяем допустимость действия
                    new_state = self._apply_action(state, action)
                    if new_state is not None:
                        actions.append(action)

        return actions

    def _terminal_value(self, state: PortfolioState) -> float:
        """
        Функция терминального значения (доходность на последнем этапе).

        На последнем этапе доходность - это общая стоимость портфеля.

        Args:
            state: терминальное состояние

        Returns:
            Общая стоимость портфеля
        """
        return state.cb1 + state.cb2 + state.dep + state.cash

    def solve(self) -> Tuple[float, Dict[int, Dict[PortfolioState, Action]]]:
        """
        Решение задачи методом обратного хода ДП.

        Returns:
            Кортеж (максимальный ожидаемый доход, стратегия по этапам)
        """
        # Очищаем кэш перед решением
        self.cache.clear()
        self.optimal_strategy.clear()

        # Обратный ход: начинаем с последнего этапа
        num_stages = len(self.stages)

        # Вызываем рекурсивную функцию для начального состояния и первого этапа
        max_expected_value = self._bellman_recursive(self.initial_state, 0)

        # Формируем стратегию по этапам
        strategy_by_stage: Dict[int, Dict[PortfolioState, Action]] = {}
        for stage_idx in range(num_stages):
            strategy_by_stage[stage_idx] = {}
            # Собираем все оптимальные действия для данного этапа из кэша
            for (s_idx, state), (_, action) in self.cache.items():
                if s_idx == stage_idx and action is not None:
                    strategy_by_stage[stage_idx][state] = action

        return max_expected_value, strategy_by_stage

    def _bellman_recursive(self, state: PortfolioState, stage_idx: int) -> float:
        """
        Рекурсивная функция для вычисления уравнения Беллмана.

        Уравнение Беллмана для стохастического случая:
        V_t(s) = max_{a} E[R(s, a, ξ) + V_{t+1}(f(s, a, ξ))]

        где:
        - V_t(s) - функция ценности на этапе t в состоянии s
        - a - действие (управление)
        - ξ - случайная величина (сценарий)
        - R(s, a, ξ) - доходность на этапе t
        - f(s, a, ξ) - функция перехода состояния

        Args:
            state: текущее состояние
            stage_idx: индекс текущего этапа (0-based)

        Returns:
            Максимальное ожидаемое значение функции ценности
        """
        # Проверка кэша
        cache_key = (stage_idx, state)
        if cache_key in self.cache:
            return self.cache[cache_key][0]

        # Если это последний этап, возвращаем терминальное значение
        if stage_idx >= len(self.stages):
            value = self._terminal_value(state)
            self.cache[cache_key] = (value, None)
            return value

        stage = self.stages[stage_idx]
        best_value = float('-inf')
        best_action: Optional[Action] = None

        # Генерируем все допустимые действия
        actions = self._generate_actions(state)

        # Если нет допустимых действий, возвращаем терминальное значение
        if not actions:
            value = self._terminal_value(state)
            self.cache[cache_key] = (value, None)
            return value

        # Для каждого действия вычисляем ожидаемое значение
        for action in actions:
            # Применяем действие
            state_after_action = self._apply_action(state, action)
            if state_after_action is None:
                continue

            # Вычисляем ожидаемое значение по всем сценариям
            expected_value = 0.0

            for scenario in stage.scenarios:
                # Применяем сценарий к состоянию после действия
                state_after_scenario = self._apply_scenario(state_after_action, scenario)

                # Рекурсивно вычисляем значение для следующего этапа
                future_value = self._bellman_recursive(state_after_scenario, stage_idx + 1)

                # Добавляем вклад сценария (с учетом вероятности)
                expected_value += scenario.probability * future_value

            # Обновляем лучшее значение и действие
            if expected_value > best_value:
                best_value = expected_value
                best_action = action

        # Сохраняем в кэш
        self.cache[cache_key] = (best_value, best_action)
        if best_action is not None:
            self.optimal_strategy[cache_key] = best_action

        return best_value

    def get_optimal_path(self, state: PortfolioState, stage_idx: int = 0) -> List[DecisionNode]:
        """
        Получение оптимального пути (последовательности решений) для заданного состояния.

        Args:
            state: начальное состояние
            stage_idx: начальный этап

        Returns:
            Список узлов решений (состояние, действие, ожидаемое значение)
        """
        path = []
        current_state = state
        current_stage = stage_idx

        while current_stage < len(self.stages):
            cache_key = (current_stage, current_state)
            if cache_key not in self.cache:
                break

            expected_value, action = self.cache[cache_key]
            path.append(DecisionNode(current_state, action, expected_value, current_stage))

            if action is None:
                break

            # Применяем действие
            state_after_action = self._apply_action(current_state, action)
            if state_after_action is None:
                break

            # Применяем первый сценарий для демонстрации (можно выбрать любой)
            # В реальности путь зависит от реализовавшегося сценария
            if current_stage < len(self.stages):
                scenario = self.stages[current_stage].scenarios[0]  # Берем первый сценарий
                current_state = self._apply_scenario(state_after_action, scenario)
                current_stage += 1
            else:
                break

        return path
