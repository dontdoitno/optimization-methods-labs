"""
Модели данных для задачи управления инвестиционным портфелем.
"""
from dataclasses import dataclass
from typing import Tuple, List, Optional


@dataclass(frozen=True)
class PortfolioState:
    """
    Состояние портфеля: количество активов и свободные средства.

    Атрибуты:
        cb1: объем ценной бумаги 1 (в д.е.)
        cb2: объем ценной бумаги 2 (в д.е.)
        dep: объем депозитов (в д.е.)
        cash: свободные средства (в д.е.)
    """
    cb1: float
    cb2: float
    dep: float
    cash: float

    def __str__(self) -> str:
        return f"State(CB1={self.cb1:.2f}, CB2={self.cb2:.2f}, Dep={self.dep:.2f}, Cash={self.cash:.2f})"


@dataclass(frozen=True)
class Action:
    """
    Действие (управление): количество пакетов для покупки/продажи.

    Отрицательные значения означают продажу, положительные - покупку.

    Атрибуты:
        cb1_packages: количество пакетов ЦБ1 (1 пакет = 25 д.е.)
        cb2_packages: количество пакетов ЦБ2 (1 пакет = 200 д.е.)
        dep_packages: количество пакетов Деп (1 пакет = 100 д.е.)
    """
    cb1_packages: int
    cb2_packages: int
    dep_packages: int

    def __str__(self) -> str:
        return f"Action(CB1={self.cb1_packages:+d}, CB2={self.cb2_packages:+d}, Dep={self.dep_packages:+d})"


@dataclass
class Scenario:
    """
    Сценарий развития событий на этапе.

    Атрибуты:
        name: название сценария (Благоприятная, Нейтральная, Негативная)
        probability: вероятность сценария
        multipliers: коэффициенты изменения стоимости (cb1, cb2, dep)
    """
    name: str
    probability: float
    multipliers: Tuple[float, float, float]  # (cb1_mult, cb2_mult, dep_mult)


@dataclass
class Stage:
    """
    Этап планирования с набором возможных сценариев.

    Атрибуты:
        stage_number: номер этапа (1, 2, 3)
        scenarios: список возможных сценариев
    """
    stage_number: int
    scenarios: List[Scenario]
