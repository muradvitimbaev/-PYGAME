"""
Duelist Game - 2D fighting game with bot and player vs player modes
Main game module
"""

import pygame
import sys
import random
from enum import Enum
from typing import Tuple, Optional, List

# Инициализация Pygame
pygame.init()
pygame.font.init()

class GameState(Enum):
    """Состояния игры"""
    MENU = "menu"
    CHARACTER_SELECT_P1 = "character_select_p1"  # Выбор персонажа для игрока 1
    CHARACTER_SELECT_P2 = "character_select_p2"  # Выбор персонажа для игрока 2
    PLAYER_VS_PLAYER = "player_vs_player"
    PLAYER_VS_BOT = "player_vs_bot"
    SETTINGS = "settings"
    CONTROLS = "controls"
    EXIT = "exit"

class BodyType(Enum):
    """Типы телосложения персонажей"""
    ATHLETIC = "athletic"     # Атлетическое (мускулистое)
    LEAN = "lean"             # Худощавое
    HEAVY = "heavy"           # Тяжелое (крупное)
    SUMO = "sumo"             # Сумоист
    NINJA = "ninja"           # Ниндзя (гибкое)
    ROBOTIC = "robotic"       # Роботизированное

class ColorPalette:
    """Цветовые палитры для персонажей"""
    PALETTES = {
        "default": {
            "body": (30, 30, 40),
            "highlight": (60, 60, 80),
            "attack": (220, 60, 60),
            "block": (60, 120, 220),
        },
        "red": {
            "body": (50, 20, 25),
            "highlight": (80, 40, 45),
            "attack": (240, 80, 80),
            "block": (80, 160, 240),
        },
        "blue": {
            "body": (20, 30, 50),
            "highlight": (40, 60, 90),
            "attack": (240, 100, 60),
            "block": (100, 180, 250),
        },
        "green": {
            "body": (25, 40, 25),
            "highlight": (45, 70, 45),
            "attack": (230, 80, 80),
            "block": (80, 180, 230),
        },
        "purple": {
            "body": (40, 20, 50),
            "highlight": (70, 40, 80),
            "attack": (240, 120, 60),
            "block": (120, 80, 240),
        },
        "gold": {
            "body": (60, 50, 30),
            "highlight": (90, 80, 50),
            "attack": (240, 140, 60),
            "block": (140, 200, 240),
        }
    }

    @staticmethod
    def get_palette(name: str) -> dict:
        """Возвращает цветовую палитру по имени"""
        return ColorPalette.PALETTES.get(name, ColorPalette.PALETTES["default"])

    @staticmethod
    def get_palette_names() -> list:
        """Возвращает список имен всех палитр"""
        return list(ColorPalette.PALETTES.keys())

class Settings:
    """Класс для хранения настроек игры"""
    def __init__(self):
        self.screen_width = 1024
        self.screen_height = 768
        self.fullscreen = False
        self.borderless = False
        self.current_resolution = (1024, 768)

        # Доступные разрешения
        self.available_resolutions = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1366, 768),
            (1600, 900),
            (1920, 1080),
            (2560, 1440)
        ]

    def set_resolution(self, width: int, height: int):
        """Установка разрешения экрана"""
        self.current_resolution = (width, height)
        self.screen_width = width
        self.screen_height = height

    def set_fullscreen(self, fullscreen: bool):
        """Установка полноэкранного режима"""
        self.fullscreen = fullscreen
        self.borderless = False

    def set_borderless(self, borderless: bool):
        """Установка режима без рамок"""
        self.borderless = borderless
        self.fullscreen = False

