"""
Константы и настройки игры
"""

import pygame

# Константы игры
GAME_NAME = "Дуэлянты - Арена Силуэтов"
VERSION = "1.0.0"
FPS = 60

# Константы экрана
DEFAULT_SCREEN_WIDTH = 1024
DEFAULT_SCREEN_HEIGHT = 768

# Доступные разрешения
AVAILABLE_RESOLUTIONS = [
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
    (2560, 1440)
]

# Константы персонажей
DEFAULT_HEALTH = 100
DEFAULT_SPEED = 5.0
DEFAULT_DAMAGE = 10

# Константы анимации
ATTACK_ANIMATION_DURATION = 15
BLOCK_ANIMATION_DURATION = 40
HIT_EFFECT_DURATION = 15

# Константы физики
GRAVITY = 0.5
GROUND_FRICTION = 0.8

# Константы цвета
BACKGROUND_COLOR = (20, 25, 30)
TEXT_COLOR = (230, 235, 240)
HIGHLIGHT_COLOR = (210, 90, 90)
GROUND_COLOR = (45, 50, 55)
INFO_COLOR = (90, 160, 240)
ARENA_COLOR = (30, 35, 40)

# Константы управления
CONTROLS = {
    'player1': {
        'move_left': [pygame.K_a, pygame.K_LEFT],
        'move_right': [pygame.K_d, pygame.K_RIGHT],
        'attack': [pygame.K_LALT],
        'block': [pygame.K_w, pygame.K_UP]
    },
    'player2': {
        'move_left': [pygame.K_LEFT],
        'move_right': [pygame.K_RIGHT],
        'attack': [pygame.K_RALT],
        'block': [pygame.K_UP]
    }
}

# Константы пути (если используются ресурсы)
try:
    # Для совместимости с разными ОС
    import os
    if getattr(sys, 'frozen', False):
        # Если запущено как исполняемый файл
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        # Если запущено как скрипт
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
    FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
    IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
    SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

except ImportError:
    # Если что-то пошло не так
    BASE_DIR = "."
    ASSETS_DIR = "assets"
    FONTS_DIR = "assets/fonts"
    IMAGES_DIR = "assets/images"
    SOUNDS_DIR = "assets/sounds"

# Сообщения и текст
MENU_ITEMS = [
    "БОЙ С БОТОМ",
    "ИГРОК ПРОТИВ ИГРОКА",
    "ПРАВИЛА И УПРАВЛЕНИЕ",
    "НАСТРОЙКИ",
    "ВЫХОД"
]

SETTINGS_ITEMS = [
    "Оконный режим",
    "Оконный без рамки",
    "Полноэкранный"
]

BODY_TYPE_NAMES = {
    'ATHLETIC': "АТЛЕТ",
    'LEAN': "ПРОВОРНЫЙ",
    'HEAVY': "ТЯЖЕЛОВЕС",
    'SUMO': "СУМОИСТ",
    'NINJA': "НИНДЗЯ",
    'ROBOTIC': "КИБОРГ"
}

BODY_TYPE_DESCRIPTIONS = {
    'ATHLETIC': "Сбалансированные характеристики",
    'LEAN': "Быстрый но хрупкий",
    'HEAVY': "Медленный но выносливый",
    'SUMO': "Очень выносливый, очень медленный",
    'NINJA': "Очень быстрый, мало здоровья",
    'ROBOTIC': "Хороший баланс с технологиями"
}