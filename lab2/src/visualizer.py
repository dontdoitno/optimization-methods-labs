"""
Визуализация функции, ломаной линии и результатов оптимизации.
"""
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Callable
from src.optimizer import OptimizationResult


def visualize(
    func: Callable[[float], float],
    result: OptimizationResult,
    a: float,
    b: float,
    save_path: str = None,
    show_plot: bool = True
) -> None:
    """
    Визуализирует функцию, ломаную линию и найденный минимум.

    :param func: исходная функция
    :param result: результат оптимизации
    :param a: левый конец отрезка
    :param b: правый конец отрезка
    :param save_path: путь для сохранения графика (опционально)
    :param show_plot: показывать ли график
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    # Строим график исходной функции
    x_fine = np.linspace(a, b, 1000)
    y_fine = [func(x) for x in x_fine]
    ax.plot(x_fine, y_fine, 'b-', linewidth=2, label='Исходная функция f(x)')

    # Строим ломаную линию (нижнюю оценку)
    if result.broken_line_points:
        x_broken = [p[0] for p in result.broken_line_points]
        y_broken = [p[1] for p in result.broken_line_points]
        ax.plot(x_broken, y_broken, 'r--', linewidth=1.5, alpha=0.7, label='Ломаная линия (нижняя оценка)')

    # Отмечаем вычисленные точки функции
    if result.function_points:
        x_computed = [p[0] for p in result.function_points]
        y_computed = [p[1] for p in result.function_points]
        ax.scatter(x_computed, y_computed, c='green', s=30, alpha=0.6, zorder=5, label='Вычисленные точки')

    # Отмечаем найденный минимум
    ax.scatter([result.x_min], [result.f_min], c='red', s=200, marker='*',
               zorder=10, label=f'Найденный минимум: x={result.x_min:.6f}, f={result.f_min:.6f}')

    # Вертикальная линия в точке минимума
    ax.axvline(x=result.x_min, color='red', linestyle=':', alpha=0.5, linewidth=1)

    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('f(x)', fontsize=12)
    ax.set_title('Глобальная оптимизация методом Пиявского', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"График сохранён в {save_path}")

    if show_plot:
        plt.show()
    else:
        plt.close()
