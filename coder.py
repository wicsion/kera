from string import digits as DIGITS


# Константы для символов
OPEN_BRACKET = '['
CLOSE_BRACKET = ']'

# Набор цифр для проверки
DIGITS_SET = set(DIGITS)

def decode_string(encoded_string: str) -> str:
    """
    Декодирует строку, состоящую из чисел и строк, формируя повторяющиеся подстроки.

    :param encoded_string: Закодированная строка, содержащая числа и подстроки.
    :return: Декодированная строка.
    """
    stack: list[tuple[int, str]] = []  # Стек для хранения (количество, строка)
    current_num = 0  # Текущее число повторений
    current_string = ''  # Текущая строка

    for char in encoded_string:
        if char in DIGITS_SET:
            # Собираем цифры для многозначных чисел
            current_num = current_num * 10 + int(char)
        elif char == OPEN_BRACKET:
            # Сохраняем текущее число и строку в стек
            stack.append((current_num, current_string))
            current_num, current_string = 0, ''  # Сбрасываем текущее число и строку
        elif char == CLOSE_BRACKET:
            # Извлекаем из стека и создаем новую строку
            last_num, last_string = stack.pop()
            current_string = last_string + current_string * last_num
        else:
            # Добавляем текущий символ к строке
            current_string += char

    return current_string

if __name__ == '__main__':
    # Чтение входных данных
    input_string = input()

    # Вывод результата
    print(decode_string(input_string))
    #ID успешной посылки 130845887
