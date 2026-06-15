import struct
import os
from pathlib import Path


class TEA:
    """Tiny Encryption Algorithm - блочный шифр с блоком 64 бита (8 байт) и ключом 128 бит (16 байт)"""

    DELTA = 0x9E3779B9
    ROUNDS = 32

    @staticmethod
    def _encrypt_block(v, key):
        """Шифрование одного 64-битного блока"""
        v0, v1 = v
        k0, k1, k2, k3 = key
        s = 0

        for _ in range(TEA.ROUNDS):
            s = (s + TEA.DELTA) & 0xFFFFFFFF
            v0 = (v0 + (((v1 << 4) + k0) ^ (v1 + s) ^ ((v1 >> 5) + k1))) & 0xFFFFFFFF
            v1 = (v1 + (((v0 << 4) + k2) ^ (v0 + s) ^ ((v0 >> 5) + k3))) & 0xFFFFFFFF

        return (v0, v1)

    @staticmethod
    def _decrypt_block(v, key):
        """Расшифрование одного 64-битного блока"""
        v0, v1 = v
        k0, k1, k2, k3 = key
        s = (TEA.DELTA * TEA.ROUNDS) & 0xFFFFFFFF

        for _ in range(TEA.ROUNDS):
            v1 = (v1 - (((v0 << 4) + k2) ^ (v0 + s) ^ ((v0 >> 5) + k3))) & 0xFFFFFFFF
            v0 = (v0 - (((v1 << 4) + k0) ^ (v1 + s) ^ ((v1 >> 5) + k1))) & 0xFFFFFFFF
            s = (s - TEA.DELTA) & 0xFFFFFFFF

        return (v0, v1)

    @staticmethod
    def _prepare_key(key_bytes):
        """Преобразование ключа из 16 байт в 4 числа по 32 бита"""
        if len(key_bytes) < 16:
            key_bytes = key_bytes.ljust(16, b'\x00')
        elif len(key_bytes) > 16:
            key_bytes = key_bytes[:16]

        return struct.unpack('>4I', key_bytes)

    @staticmethod
    def encrypt_file(input_file, output_file, key_bytes):
        """Шифрование файла с добавлением паддинга PKCS7"""
        try:
            with open(input_file, 'rb') as f:
                data = f.read()

            key = TEA._prepare_key(key_bytes)

            pad_len = 8 - (len(data) % 8)
            if pad_len != 8:
                data += bytes([pad_len]) * pad_len
            else:
                data += bytes([8]) * 8

            encrypted = bytearray()

            for i in range(0, len(data), 8):
                block = data[i:i + 8]
                v0, v1 = struct.unpack('>2I', block)
                v0_enc, v1_enc = TEA._encrypt_block((v0, v1), key)
                encrypted.extend(struct.pack('>2I', v0_enc, v1_enc))

            with open(output_file, 'wb') as f:
                f.write(encrypted)

            print(f"Зашифровано: {input_file} -> {output_file}")
            return True

        except Exception as e:
            print(f"Ошибка: {e}")
            return False

    @staticmethod
    def decrypt_file(input_file, output_file, key_bytes):
        """Расшифрование файла с удалением паддинга PKCS7"""
        try:
            with open(input_file, 'rb') as f:
                data = f.read()

            if len(data) % 8 != 0:
                print("Ошибка: размер файла не кратен 8 байтам")
                return False

            key = TEA._prepare_key(key_bytes)

            decrypted = bytearray()

            for i in range(0, len(data), 8):
                block = data[i:i + 8]
                v0, v1 = struct.unpack('>2I', block)
                v0_dec, v1_dec = TEA._decrypt_block((v0, v1), key)
                decrypted.extend(struct.pack('>2I', v0_dec, v1_dec))

            pad_len = decrypted[-1]
            if 1 <= pad_len <= 8:
                if decrypted[-pad_len:] == bytes([pad_len]) * pad_len:
                    decrypted = decrypted[:-pad_len]

            with open(output_file, 'wb') as f:
                f.write(decrypted)

            print(f"Расшифровано: {input_file} -> {output_file}")
            return True

        except Exception as e:
            print(f"Ошибка: {e}")
            return False


