"""
Программа для поиска глобального экстремума липшицевой функции на отрезке.
Использует метод Пиявского (Piyavskii-Shubert).
"""
import os
import argparse
from src.function_parser import parse_function, estimate_lipschitz_constant
from src.test_functions import get_test_function, get_function_string
from src.optimizer import piyavskii_shubert
from src.visualizer import visualize


def main():
    parser = argparse.ArgumentParser(
        description='Поиск глобального минимума липшицевой функции методом Пиявского'
    )
    parser.add_argument(
        '--function', '-f',
        type=str,
        help='Строка функции (например, "x + sin(3.14159*x)" или имя тестовой функции: rastrigin, ackley)'
    )
    parser.add_argument(
        '--a', '-a',
        type=float,
        help='Левый конец отрезка'
    )
    parser.add_argument(
        '--b', '-b',
        type=float,
        help='Правый конец отрезка'
    )
    parser.add_argument(
        '--eps', '-e',
        type=float,
        default=0.01,
        help='Точность вычисления (по умолчанию 0.01)'
    )
    parser.add_argument(
        '--L', '-L',
        type=float,
        default=None,
        help='Константа Липшица (если не указана, будет оценена автоматически)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Путь для сохранения графика'
    )

    args = parser.parse_args()

    # Если аргументы не переданы, используем интерактивный режим или значения по умолчанию
    if args.function is None:
        print("=== Поиск глобального минимума функции ===")
        print("\nДоступные тестовые функции:")
        print("  1. rastrigin - функция Растригина")
        print("  2. ackley - функция Экли")
        print("  3. custom - ввести свою функцию")

        choice = input("\nВыберите функцию (1/2/3 или Enter для rastrigin): ").strip()

        if choice == '1' or choice == '':
            func_name = 'rastrigin'
            func = get_test_function('rastrigin')
            func_str = get_function_string('rastrigin')
        elif choice == '2':
            func_name = 'ackley'
            func = get_test_function('ackley')
            func_str = get_function_string('ackley')
        elif choice == '3':
            func_str = input("Введите функцию (например, 'x + sin(3.14159*x)'): ").strip()
            func = parse_function(func_str)
        else:
            func_name = 'rastrigin'
            func = get_test_function('rastrigin')
            func_str = get_function_string('rastrigin')

        if args.a is None:
            a = float(input("Введите левый конец отрезка (или Enter для -5): ") or "-5")
        else:
            a = args.a

        if args.b is None:
            b = float(input("Введите правый конец отрезка (или Enter для 5): ") or "5")
        else:
            b = args.b

        if args.eps is None:
            eps = float(input("Введите точность (или Enter для 0.01): ") or "0.01")
        else:
            eps = args.eps
    else:
        # Режим с аргументами командной строки
        func_str = args.function

        # Проверяем, является ли это именем тестовой функции
        test_functions = ['rastrigin', 'ackley', 'griewank']
        if func_str.lower() in test_functions:
            func = get_test_function(func_str)
            func_str = get_function_string(func_str)
        else:
            func = parse_function(func_str)

        a = args.a if args.a is not None else -5.0
        b = args.b if args.b is not None else 5.0
        eps = args.eps

    print(f"\nФункция: f(x) = {func_str}")
    print(f"Отрезок: [{a}, {b}]")
    print(f"Точность: {eps}")

    # Оценка константы Липшица
    if args.L is None:
        print("\nОцениваем константу Липшица...")
        L = estimate_lipschitz_constant(func, a, b)
        print(f"Оценка константы Липшица: L = {L:.4f}")
    else:
        L = args.L
        print(f"Используется заданная константа Липшица: L = {L:.4f}")

    # Оптимизация
    print("\nЗапуск оптимизации методом Пиявского...")
    result = piyavskii_shubert(func, a, b, L, eps)

    # Вывод результатов
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ ОПТИМИЗАЦИИ")
    print("="*60)
    print(f"Приближённое значение аргумента: x_min = {result.x_min:.8f}")
    print(f"Минимальное значение функции: f_min = {result.f_min:.8f}")
    print(f"Число итераций: {result.iterations}")
    print(f"Затраченное время: {result.elapsed_time:.4f} секунд")
    print("="*60)

    # Визуализация
    base_dir = os.path.dirname(__file__)
    if args.output is None:
        output_path = os.path.join(base_dir, 'examples', 'optimization_result.png')
    else:
        output_path = args.output

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print("\nСоздание визуализации...")
    visualize(func, result, a, b, save_path=output_path, show_plot=True)

    # Сохранение результатов в файл
    results_file = os.path.join(base_dir, 'examples', 'optimization_results.txt')
    os.makedirs(os.path.dirname(results_file), exist_ok=True)

    with open(results_file, 'w', encoding='utf-8') as f:
        f.write("РЕЗУЛЬТАТЫ ОПТИМИЗАЦИИ\n")
        f.write("="*60 + "\n")
        f.write(f"Функция: f(x) = {func_str}\n")
        f.write(f"Отрезок: [{a}, {b}]\n")
        f.write(f"Точность: {eps}\n")
        f.write(f"Константа Липшица: L = {L:.4f}\n")
        f.write("\n")
        f.write(f"Приближённое значение аргумента: x_min = {result.x_min:.8f}\n")
        f.write(f"Минимальное значение функции: f_min = {result.f_min:.8f}\n")
        f.write(f"Число итераций: {result.iterations}\n")
        f.write(f"Затраченное время: {result.elapsed_time:.4f} секунд\n")

    print(f"\nРезультаты сохранены в {results_file}")


if __name__ == '__main__':
    main()
