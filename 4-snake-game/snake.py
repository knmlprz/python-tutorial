import random

import pygame
from pygame.locals import K_DOWN, K_ESCAPE, K_LEFT, K_RIGHT, K_UP, KEYDOWN

# Game settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SEGMENT_SIZE = 25
BACKGROUND_COLOR = (0, 0, 0)
INITIAL_SNAKE_LENGTH = 10
FRAMES_PER_SECOND = 60
INITIAL_FRAMES_PER_MOVE = 10
ACCELERATION = 0.25
DIRECTIONS = ["up", "left", "right", "down"]

# Pygame module configuration
pygame.init()
screen = pygame.display.set_mode(size=(SCREEN_WIDTH, SCREEN_HEIGHT), vsync=1)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)

# Loading images
images = []
for image_path in [
    "images/head.png",
    "images/forward.png",
    "images/right.png",
    "images/left.png",
    "images/tail.png",
    "images/apple.png",
]:
    img = pygame.image.load(image_path).convert()
    img.set_colorkey((255, 255, 255))
    images.append(img)
img_head, img_forward, img_right, img_left, img_tail, img_apple = images


class Movements:
    """This class is responsible for all possible movements in game."""

    directions = {
        "up": (0, -SEGMENT_SIZE),
        "down": (0, SEGMENT_SIZE),
        "left": (-SEGMENT_SIZE, 0),
        "right": (SEGMENT_SIZE, 0),
    }
    degrees = {"up": 0, "left": 90, "down": 180, "right": 270}
    turn_skins = {
        270: img_right,
        -90: img_right,
        90: img_left,
        -270: img_left,
        0: img_forward,
        180: img_forward,
        -180: img_forward,
        360: img_forward,
    }

    def turn(self, from_direction: str, to_direction: str):
        return self.degrees.get(to_direction) - self.degrees.get(from_direction)

    def to(self, direction: str):
        return self.directions.get(direction)

    def opposite_to(self, direction: str):
        direction_id = DIRECTIONS.index(direction) + 1
        opposite_direction = DIRECTIONS[-direction_id]
        return self.directions.get(opposite_direction)


class SnakeBodySection(pygame.sprite.Sprite):
    """Base class of snake's body section"""

    direction: str
    previous_direction: str

    def __init__(self, *groups: pygame.sprite.AbstractGroup):
        super().__init__(*groups)
        self.surface = pygame.Surface(
            size=(SEGMENT_SIZE, SEGMENT_SIZE), flags=pygame.SRCALPHA
        )
        self.is_tail = True