class Player:
    """Класс игрока с силуэтными персонажами и анимированными руками"""
    def __init__(self, x: int, y: int, is_left: bool = True,
                 body_type: BodyType = BodyType.ATHLETIC,
                 color_palette: str = "default"):
        self.x = x
        self.y = y
        self.is_left = is_left
        self.body_type = body_type
        self.color_palette_name = color_palette
        self.color_palette = ColorPalette.get_palette(color_palette)

        # Основные параметры в зависимости от телосложения
        self.set_body_parameters()

        # Состояния игрока
        self.moving_left = False
        self.moving_right = False
        self.attacking = False
        self.blocking = False
        self.block_direction = "left"
        self.attack_cooldown = 0
        self.block_cooldown = 0
        self.attack_animation = 0
        self.already_hit_in_current_attack = False
        self.attacking_with_right = True

        # Позиции частей тела
        self.body_parts = {}
        self.arm_positions = {
            "left_upper": {"base_x": 0, "base_y": 0, "current_x": 0, "current_y": 0},
            "left_lower": {"base_x": 0, "base_y": 0, "current_x": 0, "current_y": 0},
            "right_upper": {"base_x": 0, "base_y": 0, "current_x": 0, "current_y": 0},
            "right_lower": {"base_x": 0, "base_y": 0, "current_x": 0, "current_y": 0}
        }

        self.update_body_parts()

    def set_body_parameters(self):
        """Установка параметров тела в зависимости от типа"""
        if self.body_type == BodyType.ATHLETIC:
            self.width = 52
            self.height = 130
            self.speed = 5.5
            self.health = 100
            self.max_health = 100
            self.head_radius = 18
            self.shoulder_width = 45
            self.waist_width = 40
            self.arm_thickness = 16
            self.leg_thickness = 18
            self.arm_length = 55

        elif self.body_type == BodyType.LEAN:
            self.width = 42
            self.height = 140
            self.speed = 6.0
            self.health = 90
            self.max_health = 90
            self.head_radius = 16
            self.shoulder_width = 35
            self.waist_width = 32
            self.arm_thickness = 12
            self.leg_thickness = 14
            self.arm_length = 60

        elif self.body_type == BodyType.HEAVY:
            self.width = 65
            self.height = 125
            self.speed = 4.5
            self.health = 120
            self.max_health = 120
            self.head_radius = 22
            self.shoulder_width = 55
            self.waist_width = 50
            self.arm_thickness = 20
            self.leg_thickness = 22
            self.arm_length = 50

        elif self.body_type == BodyType.SUMO:
            self.width = 75
            self.height = 115
            self.speed = 3.5
            self.health = 150
            self.max_health = 150
            self.head_radius = 25
            self.shoulder_width = 60
            self.waist_width = 70
            self.arm_thickness = 18
            self.leg_thickness = 20
            self.arm_length = 45

        elif self.body_type == BodyType.NINJA:
            self.width = 45
            self.height = 135
            self.speed = 6.5
            self.health = 85
            self.max_health = 85
            self.head_radius = 17
            self.shoulder_width = 38
            self.waist_width = 35
            self.arm_thickness = 13
            self.leg_thickness = 15
            self.arm_length = 65

        elif self.body_type == BodyType.ROBOTIC:
            self.width = 58
            self.height = 145
            self.speed = 5.0
            self.health = 110
            self.max_health = 110
            self.head_radius = 20
            self.shoulder_width = 50
            self.waist_width = 45
            self.arm_thickness = 17
            self.leg_thickness = 19
            self.arm_length = 58

    def determine_attack_hand(self, opponent_x: float):
        """Определяет какой рукой бить в зависимости от позиции противника"""
        if opponent_x < self.x + self.width // 2:
            self.attacking_with_right = False
        else:
            self.attacking_with_right = True

        if self.attacking_with_right:
            self.block_direction = "left"
        else:
            self.block_direction = "right"

    def move_left(self):
        """Движение влево"""
        self.moving_left = True
        self.moving_right = False

    def move_right(self):
        """Движение вправо"""
        self.moving_right = True
        self.moving_left = False

    def stop_moving(self):
        """Остановка движения"""
        self.moving_left = False
        self.moving_right = False

    def attack(self, opponent_x: float):
        """Начало атаки с автоматическим выбором руки"""
        if self.attack_cooldown <= 0:
            self.determine_attack_hand(opponent_x)
            self.attacking = True
            self.attack_animation = 15  # Увеличенная длительность анимации
            self.attack_cooldown = 30
            self.already_hit_in_current_attack = False

    def block(self, opponent_x: float):
        """Установка блока с автоматическим выбором стороны"""
        if self.block_cooldown <= 0:
            if opponent_x < self.x + self.width // 2:
                self.block_direction = "left"
            else:
                self.block_direction = "right"
            self.blocking = True
            self.block_cooldown = 40

    def update_body_parts(self):
        """Обновление позиций всех частей тела с анимацией рук"""
        center_x = self.x + self.width // 2
        base_y = self.y

        # Очищаем предыдущие части тела
        self.body_parts = {}

        # Голова
        head_width = self.head_radius * 1.8
        head_height = self.head_radius * 2.2
        self.body_parts["head"] = {
            "type": "ellipse",
            "rect": pygame.Rect(center_x - head_width//2, base_y - head_height + 5, head_width, head_height),
            "color": self.color_palette["body"]
        }

        # Шея
        neck_height = 15
        neck_width = self.head_radius
        self.body_parts["neck"] = {
            "type": "rect",
            "rect": pygame.Rect(center_x - neck_width//2, base_y - neck_height, neck_width, neck_height),
            "color": self.color_palette["body"]
        }

        # Торс
        torso_height = self.height * 0.45
        torso_y = base_y
        torso_top_width = self.shoulder_width * 0.9
        torso_bottom_width = self.waist_width

        self.body_parts["torso"] = {
            "type": "polygon",
            "points": [
                (center_x - torso_top_width//2, torso_y),
                (center_x + torso_top_width//2, torso_y),
                (center_x + torso_bottom_width//2, torso_y + torso_height),
                (center_x - torso_bottom_width//2, torso_y + torso_height)
            ],
            "color": self.color_palette["body"]
        }

        # Таз
        pelvis_height = self.height * 0.25
        pelvis_y = torso_y + torso_height
        pelvis_top_width = torso_bottom_width
        pelvis_bottom_width = pelvis_top_width * 0.8

        self.body_parts["pelvis"] = {
            "type": "polygon",
            "points": [
                (center_x - pelvis_top_width//2, pelvis_y),
                (center_x + pelvis_top_width//2, pelvis_y),
                (center_x + pelvis_bottom_width//2, pelvis_y + pelvis_height),
                (center_x - pelvis_bottom_width//2, pelvis_y + pelvis_height)
            ],
            "color": self.color_palette["body"]
        }

        # Анимация удара
        attack_progress = self.attack_animation / 15.0 if self.attacking else 0
        attack_strength = 1.0 - abs(attack_progress - 0.5) * 2  # Пик на середине анимации

        # Позиции плеч
        left_shoulder_x = center_x - self.shoulder_width // 2 + 5
        right_shoulder_x = center_x + self.shoulder_width // 2 - 5
        shoulder_y = base_y + 5

        # РУКИ С АНИМАЦИЕЙ
        if self.attacking:
            if self.attacking_with_right:
                # Анимация правой руки для удара
                attack_offset_x = 50 * attack_strength
                attack_offset_y = -20 * attack_strength

                # Правая рука (атакующая)
                self.arm_positions["right_upper"]["current_x"] = right_shoulder_x + attack_offset_x * 0.3
                self.arm_positions["right_upper"]["current_y"] = shoulder_y + attack_offset_y * 0.3
                self.arm_positions["right_lower"]["current_x"] = right_shoulder_x + attack_offset_x * 0.7
                self.arm_positions["right_lower"]["current_y"] = shoulder_y + attack_offset_y * 0.7

                # Левая рука (отводится назад)
                self.arm_positions["left_upper"]["current_x"] = left_shoulder_x - 10
                self.arm_positions["left_upper"]["current_y"] = shoulder_y + 5
                self.arm_positions["left_lower"]["current_x"] = left_shoulder_x - 20
                self.arm_positions["left_lower"]["current_y"] = shoulder_y + 30
            else:
                # Анимация левой руки для удара
                attack_offset_x = -50 * attack_strength
                attack_offset_y = -20 * attack_strength

                # Левая рука (атакующая)
                self.arm_positions["left_upper"]["current_x"] = left_shoulder_x + attack_offset_x * 0.3
                self.arm_positions["left_upper"]["current_y"] = shoulder_y + attack_offset_y * 0.3
                self.arm_positions["left_lower"]["current_x"] = left_shoulder_x + attack_offset_x * 0.7
                self.arm_positions["left_lower"]["current_y"] = shoulder_y + attack_offset_y * 0.7

                # Правая рука (отводится назад)
                self.arm_positions["right_upper"]["current_x"] = right_shoulder_x + 10
                self.arm_positions["right_upper"]["current_y"] = shoulder_y + 5
                self.arm_positions["right_lower"]["current_x"] = right_shoulder_x + 20
                self.arm_positions["right_lower"]["current_y"] = shoulder_y + 30
        else:
            # Нормальное положение рук
            self.arm_positions["left_upper"]["current_x"] = left_shoulder_x
            self.arm_positions["left_upper"]["current_y"] = shoulder_y
            self.arm_positions["left_lower"]["current_x"] = left_shoulder_x
            self.arm_positions["left_lower"]["current_y"] = shoulder_y + self.arm_length * 0.6

            self.arm_positions["right_upper"]["current_x"] = right_shoulder_x
            self.arm_positions["right_upper"]["current_y"] = shoulder_y
            self.arm_positions["right_lower"]["current_x"] = right_shoulder_x
            self.arm_positions["right_lower"]["current_y"] = shoulder_y + self.arm_length * 0.6

        # Сохраняем базовые позиции
        self.arm_positions["left_upper"]["base_x"] = left_shoulder_x
        self.arm_positions["left_upper"]["base_y"] = shoulder_y
        self.arm_positions["right_upper"]["base_x"] = right_shoulder_x
        self.arm_positions["right_upper"]["base_y"] = shoulder_y

        # Левая рука (верхняя часть)
        left_upper_arm = {
            "type": "polygon",
            "points": [
                (self.arm_positions["left_upper"]["base_x"], self.arm_positions["left_upper"]["base_y"]),
                (self.arm_positions["left_upper"]["base_x"] - self.arm_thickness, self.arm_positions["left_upper"]["base_y"]),
                (self.arm_positions["left_lower"]["current_x"] - self.arm_thickness * 0.8, self.arm_positions["left_lower"]["current_y"]),
                (self.arm_positions["left_lower"]["current_x"], self.arm_positions["left_lower"]["current_y"])
            ],
            "color": self.color_palette["body"]
        }

        # Левая рука (нижняя часть)
        left_lower_arm = {
            "type": "polygon",
            "points": [
                (self.arm_positions["left_lower"]["current_x"], self.arm_positions["left_lower"]["current_y"]),
                (self.arm_positions["left_lower"]["current_x"] - self.arm_thickness * 0.8, self.arm_positions["left_lower"]["current_y"]),
                (self.arm_positions["left_lower"]["current_x"] - self.arm_thickness * 0.6, self.arm_positions["left_lower"]["current_y"] + self.arm_length * 0.4),
                (self.arm_positions["left_lower"]["current_x"], self.arm_positions["left_lower"]["current_y"] + self.arm_length * 0.4)
            ],
            "color": self.color_palette["body"]
        }

        # Правая рука (верхняя часть)
        right_upper_arm = {
            "type": "polygon",
            "points": [
                (self.arm_positions["right_upper"]["base_x"], self.arm_positions["right_upper"]["base_y"]),
                (self.arm_positions["right_upper"]["base_x"] + self.arm_thickness, self.arm_positions["right_upper"]["base_y"]),
                (self.arm_positions["right_lower"]["current_x"] + self.arm_thickness * 0.8, self.arm_positions["right_lower"]["current_y"]),
                (self.arm_positions["right_lower"]["current_x"], self.arm_positions["right_lower"]["current_y"])
            ],
            "color": self.color_palette["body"]
        }

        # Правая рука (нижняя часть)
        right_lower_arm = {
            "type": "polygon",
            "points": [
                (self.arm_positions["right_lower"]["current_x"], self.arm_positions["right_lower"]["current_y"]),
                (self.arm_positions["right_lower"]["current_x"] + self.arm_thickness * 0.8, self.arm_positions["right_lower"]["current_y"]),
                (self.arm_positions["right_lower"]["current_x"] + self.arm_thickness * 0.6, self.arm_positions["right_lower"]["current_y"] + self.arm_length * 0.4),
                (self.arm_positions["right_lower"]["current_x"], self.arm_positions["right_lower"]["current_y"] + self.arm_length * 0.4)
            ],
            "color": self.color_palette["body"]
        }

        self.body_parts["left_upper_arm"] = left_upper_arm
        self.body_parts["left_lower_arm"] = left_lower_arm
        self.body_parts["right_upper_arm"] = right_upper_arm
        self.body_parts["right_lower_arm"] = right_lower_arm

        # Кисти рук
        hand_size = self.arm_thickness * 0.8
        if self.attacking:
            # Атакующая рука - сжатый кулак
            if self.attacking_with_right:
                right_hand = {
                    "type": "ellipse",
                    "rect": pygame.Rect(
                        self.arm_positions["right_lower"]["current_x"] - hand_size//2,
                        self.arm_positions["right_lower"]["current_y"] + self.arm_length * 0.4 - hand_size//2,
                        hand_size * 1.2,
                        hand_size * 1.2
                    ),
                    "color": self.color_palette["attack"]
                }
                left_hand = {
                    "type": "ellipse",
                    "rect": pygame.Rect(
                        self.arm_positions["left_lower"]["current_x"] - hand_size//2,
                        self.arm_positions["left_lower"]["current_y"] + self.arm_length * 0.4 - hand_size//2,
                        hand_size,
                        hand_size
                    ),
                    "color": self.color_palette["body"]
                }
            else:
                left_hand = {
                    "type": "ellipse",
                    "rect": pygame.Rect(
                        self.arm_positions["left_lower"]["current_x"] - hand_size//2,
                        self.arm_positions["left_lower"]["current_y"] + self.arm_length * 0.4 - hand_size//2,
                        hand_size * 1.2,
                        hand_size * 1.2
                    ),
                    "color": self.color_palette["attack"]
                }
                right_hand = {
                    "type": "ellipse",
                    "rect": pygame.Rect(
                        self.arm_positions["right_lower"]["current_x"] - hand_size//2,
                        self.arm_positions["right_lower"]["current_y"] + self.arm_length * 0.4 - hand_size//2,
                        hand_size,
                        hand_size
                    ),
                    "color": self.color_palette["body"]
                }
        else:
            # Обычное положение - расслабленные кисти
            left_hand = {
                "type": "ellipse",
                "rect": pygame.Rect(
                    self.arm_positions["left_lower"]["current_x"] - hand_size//2,
                    self.arm_positions["left_lower"]["current_y"] + self.arm_length * 0.4 - hand_size//2,
                    hand_size,
                    hand_size
                ),
                "color": self.color_palette["body"]
            }
            right_hand = {
                "type": "ellipse",
                "rect": pygame.Rect(
                    self.arm_positions["right_lower"]["current_x"] - hand_size//2,
                    self.arm_positions["right_lower"]["current_y"] + self.arm_length * 0.4 - hand_size//2,
                    hand_size,
                    hand_size
                ),
                "color": self.color_palette["body"]
            }

        self.body_parts["left_hand"] = left_hand
        self.body_parts["right_hand"] = right_hand

        # Ноги
        leg_length = self.height * 0.5
        leg_start_y = pelvis_y + pelvis_height

        # Левая нога (верхняя часть)
        left_upper_leg = {
            "type": "polygon",
            "points": [
                (center_x - 10, leg_start_y),
                (center_x - 10 - self.leg_thickness, leg_start_y),
                (center_x - 15 - self.leg_thickness, leg_start_y + leg_length//2),
                (center_x - 15, leg_start_y + leg_length//2)
            ],
            "color": self.color_palette["body"]
        }

        # Левая нога (нижняя часть)
        left_lower_leg = {
            "type": "polygon",
            "points": [
                (center_x - 15, leg_start_y + leg_length//2),
                (center_x - 15 - self.leg_thickness, leg_start_y + leg_length//2),
                (center_x - 12 - self.leg_thickness, leg_start_y + leg_length),
                (center_x - 12, leg_start_y + leg_length)
            ],
            "color": self.color_palette["body"]
        }

        # Правая нога (верхняя часть)
        right_upper_leg = {
            "type": "polygon",
            "points": [
                (center_x + 10, leg_start_y),
                (center_x + 10 + self.leg_thickness, leg_start_y),
                (center_x + 15 + self.leg_thickness, leg_start_y + leg_length//2),
                (center_x + 15, leg_start_y + leg_length//2)
            ],
            "color": self.color_palette["body"]
        }

        # Правая нога (нижняя часть)
        right_lower_leg = {
            "type": "polygon",
            "points": [
                (center_x + 15, leg_start_y + leg_length//2),
                (center_x + 15 + self.leg_thickness, leg_start_y + leg_length//2),
                (center_x + 12 + self.leg_thickness, leg_start_y + leg_length),
                (center_x + 12, leg_start_y + leg_length)
            ],
            "color": self.color_palette["body"]
        }

        self.body_parts["left_upper_leg"] = left_upper_leg
        self.body_parts["left_lower_leg"] = left_lower_leg
        self.body_parts["right_upper_leg"] = right_upper_leg
        self.body_parts["right_lower_leg"] = right_lower_leg

        # Ступни
        foot_length = self.leg_thickness * 2
        foot_height = self.leg_thickness * 0.7

        left_foot = {
            "type": "ellipse",
            "rect": pygame.Rect(
                center_x - 12 - foot_length//2,
                leg_start_y + leg_length - foot_height//2,
                foot_length,
                foot_height
            ),
            "color": self.color_palette["body"]
        }

        right_foot = {
            "type": "ellipse",
            "rect": pygame.Rect(
                center_x + 12 - foot_length//2,
                leg_start_y + leg_length - foot_height//2,
                foot_length,
                foot_height
            ),
            "color": self.color_palette["body"]
        }

        self.body_parts["left_foot"] = left_foot
        self.body_parts["right_foot"] = right_foot

        # Специальные детали для разных типов телосложения
        if self.body_type == BodyType.ATHLETIC:
            # Мускульные детали
            chest_detail = {
                "type": "ellipse",
                "rect": pygame.Rect(center_x - 15, base_y + 30, 30, 20),
                "color": self.color_palette["highlight"]
            }
            self.body_parts["chest_detail"] = chest_detail

        elif self.body_type == BodyType.HEAVY:
            # Детали для крупного телосложения
            belly_detail = {
                "type": "ellipse",
                "rect": pygame.Rect(center_x - 20, base_y + 60, 40, 25),
                "color": self.color_palette["highlight"]
            }
            self.body_parts["belly_detail"] = belly_detail

        elif self.body_type == BodyType.SUMO:
            # Пояс сумоиста
            mawashi_width = 60
            mawashi_height = 15
            mawashi = {
                "type": "rect",
                "rect": pygame.Rect(center_x - mawashi_width//2, base_y + 80, mawashi_width, mawashi_height),
                "color": (180, 60, 60)  # Красный пояс
            }
            self.body_parts["mawashi"] = mawashi

            # Прическа сумоиста
            topknot = {
                "type": "ellipse",
                "rect": pygame.Rect(center_x - 10, base_y - self.head_radius*2.2 - 5, 20, 25),
                "color": self.color_palette["body"]
            }
            self.body_parts["topknot"] = topknot

        elif self.body_type == BodyType.NINJA:
            # Повязка ниндзя
            headband_width = 40
            headband_height = 8
            headband = {
                "type": "rect",
                "rect": pygame.Rect(center_x - headband_width//2, base_y - self.head_radius*1.8, headband_width, headband_height),
                "color": (200, 30, 30)  # Красная повязка
            }
            self.body_parts["headband"] = headband

        elif self.body_type == BodyType.ROBOTIC:
            # Детали робота
            panel1 = {
                "type": "rect",
                "rect": pygame.Rect(center_x - 12, base_y + 40, 24, 15),
                "color": self.color_palette["highlight"]
            }
            panel2 = {
                "type": "rect",
                "rect": pygame.Rect(center_x - 8, base_y + 65, 16, 10),
                "color": self.color_palette["highlight"]
            }
            self.body_parts["robot_panel1"] = panel1
            self.body_parts["robot_panel2"] = panel2

            # Антенна
            antenna = {
                "type": "line",
                "points": [(center_x, base_y - self.head_radius*2.2), (center_x, base_y - self.head_radius*2.2 - 20)],
                "color": self.color_palette["highlight"],
                "width": 3
            }
            self.body_parts["antenna"] = antenna

    def update(self, ground_y: int, screen_width: int, opponent_x: Optional[float] = None):
        """Обновление состояния игрока"""
        if self.moving_left and self.x > 0:
            self.x -= self.speed
        if self.moving_right and self.x < screen_width - self.width:
            self.x += self.speed

        self.y = ground_y - self.height

        if self.attacking and self.attack_animation > 0:
            self.attack_animation -= 1
            if self.attack_animation <= 0:
                self.attacking = False
                self.already_hit_in_current_attack = False

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.block_cooldown > 0:
            self.block_cooldown -= 1
            if self.block_cooldown <= 0:
                self.blocking = False

        if opponent_x is not None and self.blocking:
            if opponent_x < self.x + self.width // 2:
                self.block_direction = "left"
            else:
                self.block_direction = "right"

        self.update_body_parts()

    def take_damage(self, damage: int = 10):
        """Получение урона"""
        if not self.blocking:
            self.health = max(0, self.health - damage)
            return True
        return False

    def get_rect(self) -> pygame.Rect:
        """Получение прямоугольника для коллизий"""
        return pygame.Rect(
            self.x,
            self.y - self.head_radius * 2,
            self.width,
            self.height + self.head_radius * 2
        )

    def get_attack_rect(self) -> pygame.Rect:
        """Получение прямоугольника для атаки"""
        if not self.attacking:
            return pygame.Rect(0, 0, 0, 0)

        center_x = self.x + self.width // 2

        if self.attacking_with_right:
            # Прямоугольник для правой атакующей руки
            hand_x = self.arm_positions["right_lower"]["current_x"]
            hand_y = self.arm_positions["right_lower"]["current_y"] + self.arm_length * 0.4

            return pygame.Rect(
                hand_x - 15,
                hand_y - 15,
                30,
                30
            )
        else:
            # Прямоугольник для левой атакующей руки
            hand_x = self.arm_positions["left_lower"]["current_x"]
            hand_y = self.arm_positions["left_lower"]["current_y"] + self.arm_length * 0.4

            return pygame.Rect(
                hand_x - 15,
                hand_y - 15,
                30,
                30
            )

    def get_block_rect(self) -> pygame.Rect:
        """Получение прямоугольника для блока"""
        if not self.blocking:
            return pygame.Rect(0, 0, 0, 0)

        center_x = self.x + self.width // 2
        block_width = 25
        block_height = 80

        if self.block_direction == "left":
            return pygame.Rect(
                center_x - self.shoulder_width//2 - block_width,
                self.y + 25,
                block_width,
                block_height
            )
        else:
            return pygame.Rect(
                center_x + self.shoulder_width//2,
                self.y + 25,
                block_width,
                block_height
            )

    def draw(self, screen: pygame.Surface):
        """Отрисовка персонажа с анимированными руками"""
        # Отрисовка ног и ступней
        for part_name in ["left_upper_leg", "left_lower_leg", "right_upper_leg", "right_lower_leg",
                         "left_foot", "right_foot"]:
            if part_name in self.body_parts:
                part_data = self.body_parts[part_name]
                color = part_data["color"]

                if part_data["type"] == "rect":
                    pygame.draw.rect(screen, color, part_data["rect"], border_radius=3)
                elif part_data["type"] == "ellipse":
                    pygame.draw.ellipse(screen, color, part_data["rect"])
                elif part_data["type"] == "polygon":
                    pygame.draw.polygon(screen, color, part_data["points"])

        # Отрисовка таза и торса
        for part_name in ["pelvis", "torso"]:
            if part_name in self.body_parts:
                part_data = self.body_parts[part_name]
                pygame.draw.polygon(screen, part_data["color"], part_data["points"])

        # Отрисовка рук
        for part_name in ["left_upper_arm", "left_lower_arm", "right_upper_arm", "right_lower_arm"]:
            if part_name in self.body_parts:
                part_data = self.body_parts[part_name]
                pygame.draw.polygon(screen, part_data["color"], part_data["points"])

        # Отрисовка кистей
        for part_name in ["left_hand", "right_hand"]:
            if part_name in self.body_parts:
                part_data = self.body_parts[part_name]
                pygame.draw.ellipse(screen, part_data["color"], part_data["rect"])

        # Отрисовка шеи и головы
        for part_name in ["neck", "head"]:
            if part_name in self.body_parts:
                part_data = self.body_parts[part_name]
                if part_data["type"] == "rect":
                    pygame.draw.rect(screen, part_data["color"], part_data["rect"], border_radius=3)
                elif part_data["type"] == "ellipse":
                    pygame.draw.ellipse(screen, part_data["color"], part_data["rect"])

        # Отрисовка деталей
        for part_name, part_data in self.body_parts.items():
            if part_name not in ["head", "neck", "torso", "pelvis", "left_upper_arm", "left_lower_arm",
                               "right_upper_arm", "right_lower_arm", "left_hand", "right_hand",
                               "left_upper_leg", "left_lower_leg", "right_upper_leg", "right_lower_leg",
                               "left_foot", "right_foot"]:
                color = part_data["color"]

                if part_data["type"] == "rect":
                    pygame.draw.rect(screen, color, part_data["rect"], border_radius=3)
                elif part_data["type"] == "ellipse":
                    pygame.draw.ellipse(screen, color, part_data["rect"])
                elif part_data["type"] == "polygon":
                    pygame.draw.polygon(screen, color, part_data["points"])
                elif part_data["type"] == "line":
                    pygame.draw.line(screen, color,
                                   part_data["points"][0], part_data["points"][1],
                                   part_data.get("width", 3))

        # Отрисовка блока
        if self.blocking:
            block_rect = self.get_block_rect()
            if block_rect.width > 0:
                block_surface = pygame.Surface((block_rect.width, block_rect.height), pygame.SRCALPHA)

                # Для ниндзя - особый эффект блока
                if self.body_type == BodyType.NINJA:
                    for i in range(5):
                        alpha = 100 - i * 20
                        offset = i * 3
                        pygame.draw.rect(block_surface, (*self.color_palette["block"], alpha),
                                       (offset, offset,
                                        block_rect.width - offset*2,
                                        block_rect.height - offset*2),
                                       border_radius=2)
                else:
                    pygame.draw.rect(block_surface, (*self.color_palette["block"], 120),
                                   (0, 0, block_rect.width, block_rect.height), border_radius=4)

                screen.blit(block_surface, block_rect)

class Bot(Player):
    """Класс бота, наследуется от игрока"""
    def __init__(self, x: int, y: int, is_left: bool = True,
                 body_type: BodyType = BodyType.ATHLETIC,
                 color_palette: str = "default"):
        super().__init__(x, y, is_left, body_type, color_palette)
        self.decision_cooldown = 0
        self.aggression = 0.6
        self.caution = 0.4
        self.last_action = None

    def make_decision(self, player: Player, screen_width: int):
        """Принятие решения ботом"""
        if self.decision_cooldown > 0:
            self.decision_cooldown -= 1
            return

        distance = abs(self.x - player.x)
        player_is_left = self.x > player.x

        self.stop_moving()
        self.attacking = False
        self.blocking = False

        if distance < 100:
            if random.random() < self.aggression:
                if random.random() < 0.7:
                    self.attack(player.x)
                    self.last_action = "attack"
                else:
                    if player_is_left:
                        self.move_left()
                    else:
                        self.move_right()
                    self.last_action = "retreat"
            elif random.random() < self.caution:
                self.block(player.x)
                self.last_action = "block"
            else:
                if player_is_left:
                    self.move_left()
                else:
                    self.move_right()
                self.last_action = "advance"

        elif distance < 250:
            if random.random() < 0.4:
                if player_is_left:
                    self.move_left()
                else:
                    self.move_right()
                self.last_action = "advance"
            elif random.random() < 0.3:
                self.block(player.x)
                self.last_action = "prepare"
            else:
                self.last_action = "wait"

        else:
            if random.random() < 0.8:
                if player_is_left:
                    self.move_left()
                else:
                    self.move_right()
                self.last_action = "advance"
            else:
                self.last_action = "wait"

        self.decision_cooldown = random.randint(10, 25)

        if self.health < 30:
            self.aggression = min(0.9, self.aggression + 0.1)
            self.caution = max(0.1, self.caution - 0.1)

class Game:
    """Основной класс игры"""
    def __init__(self, settings: Settings):
        self.settings = settings
        self.state = GameState.MENU
        self.screen = None
        self.clock = pygame.time.Clock()
        self.font = None

        # Меню и настройки
        self.menu_selection = 0
        self.settings_selection = 0
        self.controls_selection = 0

        # Выбор персонажей
        self.player1_selection = 0
        self.player1_color_selection = 0
        self.player2_selection = 0
        self.player2_color_selection = 0

        self.selected_body_type_p1 = BodyType.ATHLETIC
        self.selected_color_p1 = "default"
        self.selected_body_type_p2 = BodyType.ATHLETIC
        self.selected_color_p2 = "default"

        # Игровые объекты
        self.player1 = None
        self.player2 = None
        self.bot = None
        self.ground_y = 0
        self.winner = None
        self.game_time = 0
        self.round_time = 0
        self.hit_effects = []
        self.battle_finished = False

        # Фон для игры
        self.background_image = None
        self.create_background()

        # Инициализация экрана
        self.init_screen()

        # Цвета
        self.dark_gray = (20, 25, 30)
        self.black = (10, 10, 15)
        self.light_gray = (120, 125, 130)
        self.white = (230, 235, 240)
        self.highlight_color = (210, 90, 90)
        self.ground_color = (45, 50, 55)
        self.info_color = (90, 160, 240)
        self.arena_color = (30, 35, 40)

        # Загрузка шрифтов
        self.title_font = None
        self.load_fonts()

    def create_background(self):
        """Создание тематического фона для игры"""
        width, height = 1024, 768
        self.background_image = pygame.Surface((width, height))

        # Градиентное небо
        sky_colors = [
            ((15, 20, 30), 0),
            ((25, 35, 45), height * 0.4),
            ((35, 45, 55), height * 0.7),
            ((45, 55, 65), height)
        ]

        for i in range(len(sky_colors)-1):
            color1, y1 = sky_colors[i]
            color2, y2 = sky_colors[i+1]
            for y in range(int(y1), int(y2)):
                ratio = (y - y1) / (y2 - y1)
                r = int(color1[0] + (color2[0] - color1[0]) * ratio)
                g = int(color1[1] + (color2[1] - color1[1]) * ratio)
                b = int(color1[2] + (color2[2] - color1[2]) * ratio)
                pygame.draw.line(self.background_image, (r, g, b), (0, y), (width, y))

        # Облака
        cloud_colors = [(50, 60, 70, 100), (55, 65, 75, 80), (60, 70, 80, 60)]
        cloud_positions = [
            (200, 100, 120, 40),
            (500, 150, 180, 50),
            (800, 80, 150, 45),
            (100, 200, 100, 35),
            (700, 250, 200, 55)
        ]

        for x, y, w, h in cloud_positions:
            for i, color in enumerate(cloud_colors):
                cloud_surface = pygame.Surface((w + i*20, h + i*10), pygame.SRCALPHA)
                pygame.draw.ellipse(cloud_surface, color, (0, 0, w + i*20, h + i*10))
                self.background_image.blit(cloud_surface, (x - i*10, y - i*5))

        # Горы на заднем плане
        mountain_colors = [(40, 50, 60), (35, 45, 55), (30, 40, 50)]
        mountain_peaks = [
            [(0, height*0.6), (200, height*0.3), (400, height*0.6)],
            [(300, height*0.6), (500, height*0.4), (700, height*0.6)],
            [(600, height*0.6), (800, height*0.35), (1000, height*0.6)],
            [(900, height*0.6), (1100, height*0.45), (1300, height*0.6)]
        ]

        for i, peaks in enumerate(mountain_peaks):
            color = mountain_colors[i % len(mountain_colors)]
            pygame.draw.polygon(self.background_image, color, peaks)

        # Деревья (силуэты)
        for x in range(50, width, 150):
            tree_height = random.randint(80, 120)
            tree_width = random.randint(40, 60)
            tree_y = height * 0.7

            # Ствол
            trunk_width = tree_width // 4
            trunk_height = tree_height // 3
            pygame.draw.rect(self.background_image, (45, 40, 35),
                           (x - trunk_width//2, tree_y, trunk_width, trunk_height))

            # Крона (треугольники)
            crown_points = [
                (x, tree_y - tree_height),
                (x - tree_width//2, tree_y - tree_height//3),
                (x + tree_width//2, tree_y - tree_height//3)
            ]
            pygame.draw.polygon(self.background_image, (25, 35, 30), crown_points)

    def load_fonts(self):
        """Загрузка шрифтов"""
        try:
            self.font = pygame.font.Font(None, 36)
            self.title_font = pygame.font.Font(None, 72)
            self.small_font = pygame.font.Font(None, 24)
            self.medium_font = pygame.font.Font(None, 32)
        except:
            self.font = pygame.font.SysFont(None, 36)
            self.title_font = pygame.font.SysFont(None, 72)
            self.small_font = pygame.font.SysFont(None, 24)
            self.medium_font = pygame.font.SysFont(None, 32)

    def init_screen(self):
        """Инициализация экрана с текущими настройками"""
        flags = 0
        if self.settings.fullscreen:
            flags = pygame.FULLSCREEN
        elif self.settings.borderless:
            flags = pygame.NOFRAME

        self.screen = pygame.display.set_mode(
            self.settings.current_resolution,
            flags
        )
        pygame.display.set_caption("Дуэлянты - Арена Силуэтов")

        self.ground_y = self.settings.screen_height - 120

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = GameState.EXIT
                return

            # Обработка событий мыши для всех состояний
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Только левая кнопка мыши
                    mouse_pos = pygame.mouse.get_pos()

                    if self.state == GameState.MENU:
                        self.handle_menu_mouse_click(mouse_pos)
                    elif self.state == GameState.CHARACTER_SELECT_P1:
                        self.handle_character_select_p1_mouse_click(mouse_pos)
                    elif self.state == GameState.CHARACTER_SELECT_P2:
                        self.handle_character_select_p2_mouse_click(mouse_pos)
                    elif self.state == GameState.SETTINGS:
                        self.handle_settings_mouse_click(mouse_pos)
                    elif self.state == GameState.CONTROLS:
                        self.handle_controls_mouse_click(mouse_pos)
                    elif self.state in [GameState.PLAYER_VS_PLAYER, GameState.PLAYER_VS_BOT]:
                        # Получаем позицию мыши для игрового режима
                        mouse_pos = pygame.mouse.get_pos()
                        self.handle_game_mouse_click(event, mouse_pos)

            # Обработка клавиатурных событий
            if self.state == GameState.MENU:
                self.handle_menu_events(event)
            elif self.state == GameState.CHARACTER_SELECT_P1:
                self.handle_character_select_p1_events(event)
            elif self.state == GameState.CHARACTER_SELECT_P2:
                self.handle_character_select_p2_events(event)
            elif self.state == GameState.SETTINGS:
                self.handle_settings_events(event)
            elif self.state == GameState.CONTROLS:
                self.handle_controls_events(event)
            elif self.state in [GameState.PLAYER_VS_PLAYER, GameState.PLAYER_VS_BOT]:
                self.handle_game_events(event)

        self.handle_continuous_input()

        # Обработка наведения мыши (для подсветки)
        # Получаем позицию мыши один раз для всех обработчиков
        mouse_pos = pygame.mouse.get_pos()

        if self.state in [GameState.MENU, GameState.SETTINGS, GameState.CONTROLS,
                          GameState.CHARACTER_SELECT_P1, GameState.CHARACTER_SELECT_P2]:
            self.handle_mouse_hover(mouse_pos)

    def handle_mouse_hover(self, mouse_pos):  # ← Добавить параметр
        """Обработка наведения мыши для подсветки элементов"""
        # Убрать строку: mouse_pos = pygame.mouse.get_pos()
        if self.state == GameState.MENU:
            self.update_menu_mouse_hover(mouse_pos)
        elif self.state == GameState.SETTINGS:
            self.update_settings_mouse_hover(mouse_pos)
        elif self.state == GameState.CONTROLS:
            self.update_controls_mouse_hover(mouse_pos)
        # Для выбора персонажей наведение обрабатывается в draw_character_select

    def handle_game_mouse_click(self, event, mouse_pos):
        """Обработка кликов мыши в игровом режиме"""
        # Проверяем клик по кнопке возврата в меню (если бой завершен)
        if self.battle_finished and self.winner:
            return_width = 350
            return_height = 60
            return_x = self.settings.screen_width // 2 - return_width // 2
            return_y = self.settings.screen_height - 150

            return_rect = pygame.Rect(return_x, return_y, return_width, return_height)
            if return_rect.collidepoint(mouse_pos):
                self.return_to_menu()

    def handle_mouse_click(self, event):
        """Обработка кликов мыши"""
        if event.button != 1:  # Только левая кнопка мыши
            return

        mouse_pos = pygame.mouse.get_pos()

        if self.state == GameState.MENU:
            self.handle_menu_mouse_click(mouse_pos)
        elif self.state == GameState.CHARACTER_SELECT_P1:
            self.handle_character_select_p1_mouse_click(mouse_pos)
        elif self.state == GameState.CHARACTER_SELECT_P2:
            self.handle_character_select_p2_mouse_click(mouse_pos)
        elif self.state == GameState.SETTINGS:
            self.handle_settings_mouse_click(mouse_pos)
        elif self.state == GameState.CONTROLS:
            self.handle_controls_mouse_click(mouse_pos)

    def handle_menu_mouse_click(self, mouse_pos):
        """Обработка кликов мыши в главном меню"""
        menu_items = [
            "БОЙ С БОТОМ",
            "ИГРОК ПРОТИВ ИГРОКА",
            "ПРАВИЛА И УПРАВЛЕНИЕ",
            "НАСТРОЙКИ",
            "ВЫХОД"
        ]

        for i, item in enumerate(menu_items):
            text = self.font.render(item, True, self.white)
            text_rect = text.get_rect(center=(self.settings.screen_width // 2, 300 + i * 60))

            # Проверяем клик по тексту (расширяем область для удобства)
            click_rect = text_rect.inflate(20, 10)
            if click_rect.collidepoint(mouse_pos):
                self.menu_selection = i

                if i == 0:
                    self.state = GameState.CHARACTER_SELECT_P1
                    self.player1_selection = 0
                    self.player1_color_selection = 0
                elif i == 1:
                    self.state = GameState.CHARACTER_SELECT_P1
                    self.player1_selection = 0
                    self.player1_color_selection = 0
                elif i == 2:
                    self.state = GameState.CONTROLS
                    self.controls_selection = 0
                elif i == 3:
                    self.state = GameState.SETTINGS
                    self.settings_selection = 0
                elif i == 4:
                    self.state = GameState.EXIT
                break

    def update_menu_mouse_hover(self, mouse_pos):
        """Обновление подсветки в главном меню"""
        menu_items = [
            "БОЙ С БОТОМ",
            "ИГРОК ПРОТИВ ИГРОКА",
            "ПРАВИЛА И УПРАВЛЕНИЕ",
            "НАСТРОЙКИ",
            "ВЫХОД"
        ]

        for i, item in enumerate(menu_items):
            text = self.font.render(item, True, self.white)
            text_rect = text.get_rect(center=(self.settings.screen_width // 2, 300 + i * 60))

            # Проверяем наведение на текст (расширяем область для удобства)
            hover_rect = text_rect.inflate(20, 10)
            if hover_rect.collidepoint(mouse_pos):
                self.menu_selection = i
                break

    def handle_settings_mouse_click(self, mouse_pos):
        """Обработка кликов мыши в настройках"""
        settings_items = [
            "Оконный режим",
            "Оконный без рамки",
            "Полноэкранный"
        ]

        for i in range(3 + len(self.settings.available_resolutions)):
            item_y = 150 + i * 45

            # Проверяем клик по строке настроек
            click_rect = pygame.Rect(self.settings.screen_width // 2 - 150, item_y - 20, 300, 40)
            if click_rect.collidepoint(mouse_pos):
                self.settings_selection = i

                if i == 0:
                    self.settings.set_fullscreen(False)
                    self.settings.set_borderless(False)
                    self.init_screen()
                elif i == 1:
                    self.settings.set_borderless(True)
                    self.init_screen()
                elif i == 2:
                    self.settings.set_fullscreen(True)
                    self.init_screen()
                else:
                    res_index = i - 3
                    if res_index < len(self.settings.available_resolutions):
                        width, height = self.settings.available_resolutions[res_index]
                        self.settings.set_resolution(width, height)
                        self.init_screen()
                        self.create_background()
                break

    def update_settings_mouse_hover(self, mouse_pos):
        """Обновление подсветки в настройках"""
        for i in range(3 + len(self.settings.available_resolutions)):
            item_y = 150 + i * 45

            # Проверяем наведение на строку настроек
            hover_rect = pygame.Rect(self.settings.screen_width // 2 - 150, item_y - 20, 300, 40)
            if hover_rect.collidepoint(mouse_pos):
                self.settings_selection = i
                break

    def handle_controls_mouse_click(self, mouse_pos):
        """Обработка кликов мыши в меню управления"""
        # Проверяем клик по кнопке "Назад"
        back_width = 300
        back_height = 50
        back_x = self.settings.screen_width // 2 - back_width // 2
        back_y = self.settings.screen_height - 100

        back_rect = pygame.Rect(back_x, back_y, back_width, back_height)
        if back_rect.collidepoint(mouse_pos):
            self.state = GameState.MENU

    def update_controls_mouse_hover(self, mouse_pos):
        """Обновление подсветки в меню управления"""
        # Проверяем наведение на кнопку "Назад"
        back_width = 300
        back_height = 50
        back_x = self.settings.screen_width // 2 - back_width // 2
        back_y = self.settings.screen_height - 100

        back_rect = pygame.Rect(back_x, back_y, back_width, back_height)
        self.controls_selection = 0 if back_rect.collidepoint(mouse_pos) else -1

    def handle_menu_events(self, event):
        """Обработка событий меню"""
        if event.type == pygame.KEYDOWN:
            # Поддержка WASD и стрелок
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.menu_selection = (self.menu_selection - 1) % 5
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.menu_selection = (self.menu_selection + 1) % 5
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                self.menu_selection = (self.menu_selection - 1) % 5
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.menu_selection = (self.menu_selection + 1) % 5
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.menu_selection == 0:
                    self.state = GameState.CHARACTER_SELECT_P1
                    self.player1_selection = 0
                    self.player1_color_selection = 0
                elif self.menu_selection == 1:
                    self.state = GameState.CHARACTER_SELECT_P1
                    self.player1_selection = 0
                    self.player1_color_selection = 0
                elif self.menu_selection == 2:
                    self.state = GameState.CONTROLS
                    self.controls_selection = 0
                elif self.menu_selection == 3:
                    self.state = GameState.SETTINGS
                    self.settings_selection = 0
                elif self.menu_selection == 4:
                    self.state = GameState.EXIT

    # В классе Game, в методе handle_character_select_p1_events добавляем поддержку мыши:

    def handle_character_select_p1_events(self, event):
        """Обработка событий выбора персонажа для игрока 1"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                # Должно работать для всех 6 типов
                self.player1_selection = (self.player1_selection - 1) % len(BodyType)
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.player1_selection = (self.player1_selection + 1) % len(BodyType)
            elif event.key in [pygame.K_UP, pygame.K_w]:
                self.player1_color_selection = (self.player1_color_selection - 1) % len(
                    ColorPalette.get_palette_names())
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.player1_color_selection = (self.player1_color_selection + 1) % len(
                    ColorPalette.get_palette_names())
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.confirm_p1_selection()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                mouse_pos = pygame.mouse.get_pos()
                self.handle_character_select_p1_mouse_click(mouse_pos)

    def handle_character_select_p1_mouse_click(self, mouse_pos):
        """Обработка кликов мыши в выборе персонажа для игрока 1"""
        print(f"DEBUG: Обработка клика мыши в позиции {mouse_pos}")  # Отладочный вывод

        # Проверяем клик по цветам ПЕРВЫМ делом
        color_names = ColorPalette.get_palette_names()
        color_start_x = self.settings.screen_width // 2 - (len(color_names) * 50) // 2

        for i in range(len(color_names)):
            color_x = color_start_x + i * 50
            color_rect = pygame.Rect(color_x, 650, 45, 45)
            if color_rect.collidepoint(mouse_pos):
                print(f"DEBUG: Выбран цвет #{i}: {color_names[i]}")
                self.player1_color_selection = i
                return  # Возвращаемся, так как цвет выбран

        # Проверяем клик по кнопке "Подтвердить"
        confirm_rect = pygame.Rect(
            self.settings.screen_width // 2 - 150,
            self.settings.screen_height - 120,
            300, 50
        )

        # Проверяем клик по типам телосложения (стрелки)
        left_arrow_rect = pygame.Rect(self.settings.screen_width // 2 - 200, 400, 50, 50)
        right_arrow_rect = pygame.Rect(self.settings.screen_width // 2 + 150, 400, 50, 50)

        if left_arrow_rect.collidepoint(mouse_pos):
            self.player1_selection = (self.player1_selection - 1) % len(BodyType)
            print(f"DEBUG: Выбран тип #{self.player1_selection}")
        elif right_arrow_rect.collidepoint(mouse_pos):
            self.player1_selection = (self.player1_selection + 1) % len(BodyType)
            print(f"DEBUG: Выбран тип #{self.player1_selection}")
        elif confirm_rect.collidepoint(mouse_pos):
            print("DEBUG: Нажата кнопка подтверждения")
            self.confirm_p1_selection()

        # Проверяем клик по кнопке "Назад"
        back_rect = pygame.Rect(20, 20, 100, 40)
        if back_rect.collidepoint(mouse_pos):
            print("DEBUG: Нажата кнопка Назад")
            self.state = GameState.MENU

    def confirm_p1_selection(self):
        """Подтверждение выбора для игрока 1"""
        # Сохраняем выбор для игрока 1
        body_types = list(BodyType)
        self.selected_body_type_p1 = body_types[self.player1_selection]

        color_names = ColorPalette.get_palette_names()
        self.selected_color_p1 = color_names[self.player1_color_selection]

        print(f"Выбран персонаж для Игрока 1: {self.selected_body_type_p1}, цвет: {self.selected_color_p1}")

        # В зависимости от режима игры переходим к следующему шагу
        if self.menu_selection == 0:  # Бой с ботом
            # Запускаем игру против бота
            self.start_player_vs_bot()
        else:  # Игрок против игрока - выбираем второго игрока
            self.state = GameState.CHARACTER_SELECT_P2
            self.player2_selection = 0
            self.player2_color_selection = 0

    def handle_character_select_p2_events(self, event):
        """Обработка событий выбора персонажа для игрока 2"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.CHARACTER_SELECT_P1  # Возвращаемся к выбору первого игрока
            # Поддержка WASD и стрелок
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                self.player2_selection = (self.player2_selection - 1) % len(BodyType)
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.player2_selection = (self.player2_selection + 1) % len(BodyType)
            elif event.key in [pygame.K_UP, pygame.K_w]:
                self.player2_color_selection = (self.player2_color_selection - 1) % len(
                    ColorPalette.get_palette_names())
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.player2_color_selection = (self.player2_color_selection + 1) % len(
                    ColorPalette.get_palette_names())
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.confirm_p2_selection()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                mouse_pos = pygame.mouse.get_pos()
                self.handle_character_select_p2_mouse_click(mouse_pos)

    def handle_character_select_p2_mouse_click(self, mouse_pos):
        """Обработка кликов мыши в выборе персонажа для игрока 2"""
        # Проверяем клик по цветам ПЕРВЫМ делом
        color_names = ColorPalette.get_palette_names()
        color_start_x = self.settings.screen_width // 2 - (len(color_names) * 50) // 2

        for i in range(len(color_names)):
            color_x = color_start_x + i * 50
            color_rect = pygame.Rect(color_x, 650, 45, 45)
            if color_rect.collidepoint(mouse_pos):
                self.player2_color_selection = i
                return  # Возвращаемся, так как цвет выбран

        # Проверяем клик по кнопке "Начать бой"
        start_rect = pygame.Rect(
            self.settings.screen_width // 2 - 150,
            self.settings.screen_height - 120,
            300, 50
        )

        # Проверяем клик по типам телосложения (стрелки)
        left_arrow_rect = pygame.Rect(self.settings.screen_width // 2 - 200, 400, 50, 50)
        right_arrow_rect = pygame.Rect(self.settings.screen_width // 2 + 150, 400, 50, 50)

        if left_arrow_rect.collidepoint(mouse_pos):
            self.player2_selection = (self.player2_selection - 1) % len(BodyType)
        elif right_arrow_rect.collidepoint(mouse_pos):
            self.player2_selection = (self.player2_selection + 1) % len(BodyType)
        elif start_rect.collidepoint(mouse_pos):
            self.confirm_p2_selection()

        # Проверяем клик по кнопке "Назад"
        back_rect = pygame.Rect(20, 20, 100, 40)
        if back_rect.collidepoint(mouse_pos):
            self.state = GameState.CHARACTER_SELECT_P1

    def confirm_p2_selection(self):
        """Подтверждение выбора для игрока 2"""
        # Сохраняем выбор для игрока 2
        body_types = list(BodyType)
        self.selected_body_type_p2 = body_types[self.player2_selection]

        color_names = ColorPalette.get_palette_names()
        self.selected_color_p2 = color_names[self.player2_color_selection]

        # Начинаем игру
        self.start_player_vs_player()

    def handle_settings_events(self, event):
        """Обработка событий настроек"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU
            # Поддержка WASD и стрелок
            elif event.key in [pygame.K_UP, pygame.K_w]:
                self.settings_selection = (self.settings_selection - 1) % (
                        3 + len(self.settings.available_resolutions)
                )
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.settings_selection = (self.settings_selection + 1) % (
                        3 + len(self.settings.available_resolutions)
                )
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.settings_selection == 0:
                    self.settings.set_fullscreen(False)
                    self.settings.set_borderless(False)
                    self.init_screen()
                elif self.settings_selection == 1:
                    self.settings.set_borderless(True)
                    self.init_screen()
                elif self.settings_selection == 2:
                    self.settings.set_fullscreen(True)
                    self.init_screen()
                else:
                    res_index = self.settings_selection - 3
                    if res_index < len(self.settings.available_resolutions):
                        width, height = self.settings.available_resolutions[res_index]
                        self.settings.set_resolution(width, height)
                        self.init_screen()
                        self.create_background()

    def handle_controls_events(self, event):
        """Обработка событий в меню управления"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU
            # Поддержка WASD и стрелок
            elif event.key in [pygame.K_UP, pygame.K_w]:
                self.controls_selection = (self.controls_selection - 1) % 2
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.controls_selection = (self.controls_selection + 1) % 2
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.controls_selection == 0:  # Кнопка "Назад"
                    self.state = GameState.MENU

    def handle_game_events(self, event):
        """Обработка событий игры"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.return_to_menu()

            # Если бой завершен, блокируем игровое управление, но оставляем выход
            if self.battle_finished:
                return

            if event.key == pygame.K_a:
                self.player1.move_left()
            elif event.key == pygame.K_d:
                self.player1.move_right()
            elif event.key == pygame.K_LALT:
                if self.state == GameState.PLAYER_VS_BOT:
                    self.player1.attack(self.bot.x)
                elif self.state == GameState.PLAYER_VS_PLAYER:
                    self.player1.attack(self.player2.x)
            elif event.key == pygame.K_w:
                if self.state == GameState.PLAYER_VS_BOT:
                    self.player1.block(self.bot.x)
                elif self.state == GameState.PLAYER_VS_PLAYER:
                    self.player1.block(self.player2.x)

            if self.state == GameState.PLAYER_VS_PLAYER:
                if event.key == pygame.K_LEFT:
                    self.player2.move_left()
                elif event.key == pygame.K_RIGHT:
                    self.player2.move_right()
                elif event.key == pygame.K_RALT:
                    self.player2.attack(self.player1.x)
                elif event.key == pygame.K_UP:
                    self.player2.block(self.player1.x)

        if event.type == pygame.KEYUP:
            # Если бой завершен, блокируем игровое управление
            if self.battle_finished:
                return

            if event.key in [pygame.K_a, pygame.K_d]:
                self.player1.stop_moving()

            if self.state == GameState.PLAYER_VS_PLAYER:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    self.player2.stop_moving()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                mouse_pos = pygame.mouse.get_pos()

                # Если бой завершен, проверяем клик по кнопке возврата
                if self.battle_finished and self.winner:
                    return_width = 350
                    return_height = 60
                    return_x = self.settings.screen_width // 2 - return_width // 2
                    return_y = self.settings.screen_height - 150

                    return_rect = pygame.Rect(return_x, return_y, return_width, return_height)
                    if return_rect.collidepoint(mouse_pos):
                        self.return_to_menu()
                        return

    def return_to_menu(self):
        """Возврат в главное меню"""
        self.state = GameState.MENU
        self.winner = None
        self.battle_finished = False
        self.round_time = 0
        self.hit_effects = []

        # Сбрасываем выбор персонажей для нового раунда
        self.player1 = None
        self.player2 = None
        self.bot = None

    def handle_continuous_input(self):
        """Обработка непрерывного ввода"""
        # Если бой завершен, блокируем игровое управление
        if self.battle_finished:
            return

        # Если мы находимся в выборе персонажа или меню, не обрабатываем игровое управление
        if self.state not in [GameState.PLAYER_VS_PLAYER, GameState.PLAYER_VS_BOT]:
            return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and self.player1:
            self.player1.move_left()
        if keys[pygame.K_d] and self.player1:
            self.player1.move_right()

        if self.state == GameState.PLAYER_VS_PLAYER:
            if keys[pygame.K_LEFT] and self.player2:
                self.player2.move_left()
            if keys[pygame.K_RIGHT] and self.player2:
                self.player2.move_right()

    def start_player_vs_bot(self):
        """Начало игры против бота"""
        self.state = GameState.PLAYER_VS_BOT
        self.player1 = Player(200, self.ground_y - 100, is_left=True,
                             body_type=self.selected_body_type_p1,
                             color_palette=self.selected_color_p1)

        # Бот получает случайный тип тела
        bot_type = random.choice(list(BodyType))
        bot_color = random.choice(["default", "red", "blue", "green", "purple"])

        self.bot = Bot(self.settings.screen_width - 300, self.ground_y - 100, is_left=False,
                      body_type=bot_type,
                      color_palette=bot_color)
        self.winner = None
        self.round_time = 0
        self.hit_effects = []
        self.battle_finished = False

    def start_player_vs_player(self):
        """Начало игры игрок против игрока"""
        self.state = GameState.PLAYER_VS_PLAYER
        self.player1 = Player(200, self.ground_y - 100, is_left=True,
                             body_type=self.selected_body_type_p1,
                             color_palette=self.selected_color_p1)

        self.player2 = Player(self.settings.screen_width - 300, self.ground_y - 100, is_left=False,
                            body_type=self.selected_body_type_p2,
                            color_palette=self.selected_color_p2)
        self.winner = None
        self.round_time = 0
        self.hit_effects = []
        self.battle_finished = False

    def update_game(self):
        """Обновление игрового состояния"""
        # Если бой завершен, не обновляем состояние игроков
        if self.battle_finished:
            # Обновляем только эффекты попаданий
            self.update_hit_effects()
            return

        self.game_time += 1
        self.round_time += 1

        self.update_hit_effects()

        if self.state == GameState.PLAYER_VS_BOT:
            self.player1.update(self.ground_y, self.settings.screen_width, self.bot.x)
            self.bot.update(self.ground_y, self.settings.screen_width, self.player1.x)
            self.bot.make_decision(self.player1, self.settings.screen_width)
            self.check_collisions(self.player1, self.bot)

            if self.player1.health <= 0:
                self.winner = "БОТ"
                self.battle_finished = True  # ← Добавить эту строку
            elif self.bot.health <= 0:
                self.winner = "ИГРОК 1"
                self.battle_finished = True  # ← Добавить эту строку

        elif self.state == GameState.PLAYER_VS_PLAYER:
            self.player1.update(self.ground_y, self.settings.screen_width, self.player2.x)
            self.player2.update(self.ground_y, self.settings.screen_width, self.player1.x)
            self.check_collisions(self.player1, self.player2)

            if self.player1.health <= 0:
                self.winner = "ИГРОК 2"
                self.battle_finished = True  # ← Добавить эту строку
            elif self.player2.health <= 0:
                self.winner = "ИГРОК 1"
                self.battle_finished = True  # ← Добавить эту строку

    def update_hit_effects(self):
        """Обновление эффектов попаданий"""
        for effect in self.hit_effects[:]:
            effect['timer'] -= 1
            if effect['timer'] <= 0:
                self.hit_effects.remove(effect)

    def check_collisions(self, player1: Player, player2: Player):
        """Проверка коллизий между двумя игроками"""
        # Проверка атаки игрока 1
        if (player1.attacking and
            not player1.already_hit_in_current_attack and
            player1.get_attack_rect().colliderect(player2.get_rect())):

            block_hit = False

            if player2.blocking:
                if player1.attacking_with_right:
                    if player2.block_direction == "right":
                        if player1.x < player2.x:
                            block_hit = True
                else:
                    if player2.block_direction == "left":
                        if player1.x > player2.x:
                            block_hit = True

            if not block_hit:
                damage_dealt = player2.take_damage(10)
                if damage_dealt:
                    self.create_hit_effect(player2.x + player2.width // 2, player2.y + player2.height // 2)
                    player1.already_hit_in_current_attack = True
            else:
                player1.already_hit_in_current_attack = True

        # Проверка атаки игрока 2
        if (player2.attacking and
            not player2.already_hit_in_current_attack and
            player2.get_attack_rect().colliderect(player1.get_rect())):

            block_hit = False

            if player1.blocking:
                if player2.attacking_with_right:
                    if player1.block_direction == "right":
                        if player2.x < player1.x:
                            block_hit = True
                else:
                    if player1.block_direction == "left":
                        if player2.x > player1.x:
                            block_hit = True

            if not block_hit:
                damage_dealt = player1.take_damage(10)
                if damage_dealt:
                    self.create_hit_effect(player1.x + player1.width // 2, player1.y + player1.height // 2)
                    player2.already_hit_in_current_attack = True
            else:
                player2.already_hit_in_current_attack = True

    def create_hit_effect(self, x: int, y: int):
        """Создание визуального эффекта попадания"""
        self.hit_effects.append({
            'x': x,
            'y': y,
            'timer': 15,
            'size': 35,
            'color': (230, 70, 70, 180)
        })

    def draw_menu(self):
        """Отрисовка главного меню"""
        self.screen.fill(self.dark_gray)

        # Градиентный фон меню
        for y in range(self.settings.screen_height):
            color_value = int(25 + (y / self.settings.screen_height) * 20)
            pygame.draw.line(self.screen, (color_value, color_value + 5, color_value + 10),
                             (0, y), (self.settings.screen_width, y))

        # Заголовок с тенью
        title_text = "ДУЭЛЯНТЫ"
        title_shadow = self.title_font.render(title_text, True, (10, 10, 15))
        title_main = self.title_font.render(title_text, True, (210, 90, 90))

        title_rect = title_main.get_rect(center=(self.settings.screen_width // 2, 120))
        shadow_rect = title_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3

        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title_main, title_rect)

        subtitle = self.font.render("Арена Силуэтов", True, (160, 160, 180))
        subtitle_rect = subtitle.get_rect(center=(self.settings.screen_width // 2, 190))
        self.screen.blit(subtitle, subtitle_rect)

        # Пункты меню
        menu_items = [
            "БОЙ С БОТОМ",
            "ИГРОК ПРОТИВ ИГРОКА",
            "ПРАВИЛА И УПРАВЛЕНИЕ",
            "НАСТРОЙКИ",
            "ВЫХОД"
        ]

        for i, item in enumerate(menu_items):
            # Определяем цвет и подсветку в зависимости от выбора и наведения мыши
            is_hovered = i == self.menu_selection
            color = self.highlight_color if is_hovered else self.white
            bg_color = (60, 65, 70, 180) if is_hovered else (40, 45, 50, 0)

            # Создаем фоновую панель для пункта меню
            item_width = 400
            item_height = 45
            item_x = self.settings.screen_width // 2 - item_width // 2
            item_y = 275 + i * 60

            if is_hovered:
                # Рисуем фоновую панель для подсвеченного пункта
                panel = pygame.Surface((item_width, item_height), pygame.SRCALPHA)
                panel.fill(bg_color)
                self.screen.blit(panel, (item_x, item_y))

                # Рисуем рамку вокруг панели
                pygame.draw.rect(self.screen, self.highlight_color,
                                 (item_x, item_y, item_width, item_height), 2, border_radius=5)

            text = self.font.render(item, True, color)
            text_rect = text.get_rect(center=(self.settings.screen_width // 2, 300 + i * 60))
            self.screen.blit(text, text_rect)

            if is_hovered:
                # Анимированные маркеры выбора
                marker_size = abs(pygame.time.get_ticks() // 50 % 20 - 10) + 15
                left_marker = pygame.Rect(text_rect.left - 50, text_rect.centery - marker_size // 2,
                                          marker_size, marker_size)
                right_marker = pygame.Rect(text_rect.right + 50 - marker_size, text_rect.centery - marker_size // 2,
                                           marker_size, marker_size)
                pygame.draw.rect(self.screen, self.highlight_color, left_marker, border_radius=marker_size // 2)
                pygame.draw.rect(self.screen, self.highlight_color, right_marker, border_radius=marker_size // 2)

            # Силуэты бойцов внизу - ПОКАЗЫВАЕМ ВСЕХ 6 ПЕРСОНАЖЕЙ
            fighter_y = self.settings.screen_height - 150
            fighter_spacing = 140  # Уменьшаем расстояние между персонажами

            # Получаем ВСЕ типы телосложения
            all_body_types = list(BodyType)  # [ATHLETIC, LEAN, HEAVY, SUMO, NINJA, ROBOTIC]

            # Отображаем всех 6 персонажей
            for i, body_type in enumerate(all_body_types):
                fighter_x = self.settings.screen_width // 2 + (
                            i - len(all_body_types) // 2) * fighter_spacing + fighter_spacing // 2
                preview_fighter = Player(fighter_x - 30, fighter_y,
                                         is_left=(i < len(all_body_types) // 2),
                                         body_type=body_type,
                                         color_palette="default")

                # Определяем позицию "противника" для анимации
                if i < len(all_body_types) // 2:
                    opponent_x = fighter_x + 100  # Противник справа
                else:
                    opponent_x = fighter_x - 100  # Противник слева

                preview_fighter.update(fighter_y + 100, self.settings.screen_width, opponent_x)
                preview_fighter.draw(self.screen)

            # Подсказки
            hint = self.small_font.render("Используйте ↑↓←→/WASD или МЫШЬ для навигации, ENTER/ЛКМ для выбора",
                                          True, self.light_gray)
            hint_rect = hint.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height - 50))
            self.screen.blit(hint, hint_rect)

    def draw_character_select_p1(self):
        """Отрисовка экрана выбора персонажа для игрока 1"""
        self.draw_character_select("ИГРОК 1", self.player1_selection,
                                   self.player1_color_selection, is_p1=True)

    def draw_character_select_p2(self):
        """Отрисовка экрана выбора персонажа для игрока 2"""
        self.draw_character_select("ИГРОК 2", self.player2_selection,
                                   self.player2_color_selection, is_p1=False)

    def draw_character_select(self, player_name: str, selection: int, color_selection: int, is_p1: bool = True):
        """Общий метод отрисовки выбора персонажа"""
        self.screen.fill((30, 35, 40))

        # Заголовок
        title = self.title_font.render(f"ВЫБОР ПЕРСОНАЖА - {player_name}", True, (230, 110, 110))
        title_rect = title.get_rect(center=(self.settings.screen_width // 2, 80))
        self.screen.blit(title, title_rect)

        # Режим игры
        mode_text = "БОЙ С БОТОМ" if self.menu_selection == 0 else "ИГРОК ПРОТИВ ИГРОКА"
        subtitle = self.font.render(f"Режим: {mode_text}", True, self.highlight_color)
        subtitle_rect = subtitle.get_rect(center=(self.settings.screen_width // 2, 140))
        self.screen.blit(subtitle, subtitle_rect)

        # Название типа телосложения
        body_type_names = {
            BodyType.ATHLETIC: "АТЛЕТ",
            BodyType.LEAN: "ПРОВОРНЫЙ",
            BodyType.HEAVY: "ТЯЖЕЛОВЕС",
            BodyType.SUMO: "СУМОИСТ",
            BodyType.NINJA: "НИНДЗЯ",
            BodyType.ROBOTIC: "КИБОРГ"
        }

        # ИСПРАВЛЕНО: Используем полный список BodyType вместо среза [:3]
        body_types = list(BodyType)  # Получаем ВСЕ типы телосложения
        selected_type = body_types[selection]
        selected_name = body_type_names[selected_type]

        # Рисуем стрелки для навигации по типам телосложения
        left_arrow_rect = pygame.Rect(self.settings.screen_width // 2 - 200, 400, 50, 50)
        right_arrow_rect = pygame.Rect(self.settings.screen_width // 2 + 150, 400, 50, 50)

        # Проверяем наведение мыши
        mouse_pos = pygame.mouse.get_pos()
        left_hovered = left_arrow_rect.collidepoint(mouse_pos)
        right_hovered = right_arrow_rect.collidepoint(mouse_pos)

        # Левая стрелка
        left_color = self.highlight_color if left_hovered else self.white
        pygame.draw.polygon(self.screen, left_color, [
            (left_arrow_rect.centerx + 10, left_arrow_rect.top + 10),
            (left_arrow_rect.centerx + 10, left_arrow_rect.bottom - 10),
            (left_arrow_rect.left + 10, left_arrow_rect.centery)
        ])
        pygame.draw.rect(self.screen, left_color, left_arrow_rect, 2, border_radius=5)

        # Правая стрелка
        right_color = self.highlight_color if right_hovered else self.white
        pygame.draw.polygon(self.screen, right_color, [
            (right_arrow_rect.centerx - 10, right_arrow_rect.top + 10),
            (right_arrow_rect.centerx - 10, right_arrow_rect.bottom - 10),
            (right_arrow_rect.right - 10, right_arrow_rect.centery)
        ])
        pygame.draw.rect(self.screen, right_color, right_arrow_rect, 2, border_radius=5)

        # Отображение выбранного персонажа
        color_names = ColorPalette.get_palette_names()
        preview_player = Player(
            self.settings.screen_width // 2 - 30,
            350,
            is_left=True,
            body_type=selected_type,
            color_palette=color_names[color_selection]
        )
        preview_player.update(450, self.settings.screen_width,
                              self.settings.screen_width // 2 + 100)
        preview_player.draw(self.screen)

        # Название типа
        name_text = self.font.render(selected_name, True, self.highlight_color)
        name_rect = name_text.get_rect(center=(self.settings.screen_width // 2, 500))
        self.screen.blit(name_text, name_rect)

        # Выбор цвета
        color_title = self.medium_font.render("ЦВЕТОВАЯ СХЕМА:", True, self.white)
        color_title_rect = color_title.get_rect(center=(self.settings.screen_width // 2, 530))
        self.screen.blit(color_title, color_title_rect)

        # Палитра цветов
        color_names = ColorPalette.get_palette_names()
        color_display_names = ["По умолчанию", "Красный", "Синий", "Зеленый", "Фиолетовый", "Золотой"]
        color_values = [ColorPalette.get_palette(name)["body"] for name in color_names]

        color_start_x = self.settings.screen_width // 2 - (len(color_names) * 50) // 2
        for i, (color, name) in enumerate(zip(color_values, color_display_names)):
            color_x = color_start_x + i * 50
            color_rect = pygame.Rect(color_x, 650, 45, 45)

            # Проверяем наведение на цвет
            color_hovered = color_rect.collidepoint(mouse_pos)

            border_color = self.highlight_color if (i == color_selection or color_hovered) else self.light_gray
            border_width = 3 if (i == color_selection or color_hovered) else 1

            pygame.draw.rect(self.screen, color, color_rect, border_radius=10)
            pygame.draw.rect(self.screen, border_color, color_rect, border_width, border_radius=10)

            if i == color_selection or color_hovered:
                name_text = self.small_font.render(name, True, self.highlight_color)
                name_rect = name_text.get_rect(center=(color_rect.centerx, color_rect.bottom + 20))
                self.screen.blit(name_text, name_rect)

        # Кнопка подтверждения
        confirm_y = self.settings.screen_height - 120
        confirm_width = 300
        confirm_height = 50
        confirm_x = self.settings.screen_width // 2 - confirm_width // 2

        confirm_hovered = pygame.Rect(confirm_x, confirm_y, confirm_width, confirm_height).collidepoint(mouse_pos)
        confirm_color = self.highlight_color if confirm_hovered else (70, 75, 80)
        confirm_text_color = self.white if confirm_hovered else self.light_gray

        # Рисуем кнопку подтверждения
        pygame.draw.rect(self.screen, confirm_color,
                         (confirm_x, confirm_y, confirm_width, confirm_height), border_radius=10)
        pygame.draw.rect(self.screen, self.white,
                         (confirm_x, confirm_y, confirm_width, confirm_height), 2, border_radius=10)

        confirm_text = "ПОДТВЕРДИТЬ ВЫБОР" if is_p1 else "НАЧАТЬ БОЙ"
        confirm_text_surface = self.medium_font.render(confirm_text, True, confirm_text_color)
        confirm_text_rect = confirm_text_surface.get_rect(
            center=(self.settings.screen_width // 2, confirm_y + confirm_height // 2))
        self.screen.blit(confirm_text_surface, confirm_text_rect)

        # Кнопка "Назад"
        back_rect = pygame.Rect(20, 20, 100, 40)
        back_hovered = back_rect.collidepoint(mouse_pos)
        back_color = self.highlight_color if back_hovered else (60, 65, 70)

        pygame.draw.rect(self.screen, back_color, back_rect, border_radius=5)
        pygame.draw.rect(self.screen, self.white, back_rect, 2, border_radius=5)

        back_text = self.small_font.render("НАЗАД", True, self.white)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)

        # Статистика персонажа
        stats_y = 570
        stats = {
            BodyType.ATHLETIC: {"HP": 100, "СКОРОСТЬ": 5.5, "УРОН": 10},
            BodyType.LEAN: {"HP": 90, "СКОРОСТЬ": 6.0, "УРОН": 9},
            BodyType.HEAVY: {"HP": 120, "СКОРОСТЬ": 4.5, "УРОН": 12},
            BodyType.SUMO: {"HP": 150, "СКОРОСТЬ": 3.5, "УРОН": 15},
            BodyType.NINJA: {"HP": 85, "СКОРОСТЬ": 6.5, "УРОН": 8},
            BodyType.ROBOTIC: {"HP": 110, "СКОРОСТЬ": 5.0, "УРОН": 11}
        }

        current_stats = stats[selected_type]
        stats_texts = [
            f"Здоровье: {current_stats['HP']}",
            f"Скорость: {current_stats['СКОРОСТЬ']}",
            f"Урон: {current_stats['УРОН']}"
        ]

        for i, stat_text in enumerate(stats_texts):
            stat_surface = self.small_font.render(stat_text, True, self.white)
            stat_rect = stat_surface.get_rect(center=(self.settings.screen_width // 2, stats_y + i * 25))
            self.screen.blit(stat_surface, stat_rect)

        # Подсказки управления
        hint_y = self.settings.screen_height - 40
        hints = [
            "←→/AD - Выбор типа, ↑↓/WS - Выбор цвета",
            "ENTER/ПРОБЕЛ - Подтвердить, ЛКМ - Кликнуть по элементам",
            "ESC или кнопка 'НАЗАД' - Возврат"
        ]

        for i, hint in enumerate(hints):
            hint_text = self.small_font.render(hint, True, self.light_gray)
            hint_rect = hint_text.get_rect(center=(self.settings.screen_width // 2, hint_y + i * 20))
            self.screen.blit(hint_text, hint_rect)

    def draw_winner_screen(self):
        """Отрисовка экрана победителя"""
        overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        win_font = pygame.font.Font(None, 96)
        win_text = win_font.render("ПОБЕДА!", True, (250, 210, 90))
        win_rect = win_text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 - 100))
        self.screen.blit(win_text, win_rect)

        winner_font = pygame.font.Font(None, 120)
        winner_text = winner_font.render(self.winner, True, self.highlight_color)
        winner_rect = winner_text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2))
        self.screen.blit(winner_text, winner_rect)

        stats_font = pygame.font.Font(None, 36)

        # Собираем статистику
        if self.state == GameState.PLAYER_VS_BOT:
            winner_health = self.bot.health if self.winner == "БОТ" else self.player1.health
            loser_health = self.player1.health if self.winner == "БОТ" else self.bot.health
            winner_max = self.bot.max_health if self.winner == "БОТ" else self.player1.max_health
            loser_max = self.player1.max_health if self.winner == "БОТ" else self.bot.max_health
            hits_taken = (loser_max - loser_health) // 10
        else:
            winner_health = self.player2.health if self.winner == "ИГРОК 2" else self.player1.health
            loser_health = self.player1.health if self.winner == "ИГРОК 2" else self.player2.health
            winner_max = self.player2.max_health if self.winner == "ИГРОК 2" else self.player1.max_health
            loser_max = self.player1.max_health if self.winner == "ИГРОК 2" else self.player2.max_health
            hits_taken = (loser_max - loser_health) // 10

        stats_text = f"Оставшееся здоровье: {winner_health}"
        hits_text = f"Получено ударов: {hits_taken}"
        minutes = self.round_time // 3600
        seconds = (self.round_time % 3600) // 60
        time_text = f"Время раунда: {minutes:02d}:{seconds:02d}"

        stats_surface = stats_font.render(stats_text, True, self.white)
        hits_surface = stats_font.render(hits_text, True, self.white)
        time_surface = stats_font.render(time_text, True, self.white)

        stats_rect = stats_surface.get_rect(
            center=(self.settings.screen_width // 2, self.settings.screen_height // 2 + 80))
        hits_rect = hits_surface.get_rect(
            center=(self.settings.screen_width // 2, self.settings.screen_height // 2 + 120))
        time_rect = time_surface.get_rect(
            center=(self.settings.screen_width // 2, self.settings.screen_height // 2 + 160))

        self.screen.blit(stats_surface, stats_rect)
        self.screen.blit(hits_surface, hits_rect)
        self.screen.blit(time_surface, time_rect)

        # Кнопка возврата в меню
        return_y = self.settings.screen_height - 150
        return_width = 350
        return_height = 60
        return_x = self.settings.screen_width // 2 - return_width // 2

        # Проверяем наведение мыши
        mouse_pos = pygame.mouse.get_pos()
        return_rect = pygame.Rect(return_x, return_y, return_width, return_height)
        return_hovered = return_rect.collidepoint(mouse_pos)

        return_color = self.highlight_color if return_hovered else (70, 75, 80)
        return_text_color = self.white if return_hovered else self.light_gray

        # Рисуем кнопку
        pygame.draw.rect(self.screen, return_color, return_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.white, return_rect, 2, border_radius=10)

        return_text = "ВЕРНУТЬСЯ В МЕНЮ"
        return_surface = stats_font.render(return_text, True, return_text_color)
        return_text_rect = return_surface.get_rect(
            center=(self.settings.screen_width // 2, return_y + return_height // 2))
        self.screen.blit(return_surface, return_text_rect)

        # Подсказки
        hints = [
            "Нажмите ESC или кликните по кнопке выше",
            "чтобы вернуться в главное меню"
        ]

        for i, hint in enumerate(hints):
            hint_surface = self.small_font.render(hint, True, self.light_gray)
            hint_rect = hint_surface.get_rect(center=(self.settings.screen_width // 2,
                                                      return_y + return_height + 20 + i * 25))
            self.screen.blit(hint_surface, hint_rect)

    def draw_controls_menu(self):
        """Отрисовка меню правил и управления"""
        self.screen.fill(self.dark_gray)

        # Градиентный фон
        for y in range(self.settings.screen_height):
            color_value = int(25 + (y / self.settings.screen_height) * 20)
            pygame.draw.line(self.screen, (color_value, color_value + 5, color_value + 10),
                             (0, y), (self.settings.screen_width, y))

        title = self.title_font.render("ПРАВИЛА И УПРАВЛЕНИЕ", True, self.highlight_color)
        title_rect = title.get_rect(center=(self.settings.screen_width // 2, 80))
        self.screen.blit(title, title_rect)

        # Создаем две колонки для лучшей организации
        left_column_x = self.settings.screen_width // 4
        right_column_x = 3 * self.settings.screen_width // 4
        y_offset = 150

        # Левый столбец - Основные правила
        rules_title = self.font.render("ОСНОВНЫЕ ПРАВИЛА:", True, self.highlight_color)
        self.screen.blit(rules_title, (left_column_x - rules_title.get_width() // 2, y_offset))

        rules = [
            "• Каждый боец имеет уникальное здоровье (85-150)",
            "• 1 успешный удар = 10 урона",
            "• Блок защищает от удара с правильной стороны",
            "• Разные типы телосложения имеют разные характеристики"
        ]

        for i, rule in enumerate(rules):
            text = self.small_font.render(rule, True, self.white)
            self.screen.blit(text, (left_column_x - text.get_width() // 2, y_offset + 40 + i * 30))

        # Правый столбец - Типы телосложения
        types_title = self.font.render("ТИПЫ ТЕЛОСЛОЖЕНИЯ:", True, self.highlight_color)
        self.screen.blit(types_title, (right_column_x - types_title.get_width() // 2, y_offset))

        types = [
            "• АТЛЕТ: Сбалансированные характеристики",
            "• ПРОВОРНЫЙ: Быстрый но хрупкий",
            "• ТЯЖЕЛОВЕС: Медленный но выносливый",
            "• СУМОИСТ: Очень выносливый, очень медленный",
            "• НИНДЗЯ: Очень быстрый, мало здоровья",
            "• КИБОРГ: Хороший баланс с технологиями"
        ]

        for i, type_text in enumerate(types):
            text = self.small_font.render(type_text, True, self.white)
            self.screen.blit(text, (right_column_x - text.get_width() // 2, y_offset + 40 + i * 30))

        # Управление - размещаем внизу по центру
        controls_y = y_offset + 250

        controls_title = self.font.render("УПРАВЛЕНИЕ:", True, self.highlight_color)
        self.screen.blit(controls_title,
                         (self.settings.screen_width // 2 - controls_title.get_width() // 2, controls_y))

        # Создаем таблицу управления
        player1_controls = [
            ["ИГРОК 1 (ЛЕВЫЙ):", self.highlight_color],
            ["A / ← - Движение влево", self.white],
            ["D / → - Движение вправо", self.white],
            ["ЛЕВЫЙ ALT - Удар", self.white],
            ["W / ↑ - Блок", self.white]
        ]

        player2_controls = [
            ["ИГРОК 2 (ПРАВЫЙ):", self.highlight_color],
            ["← - Движение влево", self.white],
            ["→ - Движение вправо", self.white],
            ["ПРАВЫЙ ALT - Удар", self.white],
            ["↑ - Блок", self.white]
        ]

        # Отображаем таблицу управления
        table_start_y = controls_y + 40
        table_width = 600
        table_start_x = self.settings.screen_width // 2 - table_width // 2

        # Рисуем фоновые панели для таблицы
        for i, (controls, column_x) in enumerate(
                [(player1_controls, table_start_x), (player2_controls, table_start_x + table_width // 2)]):
            panel_width = table_width // 2 - 20
            panel = pygame.Surface((panel_width, 150), pygame.SRCALPHA)
            panel.fill((40, 45, 50, 200))
            self.screen.blit(panel, (column_x, table_start_y))

            # Рисуем рамку вокруг панели
            pygame.draw.rect(self.screen, self.light_gray, (column_x, table_start_y, panel_width, 150), 2,
                             border_radius=5)

            # Отображаем элементы управления в панели
            for j, (control_text, color) in enumerate(controls):
                text = self.small_font.render(control_text, True, color)
                text_x = column_x + panel_width // 2 - text.get_width() // 2
                self.screen.blit(text, (text_x, table_start_y + 10 + j * 30))

        # Подсказка для мыши
        mouse_hint = self.medium_font.render("Можно использовать МЫШЬ для выбора пунктов меню", True, self.info_color)
        mouse_hint_rect = mouse_hint.get_rect(center=(self.settings.screen_width // 2, table_start_y + 180))
        self.screen.blit(mouse_hint, mouse_hint_rect)

        # Кнопка "Назад" внизу с подсветкой при наведении мыши
        back_y = self.settings.screen_height - 100
        back_width = 300
        back_height = 50
        back_x = self.settings.screen_width // 2 - back_width // 2

        # Проверяем наведение мыши на кнопку "Назад"
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = (back_x <= mouse_pos[0] <= back_x + back_width and
                      back_y <= mouse_pos[1] <= back_y + back_height)

        # Цвет кнопки в зависимости от состояния
        button_color = self.highlight_color if is_hovered or self.controls_selection == 0 else (70, 75, 80)
        text_color = self.white if is_hovered or self.controls_selection == 0 else self.light_gray

        # Рисуем кнопку "Назад"
        pygame.draw.rect(self.screen, button_color, (back_x, back_y, back_width, back_height), border_radius=10)
        pygame.draw.rect(self.screen, self.white, (back_x, back_y, back_width, back_height), 2, border_radius=10)

        back_text = self.medium_font.render("ВЕРНУТЬСЯ В МЕНЮ", True, text_color)
        back_rect = back_text.get_rect(center=(self.settings.screen_width // 2, back_y + back_height // 2))
        self.screen.blit(back_text, back_rect)

        # Подсказки внизу экрана
        hint_y = self.settings.screen_height - 40
        hints = [
            "ESC / ЛКМ на кнопке - Назад в меню",
            "WASD / ←↑↓→ / МЫШЬ - Навигация"
        ]

        for i, hint in enumerate(hints):
            hint_text = self.small_font.render(hint, True, self.light_gray)
            hint_rect = hint_text.get_rect(center=(self.settings.screen_width // 2, hint_y + i * 20))
            self.screen.blit(hint_text, hint_rect)

    def draw_settings(self):
        """Отрисовка экрана настроек"""
        self.screen.fill(self.dark_gray)

        # Градиентный фон
        for y in range(self.settings.screen_height):
            color_value = int(25 + (y / self.settings.screen_height) * 20)
            pygame.draw.line(self.screen, (color_value, color_value + 5, color_value + 10),
                             (0, y), (self.settings.screen_width, y))

        title = self.title_font.render("НАСТРОЙКИ", True, self.highlight_color)
        title_rect = title.get_rect(center=(self.settings.screen_width // 2, 80))
        self.screen.blit(title, title_rect)

        settings_items = [
            "Оконный режим",
            "Оконный без рамки",
            "Полноэкранный"
        ]

        settings_items += [f"{w} x {h}" for w, h in self.settings.available_resolutions]

        for i, item in enumerate(settings_items):
            # Проверяем, выбран ли текущий пункт
            is_selected = i == self.settings_selection

            # Определяем цвет и фон
            color = self.highlight_color if is_selected else self.white
            bg_color = (60, 65, 70, 180) if is_selected else (40, 45, 50, 0)

            # Создаем фоновую панель
            item_width = 350
            item_height = 40
            item_x = self.settings.screen_width // 2 - item_width // 2
            item_y = 140 + i * 45

            if is_selected:
                panel = pygame.Surface((item_width, item_height), pygame.SRCALPHA)
                panel.fill(bg_color)
                self.screen.blit(panel, (item_x, item_y))

                # Рисуем рамку вокруг панели
                pygame.draw.rect(self.screen, self.highlight_color,
                                 (item_x, item_y, item_width, item_height), 2, border_radius=5)

            if i == 0 and not self.settings.fullscreen and not self.settings.borderless:
                item = "✓ " + item
            elif i == 1 and self.settings.borderless:
                item = "✓ " + item
            elif i == 2 and self.settings.fullscreen:
                item = "✓ " + item
            elif i >= 3:
                w, h = self.settings.available_resolutions[i - 3]
                if (w, h) == self.settings.current_resolution:
                    item = "✓ " + item

            text = self.font.render(item, True, color)
            text_rect = text.get_rect(center=(self.settings.screen_width // 2, 150 + i * 45))
            self.screen.blit(text, text_rect)

        # Подсказки внизу
        hints = [
            "ESC - Назад, ↑↓←→/WASD - Навигация, ENTER/ЛКМ - Выбор",
            "Текущее разрешение: {}x{}".format(*self.settings.current_resolution)
        ]

        for i, hint in enumerate(hints):
            hint_text = self.small_font.render(hint, True, self.light_gray)
            hint_rect = hint_text.get_rect(center=(self.settings.screen_width // 2,
                                                   self.settings.screen_height - 60 + i * 25))
            self.screen.blit(hint_text, hint_rect)

    def draw_game(self):
        """Отрисовка игрового экрана"""
        # Отображаем фон
        bg_scaled = pygame.transform.scale(self.background_image,
                                          (self.settings.screen_width,
                                           self.settings.screen_height))
        self.screen.blit(bg_scaled, (0, 0))

        # Земля с текстурой
        ground_height = 120
        ground_y = self.settings.screen_height - ground_height

        # Текстура земли
        for y in range(ground_y, self.settings.screen_height, 4):
            line_color = (40 + (y - ground_y)//2, 45 + (y - ground_y)//2, 50 + (y - ground_y)//2)
            pygame.draw.line(self.screen, line_color, (0, y), (self.settings.screen_width, y))

        # Трава
        grass_color = (45, 65, 45)
        for x in range(0, self.settings.screen_width, 10):
            grass_height = random.randint(5, 15)
            grass_points = [
                (x, ground_y),
                (x + 3, ground_y - grass_height),
                (x + 7, ground_y - grass_height//2),
                (x + 10, ground_y)
            ]
            pygame.draw.polygon(self.screen, grass_color, grass_points)

        # Центральная линия арены
        center_x = self.settings.screen_width // 2
        line_length = 200
        pygame.draw.line(self.screen, (85, 90, 95, 150),
                        (center_x, ground_y - line_length),
                        (center_x, ground_y), 3)

        # Эффекты попаданий
        self.draw_hit_effects()

        # Отрисовка игроков
        if self.state == GameState.PLAYER_VS_BOT:
            self.player1.draw(self.screen)
            self.bot.draw(self.screen)
            self.draw_game_info("ИГРОК 1", self.player1.health,
                               "БОТ", self.bot.health)

        elif self.state == GameState.PLAYER_VS_PLAYER:
            self.player1.draw(self.screen)
            self.player2.draw(self.screen)
            self.draw_game_info("ИГРОК 1", self.player1.health,
                               "ИГРОК 2", self.player2.health)

        # Отображение победителя
        if self.winner:
            self.draw_winner_screen()

            # Подсказка для выхода
            hint_text = "ESC - Выход в меню"
            if self.battle_finished:
                hint_text = "ESC - Вернуться в меню"

            hint = self.small_font.render(hint_text, True, self.white)
            self.screen.blit(hint, (self.settings.screen_width // 2 - 70, self.settings.screen_height - 40))

    def draw_hit_effects(self):
        """Отрисовка эффектов попаданий"""
        for effect in self.hit_effects:
            current_size = effect['size'] * (effect['timer'] / 15)
            alpha = int(255 * (effect['timer'] / 15))

            effect_surface = pygame.Surface((int(current_size * 2), int(current_size * 2)), pygame.SRCALPHA)

            # Внешнее кольцо
            pygame.draw.circle(effect_surface, (*effect['color'][:3], alpha//2),
                             (int(current_size), int(current_size)), int(current_size))

            # Внутреннее кольцо
            inner_radius = current_size * 0.6
            inner_color = (255, 255, 255, alpha)
            pygame.draw.circle(effect_surface, inner_color,
                             (int(current_size), int(current_size)), int(inner_radius))

            self.screen.blit(effect_surface,
                           (effect['x'] - int(current_size), effect['y'] - int(current_size)))

    def draw_game_info(self, p1_name: str, p1_health: int,
                      p2_name: str, p2_health: int):
        """Отрисовка игровой информации вверху экрана"""
        # Верхняя панель
        top_panel = pygame.Surface((self.settings.screen_width, 80), pygame.SRCALPHA)
        top_panel.fill((20, 25, 30, 220))
        self.screen.blit(top_panel, (0, 0))

        # Время раунда
        minutes = self.round_time // 3600
        seconds = (self.round_time % 3600) // 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        time_surface = self.font.render(time_text, True, (230, 190, 90))
        time_rect = time_surface.get_rect(center=(self.settings.screen_width // 2, 40))
        self.screen.blit(time_surface, time_rect)

        # Здоровье игрока 1
        p1_max_health = self.player1.max_health if self.player1 else 100
        p1_health_percent = p1_health / p1_max_health
        p1_health_width = 300 * p1_health_percent

        p1_health_color = (70, 210, 90) if p1_health_percent > 0.5 else (230, 210, 70) if p1_health_percent > 0.25 else (230, 70, 70)

        pygame.draw.rect(self.screen, (40, 45, 50), (20, 20, 304, 34), border_radius=6)
        pygame.draw.rect(self.screen, p1_health_color, (22, 22, p1_health_width, 30), border_radius=5)
        pygame.draw.rect(self.screen, (190, 195, 200), (20, 20, 304, 34), 2, border_radius=6)

        p1_text = f"{p1_name}: {p1_health}/{p1_max_health}"
        p1_surface = self.medium_font.render(p1_text, True, self.white)
        self.screen.blit(p1_surface, (25, 25))

        # Здоровье игрока 2/бота
        if self.state == GameState.PLAYER_VS_BOT:
            p2_max_health = self.bot.max_health
        else:
            p2_max_health = self.player2.max_health if self.player2 else 100

        p2_health_percent = p2_health / p2_max_health
        p2_health_width = 300 * p2_health_percent

        p2_health_color = (70, 210, 90) if p2_health_percent > 0.5 else (230, 210, 70) if p2_health_percent > 0.25 else (230, 70, 70)

        p2_x = self.settings.screen_width - 324
        pygame.draw.rect(self.screen, (40, 45, 50), (p2_x, 20, 304, 34), border_radius=6)
        pygame.draw.rect(self.screen, p2_health_color, (p2_x + 2, 22, p2_health_width, 30), border_radius=5)
        pygame.draw.rect(self.screen, (190, 195, 200), (p2_x, 20, 304, 34), 2, border_radius=6)

        p2_text = f"{p2_name}: {p2_health}/{p2_max_health}"
        p2_surface = self.medium_font.render(p2_text, True, self.white)
        p2_text_x = self.settings.screen_width - p2_surface.get_width() - 25
        self.screen.blit(p2_surface, (p2_text_x, 25))

        # Информация об ударах до победы
        hits_to_win_p1 = max(0, (p1_health + 9) // 10)
        hits_to_win_p2 = max(0, (p2_health + 9) // 10)

        hits_text = f"Ударов до победы: {hits_to_win_p1} - {hits_to_win_p2}"
        hits_surface = self.small_font.render(hits_text, True, (250, 230, 110))
        hits_rect = hits_surface.get_rect(center=(self.settings.screen_width // 2, 70))
        self.screen.blit(hits_surface, hits_rect)

    def draw_winner_screen(self):
        """Отрисовка экрана победителя"""
        overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        win_font = pygame.font.Font(None, 96)
        win_text = win_font.render("ПОБЕДА!", True, (250, 210, 90))
        win_rect = win_text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 - 100))
        self.screen.blit(win_text, win_rect)

        winner_font = pygame.font.Font(None, 120)
        winner_text = winner_font.render(self.winner, True, self.highlight_color)
        winner_rect = winner_text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2))
        self.screen.blit(winner_text, winner_rect)

        stats_font = pygame.font.Font(None, 36)

        if self.state == GameState.PLAYER_VS_BOT:
            winner_health = self.bot.health if self.winner == "БОТ" else self.player1.health
            loser_health = self.player1.health if self.winner == "БОТ" else self.bot.health
            hits_taken = (self.bot.max_health - loser_health) // 10 if self.winner == "БОТ" else (self.player1.max_health - loser_health) // 10
        else:
            winner_health = self.player2.health if self.winner == "ИГРОК 2" else self.player1.health
            loser_health = self.player1.health if self.winner == "ИГРОК 2" else self.player2.health
            winner_max = self.player2.max_health if self.winner == "ИГРОК 2" else self.player1.max_health
            loser_max = self.player1.max_health if self.winner == "ИГРОК 2" else self.player2.max_health
            hits_taken = (loser_max - loser_health) // 10

        stats_text = f"Оставшееся здоровье: {winner_health}"
        hits_text = f"Нанесено ударов: {hits_taken}"
        time_text = f"Время раунда: {self.round_time // 60} секунд"

        stats_surface = stats_font.render(stats_text, True, self.white)
        hits_surface = stats_font.render(hits_text, True, self.white)
        time_surface = stats_font.render(time_text, True, self.white)

        stats_rect = stats_surface.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 + 80))
        hits_rect = hits_surface.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 + 120))
        time_rect = time_surface.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 + 160))

        self.screen.blit(stats_surface, stats_rect)
        self.screen.blit(hits_surface, hits_rect)
        self.screen.blit(time_surface, time_rect)

        continue_text = stats_font.render("Нажмите ESC для возврата в меню", True, self.light_gray)
        continue_rect = continue_text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height - 100))
        self.screen.blit(continue_text, continue_rect)

    def draw(self):
        """Основной метод отрисовки"""
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.CHARACTER_SELECT_P1:
            self.draw_character_select_p1()
        elif self.state == GameState.CHARACTER_SELECT_P2:
            self.draw_character_select_p2()
        elif self.state == GameState.SETTINGS:
            self.draw_settings()
        elif self.state == GameState.CONTROLS:
            self.draw_controls_menu()
        elif self.state in [GameState.PLAYER_VS_PLAYER, GameState.PLAYER_VS_BOT]:
            self.draw_game()

        pygame.display.flip()

    def run(self):
        """Основной игровой цикл"""
        # Показываем курсор мыши
        pygame.mouse.set_visible(True)

        while self.state != GameState.EXIT:
            self.handle_events()

            if self.state in [GameState.PLAYER_VS_PLAYER, GameState.PLAYER_VS_BOT]:
                self.update_game()

            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

def main():
    """Точка входа в программу"""
    print("=" * 65)
    print("          ДУЭЛЯНТЫ - АРЕНА СИЛУЭТОВ")
    print("=" * 65)
    print("⚔️  6 Уникальных типов телосложения с разными характеристиками")
    print("❤️  Здоровье варьируется от 85 до 150")
    print("⚡ Скорость и урон сбалансированы")
    print("🎨 6 Разных цветовых схем")
    print("🏔️  Атмосферный фон с горами")
    print("🤖 Интеллектуальный ИИ-противник")
    print("👥 Отдельный выбор персонажей для каждого игрока")
    print("=" * 65)
    print("Выберите тип телосложения и цвет для каждого бойца перед боем!")
    print("=" * 65)

    settings = Settings()
    game = Game(settings)
    game.run()

if __name__ == "__main__":
    main()