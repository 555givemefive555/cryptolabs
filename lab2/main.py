import os
import math
import random
from collections import Counter
from pathlib import Path


class EntropyCalculator:

    @staticmethod
    def calculate_frequencies(data: bytes):
        if not data:
            return {}, 0

        total_bytes = len(data)
        frequency = Counter(data)

        frequencies = {}
        for byte_val, count in frequency.items():
            frequencies[byte_val] = count / total_bytes

        return frequencies, total_bytes

    @staticmethod
    def calculate_entropy(data: bytes):
        if not data:
            return 0.0

        frequencies, total_bytes = EntropyCalculator.calculate_frequencies(data)

        entropy = 0.0
        for prob in frequencies.values():
            if prob > 0:
                entropy -= prob * math.log2(prob)

        return entropy

    @staticmethod
    def analyze_file(filepath: str):
        try:
            with open(filepath, 'rb') as f:
                data = f.read()

            if not data:
                return {
                    'error': 'Файл пуст',
                    'entropy': 0.0,
                    'unique_symbols': 0,
                    'total_bytes': 0
                }

            frequencies, total_bytes = EntropyCalculator.calculate_frequencies(data)
            entropy = EntropyCalculator.calculate_entropy(data)

            unique_symbols = len(frequencies)
            max_possible_entropy = math.log2(256)

            result = {
                'entropy': entropy,
                'max_entropy': max_possible_entropy,
                'unique_symbols': unique_symbols,
                'total_bytes': total_bytes,
                'frequencies': frequencies,
                'entropy_percent': (entropy / max_possible_entropy) * 100 if max_possible_entropy > 0 else 0
            }

            return result

        except FileNotFoundError:
            return {'error': f'Файл не найден: {filepath}'}
        except Exception as e:
            return {'error': f'Ошибка: {str(e)}'}


class FileGenerator:

    @staticmethod
    def generate_uniform_file(filepath: str, size_bytes: int, char: int = 65):
        """Генерация файла из одинаковых символов"""
        with open(filepath, 'wb') as f:
            f.write(bytes([char]) * size_bytes)
        print(f"Создан файл с одинаковыми символами: {filepath} (размер: {size_bytes} байт)")

    @staticmethod
    def generate_random_binary_file(filepath: str, size_bytes: int):
        """Генерация файла из случайных битов (0 и 1)"""
        with open(filepath, 'wb') as f:
            for _ in range(size_bytes):
                f.write(bytes([random.choice([0, 1])]))
        print(f"Создан файл со случайными битами: {filepath} (размер: {size_bytes} байт)")

    @staticmethod
    def generate_random_byte_file(filepath: str, size_bytes: int):
        """Генерация файла из случайных байт (0-255)"""
        with open(filepath, 'wb') as f:
            for _ in range(size_bytes):
                f.write(bytes([random.randint(0, 255)]))
        print(f"Создан файл со случайными байтами: {filepath} (размер: {size_bytes} байт)")

    @staticmethod
    def generate_text_file(filepath: str, size_bytes: int):
        """Генерация текстового файла с английским текстом"""
        text_chars = list(range(97, 123)) + [32]  # a-z и пробел
        with open(filepath, 'wb') as f:
            for _ in range(size_bytes):
                f.write(bytes([random.choice(text_chars)]))
        print(f"Создан текстовый файл: {filepath} (размер: {size_bytes} байт)")

    @staticmethod
    def generate_pattern_file(filepath: str, size_bytes: int, pattern: list):
        """Генерация файла с заданным паттерном"""
        with open(filepath, 'wb') as f:
            for i in range(size_bytes):
                f.write(bytes([pattern[i % len(pattern)]]))
        print(f"Создан файл с паттерном: {filepath} (размер: {size_bytes} байт)")


def print_frequencies(frequencies, top_n=10):
    """Вывод наиболее частых символов"""
    if not frequencies:
        return

    sorted_freq = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)[:top_n]

    print("\nНаиболее частые символы:")
    for byte_val, prob in sorted_freq:
        char_repr = chr(byte_val) if 32 <= byte_val <= 126 else f'[{byte_val}]'
        print(f"  {char_repr} (код {byte_val}): {prob:.6f} ({prob * 100:.4f}%)")


