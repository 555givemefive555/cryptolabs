import sys
import re
from pathlib import Path


class CaesarCipher:
    ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
    ALPHABET_LEN = 26

    @staticmethod
    def encrypt(plaintext: str, key: int) -> str:
        key = key % CaesarCipher.ALPHABET_LEN
        result = []

        for char in plaintext:
            if char.isalpha():
                is_upper = char.isupper()
                lower_char = char.lower()
                idx = (CaesarCipher.ALPHABET.index(lower_char) + key) % CaesarCipher.ALPHABET_LEN
                new_char = CaesarCipher.ALPHABET[idx]
                result.append(new_char.upper() if is_upper else new_char)
            else:
                result.append(char)

        return ''.join(result)

    @staticmethod
    def decrypt(ciphertext: str, key: int) -> str:
        return CaesarCipher.encrypt(ciphertext, -key)

    @staticmethod
    def find_key(plaintext: str, ciphertext: str):
        plain_letters = [c.lower() for c in plaintext if c.isalpha()]
        cipher_letters = [c.lower() for c in ciphertext if c.isalpha()]

        if not plain_letters or not cipher_letters:
            return None

        p = plain_letters[0]
        c = cipher_letters[0]

        key = (CaesarCipher.ALPHABET.index(c) - CaesarCipher.ALPHABET.index(p)) % CaesarCipher.ALPHABET_LEN

        for p_char, c_char in zip(plain_letters[:10], cipher_letters[:10]):
            calc_key = (CaesarCipher.ALPHABET.index(c_char) - CaesarCipher.ALPHABET.index(
                p_char)) % CaesarCipher.ALPHABET_LEN
            if calc_key != key:
                return None

        return key


