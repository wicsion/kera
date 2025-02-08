def min_transport_platforms(weights: list[int], limit: int) -> int:
    """
    Вычисляет минимальное количество транспортных платформ, необходимых для перевозки роботов с заданными весами.

    :param weights: Список весов роботов.
    :param limit: Максимальный вес, который может быть перевезен на одной платформе.
    :return: Минимальное количество платформ, необходимых для перевозки всех роботов.
    """
    sorted_weights = sorted(weights)  # Сортируем массив весов без мутации исходных данных
    left, right, platforms = 0, len(sorted_weights) - 1, 0  # Указатели и счетчик платформ

    while left <= right:
        if sorted_weights[left] + sorted_weights[right] <= limit:
            left += 1  # Перевозим легкого робота
        right -= 1  # Перевозим тяжелого робота
        platforms += 1  # Платформа используется

    return platforms

def main() -> None:
    input_weights: str = input().strip()
    limit: int = int(input().strip())

    # Преобразование массива строк в массив целых чисел с использованием list comprehension
    weights: list[int] = [int(weight) for weight in input_weights.split()]

    # Вывод результата сразу в print
    print(min_transport_platforms(weights, limit))


if __name__ == "__main__":
    main()

# ID успешной посылки: 130729405