class XTEA:
    """Улучшенная версия TEA с более сложной раундовой функцией"""

    DELTA = 0x9E3779B9
    ROUNDS = 32

    @staticmethod
    def _encrypt_block(v, key):
        v0, v1 = v
        k0, k1, k2, k3 = key
        s = 0

        for _ in range(XTEA.ROUNDS):
            v0 = (v0 + (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (s + k0)) & 0xFFFFFFFF
            s = (s + XTEA.DELTA) & 0xFFFFFFFF
            v1 = (v1 + (((v0 << 4) ^ (v0 >> 5)) + v0) ^ (s + k1)) & 0xFFFFFFFF

        return (v0, v1)

    @staticmethod
    def _decrypt_block(v, key):
        v0, v1 = v
        k0, k1, k2, k3 = key
        s = (XTEA.DELTA * XTEA.ROUNDS) & 0xFFFFFFFF

        for _ in range(XTEA.ROUNDS):
            v1 = (v1 - (((v0 << 4) ^ (v0 >> 5)) + v0) ^ (s + k1)) & 0xFFFFFFFF
            s = (s - XTEA.DELTA) & 0xFFFFFFFF
            v0 = (v0 - (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (s + k0)) & 0xFFFFFFFF

        return (v0, v1)

    @staticmethod
    def _prepare_key(key_bytes):
        if len(key_bytes) < 16:
            key_bytes = key_bytes.ljust(16, b'\x00')
        elif len(key_bytes) > 16:
            key_bytes = key_bytes[:16]
        return struct.unpack('>4I', key_bytes)

    @staticmethod
    def encrypt_file(input_file, output_file, key_bytes):
        try:
            with open(input_file, 'rb') as f:
                data = f.read()

            key = XTEA._prepare_key(key_bytes)

            pad_len = 8 - (len(data) % 8)
            if pad_len != 8:
                data += bytes([pad_len]) * pad_len
            else:
                data += bytes([8]) * 8

            encrypted = bytearray()

            for i in range(0, len(data), 8):
                block = data[i:i + 8]
                v0, v1 = struct.unpack('>2I', block)
                v0_enc, v1_enc = XTEA._encrypt_block((v0, v1), key)
                encrypted.extend(struct.pack('>2I', v0_enc, v1_enc))

            with open(output_file, 'wb') as f:
                f.write(encrypted)

            print(f"Зашифровано (XTEA): {input_file} -> {output_file}")
            return True
        except Exception as e:
            print(f"Ошибка: {e}")
            return False

    @staticmethod
    def decrypt_file(input_file, output_file, key_bytes):
        try:
            with open(input_file, 'rb') as f:
                data = f.read()

            if len(data) % 8 != 0:
                print("Ошибка: размер файла не кратен 8 байтам")
                return False

            key = XTEA._prepare_key(key_bytes)

            decrypted = bytearray()

            for i in range(0, len(data), 8):
                block = data[i:i + 8]
                v0, v1 = struct.unpack('>2I', block)
                v0_dec, v1_dec = XTEA._decrypt_block((v0, v1), key)
                decrypted.extend(struct.pack('>2I', v0_dec, v1_dec))

            pad_len = decrypted[-1]
            if 1 <= pad_len <= 8:
                if decrypted[-pad_len:] == bytes([pad_len]) * pad_len:
                    decrypted = decrypted[:-pad_len]

            with open(output_file, 'wb') as f:
                f.write(decrypted)

            print(f"Расшифровано (XTEA): {input_file} -> {output_file}")
            return True
        except Exception as e:
            print(f"Ошибка: {e}")
            return False


def create_test_file():
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)

    test_file = test_dir / "plaintext.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("Block cipher test message.\n")
        f.write("TEA is a lightweight block cipher.\n")
        f.write("It operates on 64-bit blocks with 128-bit key.\n")
        f.write("This is a longer text to demonstrate padding handling.\n")
        f.write("1234567890!@#$%^&*()_+ABCDEFGHIJKLMNOPQRSTUVWXYZ\n")

    print(f"Создан тестовый файл: {test_file}")
    return test_file


def main():
    print("БЛОЧНЫЕ ШИФРЫ (TEA и XTEA)")

    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)

    current_key = b'my_secret_key_16'

    while True:
        print("\nМЕНЮ:")
        print("1. Установить ключ шифрования")
        print("2. Зашифровать файл (TEA)")
        print("3. Расшифровать файл (TEA)")
        print("4. Зашифровать файл (XTEA)")
        print("5. Расшифровать файл (XTEA)")
        print("6. Создать тестовый файл")
        print("7. Показать текущий ключ")
        print("0. Выход")

        choice = input("\nВыберите действие: ").strip()

        if choice == '0':
            print("До свидания!")
            break

        elif choice == '1':
            key = input("Введите ключ (16 байт, можно строку): ").strip()
            current_key = key.encode('utf-8')
            print(f"Ключ установлен: {current_key[:16]}")

        elif choice == '2':
            input_file = input("Входной файл: ").strip()
            output_file = input("Выходной файл: ").strip()
            if not output_file:
                output_file = str(test_dir / "encrypted_tea.bin")
            TEA.encrypt_file(input_file, output_file, current_key)

        elif choice == '3':
            input_file = input("Входной файл (шифротекст): ").strip()
            output_file = input("Выходной файл: ").strip()
            if not output_file:
                output_file = str(test_dir / "decrypted_tea.txt")
            TEA.decrypt_file(input_file, output_file, current_key)

        elif choice == '4':
            input_file = input("Входной файл: ").strip()
            output_file = input("Выходной файл: ").strip()
            if not output_file:
                output_file = str(test_dir / "encrypted_xtea.bin")
            XTEA.encrypt_file(input_file, output_file, current_key)

        elif choice == '5':
            input_file = input("Входной файл (шифротекст): ").strip()
            output_file = input("Выходной файл: ").strip()
            if not output_file:
                output_file = str(test_dir / "decrypted_xtea.txt")
            XTEA.decrypt_file(input_file, output_file, current_key)

        elif choice == '6':
            create_test_file()

        elif choice == '7':
            print(f"Текущий ключ: {current_key[:16]}")

        else:
            print("Неверный выбор")


if __name__ == "__main__":
    main()