class SnakeHead(SnakeBodySection):
    def __init__(self, *groups: pygame.sprite.AbstractGroup):
        super().__init__(*groups)
        self.direction = self.previous_direction = self.next_direction = DIRECTIONS[
            random.randint(0, 3)
        ]
        self.surface.blit(img_head, (0, 0))
        self.surface = pygame.transform.rotate(
            self.surface, Movements().turn("up", self.direction)
        )
        width_positions = SCREEN_WIDTH // SEGMENT_SIZE
        height_positions = SCREEN_HEIGHT // SEGMENT_SIZE
        self.rect = self.surface.get_rect()
        self.rect.move_ip(
            random.randint(width_positions // 4, width_positions - width_positions // 4)
            * SEGMENT_SIZE,
            random.randint(
                height_positions // 4, height_positions - height_positions // 4
            )
            * SEGMENT_SIZE,
        )

    def update_direction(self, pressed_keys):
        if pressed_keys[K_UP] and not self.direction == "down":
            self.next_direction = "up"
        elif pressed_keys[K_DOWN] and not self.direction == "up":
            self.next_direction = "down"
        elif pressed_keys[K_LEFT] and not self.direction == "right":
            self.next_direction = "left"
        elif pressed_keys[K_RIGHT] and not self.direction == "left":
            self.next_direction = "right"

    def update(self, *args, **kwargs):
        self.previous_direction = self.direction
        self.direction = self.next_direction
        self.surface = pygame.transform.rotate(
            self.surface, Movements().turn(self.previous_direction, self.next_direction)
        )
        self.rect.move_ip(Movements().to(self.direction))


class SnakeTail(SnakeBodySection):
    def __init__(
        self, previous_segment: SnakeBodySection, *groups: pygame.sprite.AbstractGroup
    ):
        super().__init__(*groups)
        self.previous_segment = previous_segment
        self.previous_segment.is_tail = False
        self.direction = self.previous_direction = self.previous_segment.direction
        self.surface.blit(img_tail, (0, 0))
        self.surface = pygame.transform.rotate(
            self.surface, Movements().turn("up", self.direction)
        )
        self.rect = self.previous_segment.rect.move(
            Movements().opposite_to(self.direction)
        )

    def update(self, *args, **kwargs):
        self.previous_direction = self.direction
        self.direction = self.previous_segment.previous_direction
        self.rect.move_ip(Movements().to(self.direction))

        if self.is_tail:
            self.surface.blit(img_tail, (0, 0))
            self.surface = pygame.transform.rotate(
                self.surface, Movements().turn("up", self.previous_segment.direction)
            )
        else:
            degrees = Movements().turn(self.direction, self.previous_segment.direction)
            self.surface.blit(Movements().turn_skins.get(degrees), (0, 0))
            self.surface = pygame.transform.rotate(
                self.surface, Movements().turn("up", self.direction)
            )


class Food(pygame.sprite.Sprite):
    def __init__(
        self, snake: pygame.sprite.AbstractGroup, *groups: pygame.sprite.AbstractGroup
    ):
        super().__init__(*groups)
        self.snake = snake
        self.surface = pygame.Surface(
            size=(SEGMENT_SIZE, SEGMENT_SIZE), flags=pygame.SRCALPHA
        )
        self.surface.blit(img_apple, (0, 0))
        self.update()

    def update(self, *args, **kwargs):
        while True:
            self.rect = self.surface.get_rect(
                left=random.randint(0, SCREEN_WIDTH // SEGMENT_SIZE - 1) * SEGMENT_SIZE,
                top=random.randint(0, SCREEN_HEIGHT // SEGMENT_SIZE - 1) * SEGMENT_SIZE,
            )
            if not pygame.sprite.spritecollideany(self, self.snake):
                break


class ScoreCounter(pygame.sprite.Sprite):
    def __init__(self, *groups: pygame.sprite.AbstractGroup):
        super().__init__(*groups)
        self.score_counter = INITIAL_SNAKE_LENGTH
        self.surface = font.render(str(self.score_counter), False, (255, 255, 255))
        self.rect = self.surface.get_rect(right=SCREEN_WIDTH)

    def update(self, *args, **kwargs):
        self.surface = font.render(str(self.score_counter), False, (255, 255, 255))
        self.rect = self.surface.get_rect(right=SCREEN_WIDTH)


all_sprites = pygame.sprite.Group()
snake_tail = pygame.sprite.Group()
snake_body = pygame.sprite.Group()
food_group = pygame.sprite.Group()

new_snake_segment = head = SnakeHead(snake_body, all_sprites)
for i in range(INITIAL_SNAKE_LENGTH - 1):
    new_snake_segment = SnakeTail(
        new_snake_segment, snake_tail, snake_body, all_sprites
    )
food = Food(snake_body, food_group, all_sprites)
score = ScoreCounter(all_sprites)

game_is_running = True
frames_counter = 0
frames_per_move = INITIAL_FRAMES_PER_MOVE
while game_is_running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_is_running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                game_is_running = False

    head.update_direction(pygame.key.get_pressed())

    if frames_counter % frames_per_move < 1:
        head.update()

        if pygame.sprite.spritecollideany(head, food_group):
            new_snake_segment = SnakeTail(
                new_snake_segment, snake_tail, snake_body, all_sprites
            )
            score.score_counter += 1
            score.update()
            food.update()
            frames_per_move -= ACCELERATION

        snake_tail.update()

        if pygame.sprite.spritecollideany(head, snake_tail):
            game_is_running = False
        if any(
            (
                head.rect.top < 0,
                head.rect.left < 0,
                head.rect.bottom > SCREEN_HEIGHT,
                head.rect.right > SCREEN_WIDTH,
            )
        ):
            game_is_running = False

        screen.fill(BACKGROUND_COLOR)
        for entity in all_sprites:
            screen.blit(entity.surface, entity.rect)
        pygame.display.flip()

    frames_counter += 1
    clock.tick(FRAMES_PER_SECOND)

pygame.quit()

# IDEAS:
#  - (EASY)     shift for spead up, ctrl for slow down
#  - (MEDIUM)   loose screen with "play again" button
#  - (MEDIUM)   food as boosters and penetrations (bomb, speed-up, slow-down, freeze, etc.)
#  - (HARD)     AI powered snake
