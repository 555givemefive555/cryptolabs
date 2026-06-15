import sys


def fast_pow_mod(base, exponent, modulus):
    print(f"\nВходные параметры:")
    print(f"  a = {base}, e = {exponent}, m = {modulus}")
    print(f"  e в двоичном виде: {bin(exponent)[2:]}")
    print(f"  Вес Хэмминга e: {bin(exponent).count('1')}")

    result = 1
    a = base % modulus
    e = exponent

    print(f"\nНачало: result = {result}, a = {a}")

    multiplication_count = 0
    step = 1

    while e > 0:
        print(f"\nШаг {step}: e = {e} (двоич: {bin(e)[2:]})")

        if e & 1:
            print(f"  бит = 1 -> result = {result} * {a} = {(result * a) % modulus}")
            result = (result * a) % modulus
            multiplication_count += 1
        else:
            print(f"  бит = 0 -> пропуск умножения")

        print(f"  a = {a}^2 = {(a * a) % modulus}")
        a = (a * a) % modulus
        multiplication_count += 1
        print(f"  умножений сейчас: {multiplication_count}")

        e = e >> 1
        step += 1

    print(f"\nРезультат: {base}^{exponent} mod {modulus} = {result}")
    print(f"Всего умножений: {multiplication_count}")

    return result, multiplication_count


def check_with_pow(base, exponent, modulus, result):
    expected = pow(base, exponent, modulus)
    if result == expected:
        print(f"Проверка: верно")
    else:
        print(f"Проверка: ошибка (должно быть {expected})")


def analyze_hamming_weight():
    print("\nАНАЛИЗ ЗАВИСИМОСТИ ОТ ВЕСА ХЭММИНГА\n")

    base = 7
    modulus = 1000000007

    exponents = [
        (0b1111111111, "10 единиц подряд"),
        (0b1010101010, "чередующиеся биты"),
        (0b1000000001, "единицы на концах"),
        (0b1000000000, "степень двойки"),
        (0b11111111111111111111, "20 единиц подряд"),
        (0b10101010101010101010, "чередующиеся 20 бит"),
    ]

    print(f"{'Показатель':<35} {'Вес Хэмминга':<15} {'Умножений'}")
    print("-" * 65)

    for exp, desc in exponents:
        result, mult_count = fast_pow_mod(base, exp, modulus)
        hamming = bin(exp).count('1')
        print(f"{desc[:33]:<35} {hamming:<15} {mult_count}")


def interactive_mode():
    print("БЫСТРОЕ ВОЗВЕДЕНИЕ В СТЕПЕНЬ ПО МОДУЛЮ")

    while True:
        print("\nМЕНЮ:")
        print("1. Вычислить a^e mod m")
        print("2. Анализ веса Хэмминга")
        print("0. Выход")

        choice = input("\nВыберите действие: ")

        if choice == '0':
            print("До свидания!")
            break

        elif choice == '1':
            try:
                base = int(input("a: "))
                exponent = int(input("e: "))
                modulus = int(input("m: "))

                result, count = fast_pow_mod(base, exponent, modulus)
                check_with_pow(base, exponent, modulus, result)

            except ValueError:
                print("Ошибка ввода")

        elif choice == '2':
            analyze_hamming_weight()

        else:
            print("Неверный выбор")


if __name__ == "__main__":
    interactive_mode()
