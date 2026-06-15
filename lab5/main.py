import struct
import random
import os
from collections import defaultdict


class TEAHash:
    """Криптографическая хеш-функция на базе блочного шифра TEA (режим Davies-Meyer)"""

    BLOCK_SIZE = 8
    HASH_SIZE = 8

    @staticmethod
    def _tea_encrypt(block, key):
        v0, v1 = block
        k0, k1, k2, k3 = key
        delta = 0x9E3779B9
        s = 0

        for _ in range(32):
            s = (s + delta) & 0xFFFFFFFF
            v0 = (v0 + (((v1 << 4) + k0) ^ (v1 + s) ^ ((v1 >> 5) + k1))) & 0xFFFFFFFF
            v1 = (v1 + (((v0 << 4) + k2) ^ (v0 + s) ^ ((v0 >> 5) + k3))) & 0xFFFFFFFF

        return (v0, v1)

    @staticmethod
    def _pad(message):
        original_len = len(message)
        pad_len = 8 - (original_len % 8)
        if pad_len == 8:
            pad_len = 0

        padded = message + bytes([0x80]) + b'\x00' * (pad_len - 1) if pad_len > 0 else message
        padded += struct.pack('>Q', original_len * 8)

        while len(padded) % 8 != 0:
            padded += b'\x00'

        return padded

    @staticmethod
    def hash(message):
        if isinstance(message, str):
            message = message.encode('utf-8')

        padded = TEAHash._pad(message)

        h = (0, 0)

        for i in range(0, len(padded), 8):
            block = padded[i:i + 8]
            m0, m1 = struct.unpack('>2I', block)

            h0_enc, h1_enc = TEAHash._tea_encrypt((h[0], h[1]), (m0, m1, m0, m1))

            h = (h[0] ^ h0_enc, h[1] ^ h1_enc)

        return struct.pack('>2I', h[0], h[1])

    @staticmethod
    def hexdigest(message):
        return TEAHash.hash(message).hex()

    @staticmethod
    def hash_file(filepath):
        with open(filepath, 'rb') as f:
            data = f.read()
        return TEAHash.hash(data)


def random_bytes(n):
    """Генерация случайных байт для старых версий Python"""
    return bytes([random.randint(0, 255) for _ in range(n)])


class PartialCollisionFinder:
    """Поиск частичных коллизий хеш-функции"""

    @staticmethod
    def find_collision_bytes(target_bytes=2, max_attempts=100000):
        print(f"Поиск коллизии по первым {target_bytes} байтам")
        print(f"Максимум попыток: {max_attempts}")

        seen = {}
        attempts = 0

        while attempts < max_attempts:
            data = random_bytes(random.randint(1, 100))
            hash_value = TEAHash.hash(data)
            prefix = hash_value[:target_bytes]

            if prefix in seen:
                if seen[prefix] != data:
                    print(f"\nКоллизия найдена через {attempts + 1} попыток!")
                    print(f"Сообщение 1: {seen[prefix][:50]}...")
                    print(f"Хеш 1: {TEAHash.hexdigest(seen[prefix])}")
                    print(f"\nСообщение 2: {data[:50]}...")
                    print(f"Хеш 2: {TEAHash.hexdigest(data)}")
                    print(f"\nСовпадает {target_bytes} байт: {prefix.hex()}")
                    return True
            else:
                seen[prefix] = data

            attempts += 1
            if attempts % 10000 == 0:
                print(f"Попыток: {attempts}, уникальных префиксов: {len(seen)}")

        print(f"Коллизия не найдена за {max_attempts} попыток")
        return False

    @staticmethod
    def find_collision_bits(target_bits=16, max_attempts=100000):
        target_bytes = (target_bits + 7) // 8
        mask_bits = target_bits % 8
        mask_byte = (1 << mask_bits) - 1 if mask_bits > 0 else 0

        print(f"Поиск коллизии по первым {target_bits} битам")

        seen = {}
        attempts = 0

        while attempts < max_attempts:
            data = random_bytes(random.randint(1, 50))
            hash_value = TEAHash.hash(data)

            prefix = hash_value[:target_bytes]
            key = prefix

            if mask_bits > 0 and prefix:
                last_byte = (prefix[-1] & mask_byte)
                key = prefix[:-1] + bytes([last_byte])

            if key in seen:
                if seen[key] != data:
                    print(f"\nКоллизия по {target_bits} битам найдена!")
                    print(f"Сообщение 1: {seen[key][:50]}...")
                    print(f"Хеш 1: {TEAHash.hexdigest(seen[key])}")
                    print(f"\nСообщение 2: {data[:50]}...")
                    print(f"Хеш 2: {TEAHash.hexdigest(data)}")
                    return True
            else:
                seen[key] = data

            attempts += 1

        print(f"Коллизия не найдена за {max_attempts} попыток")
        return False


