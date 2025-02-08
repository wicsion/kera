from random import randint, choice
import pygame as pg

# Константы для размеров экрана и сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Центр экрана
CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Настройка окна игры
pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Игра Змейка')
clock = pg.time.Clock()
SPEED = 10


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, body_color=BORDER_COLOR,
                 border_color=BOARD_BACKGROUND_COLOR):
        self.body_color = body_color
        self.border_color = border_color
        self.position = CENTER_POSITION

    def draw_cell(self, position):
        """Отрисовать одну ячейку."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, self.border_color, rect, 1)

    def draw(self):
        """Отрисовать игровой объект."""
        raise NotImplementedError('Метод draw должен '
                                  'быть реализован в дочерних классах.')


class Apple(GameObject):
    """Класс, представляющий яблоко."""

    def __init__(self, body_color=APPLE_COLOR, border_color=BORDER_COLOR,
                 occupied_positions=(CENTER_POSITION,)):
        super().__init__(body_color, border_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Случайно разместить яблоко на игровом поле."""
        while True:
            self.position = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                             randint(0, GRID_HEIGHT - 1) * GRID_SIZE)
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовать яблоко на экране."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс, представляющий змейку."""

    def __init__(self, body_color=SNAKE_COLOR, border_color=BORDER_COLOR):
        super().__init__(body_color, border_color)
        self.reset()  # Инициализация начального состояния
        self.direction = RIGHT  # Змейка начинает движение вправо

    def reset(self):
        """Сбросить состояние змейки к начальному значению."""
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.growing = False

    def get_head_position(self):
        """Получить позицию головы змейки."""
        return self.positions[0]

    def grow(self):
        """Увеличить змейку."""
        self.growing = True

    def update_direction(self):
        """Обновить направление змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Двигать змейку."""
        head_x, head_y = self.get_head_position()
        delta_x, delta_y = self.direction
        new_head = (
            (head_x + (delta_x * GRID_SIZE)) % SCREEN_WIDTH,
            (head_y + (delta_y * GRID_SIZE)) % SCREEN_HEIGHT,
        )

        self.positions.insert(0, new_head)
        if not self.growing:
            self.positions.pop()
        else:
            self.growing = False

    def draw(self):
        """Отрисовать змейку на экране."""
        for position in self.positions:
            self.draw_cell(position)


def handle_keys(snake):
    """Обработать нажатия клавиш."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and snake.direction != DOWN:
                snake.next_direction = UP
            elif event.key == pg.K_DOWN and snake.direction != UP:
                snake.next_direction = DOWN
            elif event.key == pg.K_LEFT and snake.direction != RIGHT:
                snake.next_direction = LEFT
            elif event.key == pg.K_RIGHT and snake.direction != LEFT:
                snake.next_direction = RIGHT


def main():
    """Основная функция игры."""
    apple = Apple()
    snake = Snake()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)

        snake.update_direction()
        snake.move()

        # Проверка столкновения с яблоком
        if snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position(snake.positions)

        # Проверка на столкновения с границами или телом
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)

        # Отрисовка объектов
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()

        pg.display.update()


if __name__ == '__main__':
    main()
