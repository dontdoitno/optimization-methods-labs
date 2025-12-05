"""
Главный файл для решения задачи управления инвестиционным портфелем
методом стохастического динамического программирования.
"""
from src.models import PortfolioState, Stage, Scenario, Action
from src.solver import InvestmentSolver


def create_stages() -> list[Stage]:
    """
    Создание этапов планирования с их сценариями.

    Returns:
        Список этапов планирования
    """
    stages = []

    # Этап 1
    stage1 = Stage(
        stage_number=1,
        scenarios=[
            Scenario("Благоприятная", 0.60, (1.20, 1.10, 1.07)),
            Scenario("Нейтральная", 0.30, (1.05, 1.02, 1.03)),
            Scenario("Негативная", 0.10, (0.80, 0.95, 1.00))
        ]
    )
    stages.append(stage1)

    # Этап 2
    stage2 = Stage(
        stage_number=2,
        scenarios=[
            Scenario("Благоприятная", 0.30, (1.40, 1.15, 1.01)),
            Scenario("Нейтральная", 0.20, (1.05, 1.00, 1.00)),
            Scenario("Негативная", 0.50, (0.60, 0.90, 1.00))
        ]
    )
    stages.append(stage2)

    # Этап 3
    stage3 = Stage(
        stage_number=3,
        scenarios=[
            Scenario("Благоприятная", 0.40, (1.15, 1.12, 1.05)),
            Scenario("Нейтральная", 0.40, (1.05, 1.01, 1.01)),
            Scenario("Негативная", 0.20, (0.70, 0.94, 1.00))
        ]
    )
    stages.append(stage3)

    return stages


def print_strategy(strategy_by_stage: dict[int, dict[PortfolioState, Action]],
                   max_value: float):
    """
    Вывод оптимальной стратегии по этапам.

    Args:
        strategy_by_stage: словарь стратегий по этапам
        max_value: максимальное ожидаемое значение
    """
    print("=" * 80)
    print("ОПТИМАЛЬНАЯ СТРАТЕГИЯ УПРАВЛЕНИЯ ПОРТФЕЛЕМ")
    print("=" * 80)
    print()

    for stage_idx in sorted(strategy_by_stage.keys()):
        print(f"ЭТАП {stage_idx + 1}")
        print("-" * 80)

        stage_strategy = strategy_by_stage[stage_idx]
        if not stage_strategy:
            print("  Нет доступных решений для данного этапа.")
            print()
            continue

        # Группируем по состояниям (для читаемости выводим только уникальные действия)
        print(f"  Количество состояний с оптимальными решениями: {len(stage_strategy)}")
        print()

        # Выводим первые несколько примеров для демонстрации
        count = 0
        for state, action in list(stage_strategy.items())[:5]:
            print(f"  Состояние: {state}")
            print(f"  Оптимальное действие: {action}")
            print()
            count += 1

        if len(stage_strategy) > 5:
            print(f"  ... и еще {len(stage_strategy) - 5} состояний")
            print()

    print("=" * 80)
    print(f"МАКСИМАЛЬНЫЙ ОЖИДАЕМЫЙ ДОХОД: {max_value:.2f} д.е.")
    print("=" * 80)


def print_optimal_path(solver: InvestmentSolver, initial_state: PortfolioState):
    """
    Вывод оптимального пути для начального состояния.

    Args:
        solver: решатель задачи
        initial_state: начальное состояние
    """
    print("\n" + "=" * 80)
    print("ОПТИМАЛЬНЫЙ ПУТЬ (ДЕМОНСТРАЦИЯ ДЛЯ ОДНОГО СЦЕНАРИЯ)")
    print("=" * 80)
    print()

    path = solver.get_optimal_path(initial_state)

    for i, node in enumerate(path):
        print(f"Этап {node.stage + 1}:")
        print(f"  Состояние: {node.state}")
        if node.action:
            print(f"  Действие: {node.action}")
        else:
            print(f"  Действие: Нет (терминальное состояние)")
        print(f"  Ожидаемое значение: {node.expected_value:.2f} д.е.")
        print()

    if path:
        print(f"Итоговое значение: {path[-1].expected_value:.2f} д.е.")
    print("=" * 80)


def main():
    """Главная функция программы."""
    print("=" * 80)
    print("РЕШЕНИЕ ЗАДАЧИ УПРАВЛЕНИЯ ИНВЕСТИЦИОННЫМ ПОРТФЕЛЕМ")
    print("Метод: Стохастическое динамическое программирование (обратный ход)")
    print("Критерий: Максимизация математического ожидания дохода (Байеса)")
    print("=" * 80)
    print()

    # Начальное состояние
    initial_state = PortfolioState(
        cb1=100.0,   # Ценная бумага 1
        cb2=800.0,   # Ценная бумага 2
        dep=400.0,   # Депозиты
        cash=600.0   # Свободные средства
    )

    print("НАЧАЛЬНОЕ СОСТОЯНИЕ ПОРТФЕЛЯ:")
    print(f"  ЦБ1: {initial_state.cb1:.2f} д.е.")
    print(f"  ЦБ2: {initial_state.cb2:.2f} д.е.")
    print(f"  Депозиты: {initial_state.dep:.2f} д.е.")
    print(f"  Свободные средства: {initial_state.cash:.2f} д.е.")
    print(f"  Общая стоимость: {initial_state.cb1 + initial_state.cb2 + initial_state.dep + initial_state.cash:.2f} д.е.")
    print()

    print("ПАРАМЕТРЫ ЗАДАЧИ:")
    print("  Комиссии брокеров:")
    print(f"    ЦБ1: 4%")
    print(f"    ЦБ2: 7%")
    print(f"    Депозиты: 5%")
    print("  Минимальные ограничения:")
    print(f"    ЦБ1: не менее 30.00 д.е.")
    print(f"    ЦБ2: не менее 150.00 д.е.")
    print(f"    Депозиты: не менее 100.00 д.е.")
    print()

    # Создаем этапы
    stages = create_stages()

    print("ЭТАПЫ ПЛАНИРОВАНИЯ:")
    for stage in stages:
        print(f"  Этап {stage.stage_number}:")
        for scenario in stage.scenarios:
            print(f"    {scenario.name}: p={scenario.probability:.2f}, "
                  f"множители (ЦБ1, ЦБ2, Деп) = {scenario.multipliers}")
    print()

    # Создаем решатель
    print("Запуск решения задачи...")
    solver = InvestmentSolver(stages, initial_state)

    # Решаем задачу
    max_expected_value, strategy_by_stage = solver.solve()

    print("Решение завершено!")
    print()

    # Выводим результаты
    print_strategy(strategy_by_stage, max_expected_value)

    # Выводим оптимальный путь
    print_optimal_path(solver, initial_state)

    # Дополнительная статистика
    print("\n" + "=" * 80)
    print("СТАТИСТИКА РЕШЕНИЯ")
    print("=" * 80)
    print(f"  Всего состояний в кэше: {len(solver.cache)}")
    print(f"  Начальная стоимость портфеля: {initial_state.cb1 + initial_state.cb2 + initial_state.dep + initial_state.cash:.2f} д.е.")
    print(f"  Максимальный ожидаемый доход: {max_expected_value:.2f} д.е.")
    print(f"  Ожидаемая доходность: {((max_expected_value / (initial_state.cb1 + initial_state.cb2 + initial_state.dep + initial_state.cash)) - 1) * 100:.2f}%")
    print("=" * 80)


if __name__ == "__main__":
    main()
