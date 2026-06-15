import os
import random
import struct
from pathlib import Path


class LCG:
    """Линейный конгруэнтный генератор"""

    def __init__(self, seed=None):
        self.modulus = 2 ** 31 - 1
        self.multiplier = 1103515245
        self.increment = 12345
        self.state = seed if seed is not None else int.from_bytes(os.urandom(4), 'little')

    def next(self):
        self.state = (self.multiplier * self.state + self.increment) % self.modulus
        return self.state

    def next_byte(self):
        return self.next() & 0xFF

    def generate_key_file(self, filename, size_bytes):
        with open(filename, 'wb') as f:
            for _ in range(size_bytes):
                f.write(bytes([self.next_byte()]))
        print(f"Ключевой файл создан: {filename} (размер: {size_bytes} байт)")


class VernamCipher:
    """Шифр Вернама (XOR)"""

    @staticmethod
    def encrypt_decrypt(input_file, key_file, output_file):
        try:
            with open(input_file, 'rb') as f_in:
                plaintext = f_in.read()

            with open(key_file, 'rb') as f_key:
                key = f_key.read()

            if len(key) < len(plaintext):
                print(f"Ошибка: ключ короче текста ({len(key)} < {len(plaintext)})")
                return False

            ciphertext = bytes([p ^ k for p, k in zip(plaintext, key)])

            with open(output_file, 'wb') as f_out:
                f_out.write(ciphertext)

            print(f"Готово: {output_file}")
            return True

        except FileNotFoundError as e:
            print(f"Ошибка: файл не найден - {e}")
            return False
        except Exception as e:
            print(f"Ошибка: {e}")
            return False

    @staticmethod
    def encrypt(input_file, key_file, output_file):
        print(f"Зашифрование {input_file} с помощью ключа {key_file}")
        return VernamCipher.encrypt_decrypt(input_file, key_file, output_file)

    @staticmethod
    def decrypt(input_file, key_file, output_file):
        print(f"Расшифрование {input_file} с помощью ключа {key_file}")
        return VernamCipher.encrypt_decrypt(input_file, key_file, output_file)


class RC4:
    """Поточный шифр RC4"""

    def __init__(self, key):
        self.key = key if isinstance(key, bytes) else key.encode()
        self.S = list(range(256))
        self._ksa()

    def _ksa(self):
        j = 0
        for i in range(256):
            j = (j + self.S[i] + self.key[i % len(self.key)]) % 256
            self.S[i], self.S[j] = self.S[j], self.S[i]

    def _prga(self):
        i = 0
        j = 0
        while True:
            i = (i + 1) % 256
            j = (j + self.S[i]) % 256
            self.S[i], self.S[j] = self.S[j], self.S[i]
            yield self.S[(self.S[i] + self.S[j]) % 256]

    def encrypt_decrypt(self, data):
        result = bytearray()
        keystream = self._prga()
        for byte in data:
            result.append(byte ^ next(keystream))
        return bytes(result)

    def process_file(self, input_file, output_file):
        try:
            with open(input_file, 'rb') as f:
                data = f.read()

            processed = self.encrypt_decrypt(data)

            with open(output_file, 'wb') as f:
                f.write(processed)

            print(f"Готово: {output_file}")
            return True

        except Exception as e:
            print(f"Ошибка: {e}")
            return False

def main():
    print("ШИФР ВЕРНАМА И ПОТОЧНЫЙ ШИФР RC4")

    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)

    while True:
        print("\nМЕНЮ:")
        print("1. Сгенерировать ключ (LCG)")
        print("2. Зашифровать файл (Вернам)")
        print("3. Расшифровать файл (Вернам)")
        print("4. Зашифровать файл (RC4)")
        print("5. Расшифровать файл (RC4)")
        print("0. Выход")

        choice = input("\nВыберите действие: ").strip()

        if choice == '0':
            print("До свидания!")
            break

        elif choice == '1':
            filename = input("Имя файла для ключа: ").strip()
            if not filename:
                filename = str(test_dir / "key.bin")

            try:
                size = int(input("Размер ключа в байтах: "))
                seed = input("Seed (Enter для случайного): ").strip()

                lcg = LCG(seed=int(seed) if seed else None)
                lcg.generate_key_file(filename, size)
            except ValueError:
                print("Ошибка: введите корректное число")

        elif choice == '2':
            input_file = input("Входной файл (открытый текст): ").strip()
            key_file = input("Файл с ключом: ").strip()
            output_file = input("Выходной файл (шифротекст): ").strip()

            if not output_file:
                output_file = str(test_dir / "encrypted_vernam.bin")

            VernamCipher.encrypt(input_file, key_file, output_file)

        elif choice == '3':
            input_file = input("Входной файл (шифротекст): ").strip()
            key_file = input("Файл с ключом: ").strip()
            output_file = input("Выходной файл (расшифрованный текст): ").strip()

            if not output_file:
                output_file = str(test_dir / "decrypted_vernam.txt")

            VernamCipher.decrypt(input_file, key_file, output_file)

        elif choice == '4':
            input_file = input("Входной файл: ").strip()
            password = input("Пароль (ключ RC4): ").strip()
            output_file = input("Выходной файл: ").strip()

            if not output_file:
                output_file = str(test_dir / "encrypted_rc4.bin")

            rc4 = RC4(password)
            rc4.process_file(input_file, output_file)

        elif choice == '5':
            input_file = input("Входной файл: ").strip()
            password = input("Пароль (ключ RC4): ").strip()
            output_file = input("Выходной файл: ").strip()

            if not output_file:
                output_file = str(test_dir / "decrypted_rc4.txt")

            rc4 = RC4(password)
            rc4.process_file(input_file, output_file)

if __name__ == "__main__":
    main()