class BirthdayParadoxDemo:
    """Демонстрация парадокса дней рождения на хеш-функции"""

    @staticmethod
    def probability_collision(n, hash_bits):
        m = 2 ** hash_bits
        p = 1 - ((m - 1) / m) ** (n * (n - 1) / 2)
        return p

    @staticmethod
    def find_collision_by_birthday(bits, max_samples=20000):
        hash_bytes = (bits + 7) // 8
        seen = {}
        samples = 0

        print(f"Парадокс дней рождения: поиск коллизии для {bits}-битного хеша")
        print(f"Ожидаемое количество попыток: ~{int(2 ** (bits / 2))}")

        while samples < max_samples:
            data = random_bytes(random.randint(1, 30))
            full_hash = TEAHash.hash(data)
            short_hash = full_hash[:hash_bytes]

            if short_hash in seen:
                if seen[short_hash] != data:
                    print(f"\nКоллизия найдена через {samples + 1} попыток!")
                    print(f"Хеш (первые {bits} бит): {short_hash.hex()}")
                    print(f"Сообщение 1: {seen[short_hash][:40]}")
                    print(f"Сообщение 2: {data[:40]}")
                    return samples + 1
            else:
                seen[short_hash] = data

            samples += 1

        print(f"Коллизия не найдена за {max_samples} попыток")
        return None

    @staticmethod
    def run_demo():
        print("\n" + "=" * 60)
        print("ДЕМОНСТРАЦИЯ ПАРАДОКСА ДНЕЙ РОЖДЕНИЯ")
        print("=" * 60)

        for bits in [8, 12, 16, 20]:
            print(f"\n{bits}-битный хеш (алфавит из {2 ** bits} значений)")
            print(
                f"Теоретическая вероятность коллизии для 100 попыток: {BirthdayParadoxDemo.probability_collision(100, bits):.4f}")
            print(f"Ожидаемое число попыток: ~{int(2 ** (bits / 2))}")

            attempts = BirthdayParadoxDemo.find_collision_by_birthday(bits, max_samples=5000)
            if attempts:
                print(f"Реально получено за {attempts} попыток")
            print("-" * 40)


class PasswordAuthSystem:
    """Система авторизации с хранением хешей паролей"""

    def __init__(self):
        self.users = {}

    def register(self, username, password):
        if username in self.users:
            print(f"Пользователь {username} уже существует")
            return False

        salt = random_bytes(8)
        hash_value = TEAHash.hash(salt + password.encode())
        self.users[username] = (salt, hash_value)
        print(f"Пользователь {username} зарегистрирован")
        return True

    def login(self, username, password):
        if username not in self.users:
            print(f"Пользователь {username} не найден")
            return False

        salt, stored_hash = self.users[username]
        test_hash = TEAHash.hash(salt + password.encode())

        if test_hash == stored_hash:
            print(f"Добро пожаловать, {username}!")
            return True
        else:
            print("Неверный пароль")
            return False

    def list_users(self):
        if not self.users:
            print("Нет зарегистрированных пользователей")
        else:
            for username, (salt, hash_val) in self.users.items():
                print(f"{username}: {hash_val.hex()[:16]}...")


def main():
    print("КРИПТОГРАФИЧЕСКАЯ ХЕШ-ФУНКЦИЯ (TEA-Davies-Meyer)")

    auth_system = PasswordAuthSystem()

    while True:
        print("\nМЕНЮ:")
        print("1. Вычислить хеш сообщения")
        print("2. Вычислить хеш файла")
        print("3. Поиск частичных коллизий")
        print("4. Демонстрация парадокса дней рождения")
        print("5. Система авторизации (регистрация)")
        print("6. Система авторизации (вход)")
        print("7. Показать зарегистрированных пользователей")
        print("0. Выход")

        choice = input("\nВыберите действие: ").strip()

        if choice == '0':
            print("До свидания!")
            break

        elif choice == '1':
            message = input("Введите сообщение: ")
            hash_value = TEAHash.hexdigest(message)
            print(f"Хеш: {hash_value}")

        elif choice == '2':
            filepath = input("Введите путь к файлу: ")
            try:
                hash_value = TEAHash.hash_file(filepath).hex()
                print(f"Хеш файла: {hash_value}")
            except FileNotFoundError:
                print("Файл не найден")

        elif choice == '3':
            print("\nВарианты:")
            print("1. Поиск коллизии по N байтам")
            print("2. Поиск коллизии по N битам")
            subchoice = input("Выберите: ")

            if subchoice == '1':
                try:
                    n = int(input("Сколько байт должны совпадать? "))
                    PartialCollisionFinder.find_collision_bytes(n)
                except ValueError:
                    print("Ошибка ввода")

            elif subchoice == '2':
                try:
                    n = int(input("Сколько бит должны совпадать? "))
                    PartialCollisionFinder.find_collision_bits(n)
                except ValueError:
                    print("Ошибка ввода")

        elif choice == '4':
            BirthdayParadoxDemo.run_demo()

        elif choice == '5':
            username = input("Имя пользователя: ")
            password = input("Пароль: ")
            auth_system.register(username, password)

        elif choice == '6':
            username = input("Имя пользователя: ")
            password = input("Пароль: ")
            auth_system.login(username, password)

        elif choice == '7':
            auth_system.list_users()

        else:
            print("Неверный выбор")


if __name__ == "__main__":
    main()