def main():
    print("ВЫЧИСЛЕНИЕ ИНФОРМАЦИОННОЙ ЭНТРОПИИ ФАЙЛА")

    calculator = EntropyCalculator()
    generator = FileGenerator()

    test_files_dir = Path("test_files")
    test_files_dir.mkdir(exist_ok=True)

    while True:
        print("\nМЕНЮ:")
        print("1. Анализ существующего файла")
        print("2. Сгенерировать тестовые файлы и проанализировать")
        print("3. Сравнить энтропию разных типов файлов")
        print("0. Выход")

        choice = input("\nВыберите действие: ").strip()

        if choice == '0':
            print("До свидания!")
            break

        elif choice == '1':
            filepath = input("Введите путь к файлу: ").strip()

            if not os.path.exists(filepath):
                print("Файл не существует!")
                continue

            result = calculator.analyze_file(filepath)

            if 'error' in result:
                print(result['error'])
            else:
                print(f"\nРезультаты анализа файла: {filepath}")
                print(f"Размер файла: {result['total_bytes']} байт")
                print(f"Количество уникальных символов: {result['unique_symbols']}")
                print(f"Энтропия: {result['entropy']:.6f} бит/символ")
                print(f"Максимальная возможная энтропия (для 256 символов): {result['max_entropy']:.6f} бит/символ")
                print(f"Относительная энтропия: {result['entropy_percent']:.2f}%")

                if input("\nПоказать частоты символов? (y/n): ").lower() == 'y':
                    print_frequencies(result['frequencies'])

        elif choice == '2':
            size = int(input("Введите размер файлов в байтах (например, 10000): "))

            files_to_analyze = []

            print("\nГенерация тестовых файлов...")

            uniform_file = test_files_dir / "uniform.txt"
            generator.generate_uniform_file(str(uniform_file), size, 65)
            files_to_analyze.append(("Файл из одинаковых символов 'A'", str(uniform_file)))

            binary_file = test_files_dir / "random_binary.bin"
            generator.generate_random_binary_file(str(binary_file), size)
            files_to_analyze.append(("Файл из случайных битов (0 и 1)", str(binary_file)))

            random_file = test_files_dir / "random_bytes.bin"
            generator.generate_random_byte_file(str(random_file), size)
            files_to_analyze.append(("Файл из случайных байт (0-255)", str(random_file)))

            text_file = test_files_dir / "random_text.txt"
            generator.generate_text_file(str(text_file), size)
            files_to_analyze.append(("Текстовый файл (a-z и пробел)", str(text_file)))

            pattern_file = test_files_dir / "pattern.bin"
            generator.generate_pattern_file(str(pattern_file), size, [65, 66, 67])
            files_to_analyze.append(("Файл с паттерном ABCABC...", str(pattern_file)))

            print("\n" + "-" * 50)
            print("РЕЗУЛЬТАТЫ АНАЛИЗА:")
            print("-" * 50)

            for name, path in files_to_analyze:
                result = calculator.analyze_file(path)
                if 'error' not in result:
                    print(f"\n{name}:")
                    print(f"  Размер: {result['total_bytes']} байт")
                    print(f"  Уникальных символов: {result['unique_symbols']}")
                    print(f"  Энтропия: {result['entropy']:.6f} бит/символ")
                    print(f"  Относительная энтропия: {result['entropy_percent']:.2f}%")

        elif choice == '3':
            print("\nСравнение энтропии для разных типов данных:")
            print("-" * 40)

            sizes = [100, 1000, 10000, 100000]

            print(f"{'Тип данных':<30} {'Размер':<10} {'Энтропия':<12} {'Уник. символов'}")
            print("-" * 65)

            for size in sizes:
                test_data = bytes([65]) * size
                entropy = calculator.calculate_entropy(test_data)
                unique = len(set(test_data))
                print(f"{'Одинаковые символы':<30} {size:<10} {entropy:<12.6f} {unique}")

                test_data = bytes([random.choice([0, 1]) for _ in range(size)])
                entropy = calculator.calculate_entropy(test_data)
                unique = len(set(test_data))
                print(f"{'Случайные биты (0,1)':<30} {size:<10} {entropy:<12.6f} {unique}")

                test_data = bytes([random.randint(0, 255) for _ in range(size)])
                entropy = calculator.calculate_entropy(test_data)
                unique = len(set(test_data))
                print(f"{'Случайные байты (0-255)':<30} {size:<10} {entropy:<12.6f} {unique}")

                alphabet_size = 26
                alphabet = list(range(97, 97 + alphabet_size))
                test_data = bytes([random.choice(alphabet) for _ in range(size)])
                entropy = calculator.calculate_entropy(test_data)
                unique = len(set(test_data))
                max_entropy = math.log2(alphabet_size)
                print(f"{f'Случайные буквы (a-z, макс={max_entropy:.3f})':<30} {size:<10} {entropy:<12.6f} {unique}")

                print("-" * 65)

            print("\nТеоретические значения:")
            print(f"  Энтропия для 2 символов (биты): {math.log2(2):.6f} бит/символ")
            print(f"  Энтропия для 26 символов (буквы): {math.log2(26):.6f} бит/символ")
            print(f"  Энтропия для 256 символов (байты): {math.log2(256):.6f} бит/символ")

        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