class DictionaryAttack:
    COMMON_WORDS = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'any', 'can',
        'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him',
        'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who',
        'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use', 'that',
        'this', 'from', 'have', 'with', 'what', 'your', 'about', 'after',
        'again', 'always', 'another', 'because', 'before', 'between', 'could',
        'every', 'first', 'found', 'friend', 'good', 'great', 'house', 'little',
        'long', 'made', 'make', 'many', 'more', 'much', 'never', 'night', 'only',
        'other', 'over', 'right', 'should', 'small', 'something', 'sound', 'still',
        'such', 'than', 'their', 'them', 'there', 'these', 'they', 'thing',
        'think', 'those', 'through', 'time', 'under', 'very', 'want', 'well',
        'went', 'where', 'which', 'while', 'will', 'with', 'word', 'work', 'world',
        'would', 'year', 'back', 'down', 'into', 'just', 'know', 'like', 'more',
        'most', 'name', 'need', 'never', 'only', 'other', 'people', 'place'
    }

    def __init__(self, dictionary_path: str = None):
        self.words = set(self.COMMON_WORDS)

        if dictionary_path and Path(dictionary_path).exists():
            self._load_dictionary(dictionary_path)

    def _load_dictionary(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().lower()
                    if word and len(word) >= 3:
                        self.words.add(word)
            print(f"Загружено {len(self.words)} слов из словаря.")
        except Exception as e:
            print(f"Ошибка загрузки словаря: {e}")

    def is_meaningful(self, text: str, min_word_length: int = 3, min_match_ratio: float = 0.3):
        words = re.findall(r'[a-zA-Z]+', text.lower())
        words = [w for w in words if len(w) >= min_word_length]

        if not words:
            return False, 0, 0

        matches = sum(1 for w in words if w in self.words)
        ratio = matches / len(words)

        return ratio >= min_match_ratio, matches, len(words)

    def attack(self, ciphertext: str):
        results = []

        print("\n" + "=" * 60)
        print("ПЕРЕБОР ВСЕХ КЛЮЧЕЙ (0-25):")
        print("=" * 60)

        for key in range(26):
            decrypted = CaesarCipher.decrypt(ciphertext, key)
            is_good, matches, total = self.is_meaningful(decrypted)

            marker = " " if is_good else ""
            print(f"Ключ {key:2d}: \"{decrypted[:60]}{'...' if len(decrypted) > 60 else ''}\" {marker}")

            results.append({
                'key': key,
                'decrypted': decrypted,
                'matches': matches,
                'total_words': total,
                'is_meaningful': is_good
            })

        results.sort(key=lambda x: (x['is_meaningful'], x['matches']), reverse=True)

        return results


def main():
    print("=" * 60)
    print("ШИФР ЦЕЗАРЯ - АТАКИ ПО ИЗВЕСТНОМУ ТЕКСТУ И ШИФРОТЕКСТУ")
    print("=" * 60)

    cipher = CaesarCipher()

    while True:
        print("\n" + "-" * 40)
        print("МЕНЮ:")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст (известен ключ)")
        print("3. Атака по известному открытому тексту (найти ключ)")
        print("4. Атака по шифротексту (перебор всех ключей)")
        print("5. Атака по шифротексту + автоопределение ключа (со словарём)")
        print("0. Выход")

        choice = input("\nВыберите действие: ").strip()

        if choice == '0':
            print("До свидания!")
            break

        elif choice == '1':
            text = input("Введите открытый текст: ")
            try:
                key = int(input("Введите ключ (0-25): "))
                if 0 <= key <= 25:
                    encrypted = cipher.encrypt(text, key)
                    print(f"\nЗашифрованный текст: {encrypted}")
                else:
                    print("Ошибка: ключ должен быть от 0 до 25!")
            except ValueError:
                print("Ошибка: ключ должен быть числом!")

        elif choice == '2':
            text = input("Введите зашифрованный текст: ")
            try:
                key = int(input("Введите ключ (0-25): "))
                if 0 <= key <= 25:
                    decrypted = cipher.decrypt(text, key)
                    print(f"\nРасшифрованный текст: {decrypted}")
                else:
                    print("Ошибка: ключ должен быть от 0 до 25!")
            except ValueError:
                print("Ошибка: ключ должен быть числом!")

        elif choice == '3':
            plaintext = input("Введите открытый текст: ")
            ciphertext = input("Введите зашифрованный текст: ")

            key = cipher.find_key(plaintext, ciphertext)
            if key is not None:
                print(f"\n Найден ключ: {key}")
                test_encrypt = cipher.encrypt(plaintext, key)
                print(f"Проверка: encrypt(plain) = {test_encrypt[:50]}")
            else:
                print("\n Не удалось определить ключ. Проверьте, что тексты соответствуют друг другу.")

        elif choice == '4':
            ciphertext = input("Введите зашифрованный текст: ")

            print("ПЕРЕБОР ВСЕХ КЛЮЧЕЙ (0-25):")

            for key in range(26):
                decrypted = cipher.decrypt(ciphertext, key)
                print(f"Ключ {key:2d}: {decrypted}")

            print("\nПросмотрите результаты и найдите осмысленный текст.")

        elif choice == '5':
            ciphertext = input("Введите зашифрованный текст: ")

            dict_path = input("Введите путь к файлу словаря: ").strip()

            attacker = DictionaryAttack(dict_path if dict_path else None)
            results = attacker.attack(ciphertext)

            print("РЕЗУЛЬТАТЫ АТАКИ (от лучших к худшим):")

            found = False
            for i, res in enumerate(results[:5]):
                print(f"\n Вариант {i + 1} (ключ = {res['key']}) ")
                print(f"Совпадений со словарём: {res['matches']}/{res['total_words']}")
                print(f"Текст: {res['decrypted']}")
                if res['is_meaningful'] and not found:
                    found = True
                    print(f" ПРЕДПОЛАГАЕМЫЙ КЛЮЧ: {res['key']} ")

            if not found:
                print(
                    "\n Не найдено явно осмысленных текстов.")

        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
