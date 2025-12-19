"""
Классы Player и Bot
"""

import pygame
import random
from typing import Optional, Tuple
from dataclasses import dataclass

try:
    from enums import BodyType, AnimationState
    from colors import ColorPalette
except ImportError:
    # Локальные определения для совместимости
    from enum import Enum

    class BodyType(Enum):
        ATHLETIC = "athletic"
        LEAN = "lean"
        HEAVY = "heavy"
        SUMO = "sumo"
        NINJA = "ninja"
        ROBOTIC = "robotic"

    class AnimationState(Enum):
        IDLE = "idle"
        WALKING = "walking"
        ATTACKING = "attacking"
        BLOCKING = "blocking"
        HURT = "hurt"

    class ColorPalette:
        @staticmethod
        def get_palette(name: str) -> dict:
            return {"body": (30, 30, 40), "highlight": (60, 60, 80),
                    "attack": (220, 60, 60), "block": (60, 120, 220)}

@dataclass
class BodyParameters:
    """Параметры тела персонажа"""
    width: int
    height: int
    speed: float
    health: int
    max_health: int
    head_radius: int
    shoulder_width: int
    waist_width: int
    arm_thickness: int
    leg_thickness: int
    arm_length: int
    damage: int = 10

class BodyTypeParameters:
    """Параметры для каждого типа телосложения"""

    PARAMETERS = {
        BodyType.ATHLETIC: BodyParameters(
            width=52, height=130, speed=5.5, health=100, max_health=100,
            head_radius=18, shoulder_width=45, waist_width=40,
            arm_thickness=16, leg_thickness=18, arm_length=55,
            damage=10
        ),
        BodyType.LEAN: BodyParameters(
            width=42, height=140, speed=6.0, health=90, max_health=90,
            head_radius=16, shoulder_width=35, waist_width=32,
            arm_thickness=12, leg_thickness=14, arm_length=60,
            damage=9
        ),
        BodyType.HEAVY: BodyParameters(
            width=65, height=125, speed=4.5, health=120, max_health=120,
            head_radius=22, shoulder_width=55, waist_width=50,
            arm_thickness=20, leg_thickness=22, arm_length=50,
            damage=12
        ),
        BodyType.SUMO: BodyParameters(
            width=75, height=115, speed=3.5, health=150, max_health=150,
            head_radius=25, shoulder_width=60, waist_width=70,
            arm_thickness=18, leg_thickness=20, arm_length=45,
            damage=15
        ),
        BodyType.NINJA: BodyParameters(
            width=45, height=135, speed=6.5, health=85, max_health=85,
            head_radius=17, shoulder_width=38, waist_width=35,
            arm_thickness=13, leg_thickness=15, arm_length=65,
            damage=8
        ),
        BodyType.ROBOTIC: BodyParameters(
            width=58, height=145, speed=5.0, health=110, max_health=110,
            head_radius=20, shoulder_width=50, waist_width=45,
            arm_thickness=17, leg_thickness=19, arm_length=58,
            damage=11
        )
    }

    @staticmethod
    def get_parameters(body_type: BodyType) -> BodyParameters:
        """Получение параметров для типа телосложения"""
        return BodyTypeParameters.PARAMETERS.get(body_type,
            BodyTypeParameters.PARAMETERS[BodyType.ATHLETIC])

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

        # Загружаем параметры тела
        self.params = BodyTypeParameters.get_parameters(body_type)

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
        self.animation_state = AnimationState.IDLE

        # Позиции частей тела
        self.body_parts = {}
        self.arm_positions = {
            "left_upper": {"base_x": 0, "base_y": 0, "current_x": 0, "current_y": 0},
            "left_lower": {"base_x": 0, "base_y": 0, "current_x": 0, "current_y": 0},
            "right_upper": {"base_x": 0, "base_y": 0, "current_x": 0, "current_y": 0},
            "right_lower": {"base_x": 0, "base_y": 0, "current_x": 0, "current_y": 0}
        }

        # Здоровье
        self.health = self.params.health
        self.max_health = self.params.max_health

        # Обновляем части тела
        self.update_body_parts()

    def set_body_parameters(self):
        """Установка параметров тела в зависимости от типа"""
        # Этот метод теперь использует BodyTypeParameters
        pass

    def determine_attack_hand(self, opponent_x: float):
        """Определяет какой рукой бить в зависимости от позиции противника"""
        if opponent_x < self.x + self.params.width // 2:
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
        self.animation_state = AnimationState.WALKING

    def move_right(self):
        """Движение вправо"""
        self.moving_right = True
        self.moving_left = False
        self.animation_state = AnimationState.WALKING

    def stop_moving(self):
        """Остановка движения"""
        self.moving_left = False
        self.moving_right = False
        if not self.attacking and not self.blocking:
            self.animation_state = AnimationState.IDLE

    def attack(self, opponent_x: float):
        """Начало атаки с автоматическим выбором руки"""
        if self.attack_cooldown <= 0:
            self.determine_attack_hand(opponent_x)
            self.attacking = True
            self.attack_animation = 15
            self.attack_cooldown = 30
            self.already_hit_in_current_attack = False
            self.animation_state = AnimationState.ATTACKING

    def block(self, opponent_x: float):
        """Установка блока с автоматическим выбором стороны"""
        if self.block_cooldown <= 0:
            if opponent_x < self.x + self.params.width // 2:
                self.block_direction = "left"
            else:
                self.block_direction = "right"
            self.blocking = True
            self.block_cooldown = 40
            self.animation_state = AnimationState.BLOCKING

    def update_body_parts(self):
        """Обновление позиций всех частей тела с анимацией рук"""
        center_x = self.x + self.params.width // 2
        base_y = self.y

        # Очищаем предыдущие части тела
        self.body_parts = {}

        # Голова
        head_width = self.params.head_radius * 1.8
        head_height = self.params.head_radius * 2.2
        self.body_parts["head"] = {
            "type": "ellipse",
            "rect": pygame.Rect(center_x - head_width//2, base_y - head_height + 5,
                              head_width, head_height),
            "color": self.color_palette["body"]
        }

        # Шея
        neck_height = 15
        neck_width = self.params.head_radius
        self.body_parts["neck"] = {
            "type": "rect",
            "rect": pygame.Rect(center_x - neck_width//2, base_y - neck_height,
                              neck_width, neck_height),
            "color": self.color_palette["body"]
        }

        # Торс
        torso_height = self.params.height * 0.45
        torso_y = base_y
        torso_top_width = self.params.shoulder_width * 0.9
        torso_bottom_width = self.params.waist_width

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
        pelvis_height = self.params.height * 0.25
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
        attack_strength = 1.0 - abs(attack_progress - 0.5) * 2

        # Позиции плеч
        left_shoulder_x = center_x - self.params.shoulder_width // 2 + 5
        right_shoulder_x = center_x + self.params.shoulder_width // 2 - 5
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
            self.arm_positions["left_lower"]["current_y"] = shoulder_y + self.params.arm_length * 0.6

            self.arm_positions["right_upper"]["current_x"] = right_shoulder_x
            self.arm_positions["right_upper"]["current_y"] = shoulder_y
            self.arm_positions["right_lower"]["current_x"] = right_shoulder_x
            self.arm_positions["right_lower"]["current_y"] = shoulder_y + self.params.arm_length * 0.6

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
                (self.arm_positions["left_upper"]["base_x"] - self.params.arm_thickness,
                 self.arm_positions["left_upper"]["base_y"]),
                (self.arm_positions["left_lower"]["current_x"] - self.params.arm_thickness * 0.8,
                 self.arm_positions["left_lower"]["current_y"]),
                (self.arm_positions["left_lower"]["current_x"], self.arm_positions["left_lower"]["current_y"])
            ],
            "color": self.color_palette["body"]
        }

        # Левая рука (нижняя часть)
        left_lower_arm = {
            "type": "polygon",
            "points": [
                (self.arm_positions["left_lower"]["current_x"], self.arm_positions["left_lower"]["current_y"]),
                (self.arm_positions["left_lower"]["current_x"] - self.params.arm_thickness * 0.8,
                 self.arm_positions["left_lower"]["current_y"]),
                (self.arm_positions["left_lower"]["current_x"] - self.params.arm_thickness * 0.6,
                 self.arm_positions["left_lower"]["current_y"] + self.params.arm_length * 0.4),
                (self.arm_positions["left_lower"]["current_x"],
                 self.arm_positions["left_lower"]["current_y"] + self.params.arm_length * 0.4)
            ],
            "color": self.color_palette["body"]
        }

        # Правая рука (верхняя часть)
        right_upper_arm = {
            "type": "polygon",
            "points": [
                (self.arm_positions["right_upper"]["base_x"], self.arm_positions["right_upper"]["base_y"]),
                (self.arm_positions["right_upper"]["base_x"] + self.params.arm_thickness,
                 self.arm_positions["right_upper"]["base_y"]),
                (self.arm_positions["right_lower"]["current_x"] + self.params.arm_thickness * 0.8,
                 self.arm_positions["right_lower"]["current_y"]),
                (self.arm_positions["right_lower"]["current_x"], self.arm_positions["right_lower"]["current_y"])
            ],
            "color": self.color_palette["body"]
        }

        # Правая рука (нижняя часть)
        right_lower_arm = {
            "type": "polygon",
            "points": [
                (self.arm_positions["right_lower"]["current_x"], self.arm_positions["right_lower"]["current_y"]),
                (self.arm_positions["right_lower"]["current_x"] + self.params.arm_thickness * 0.8,
                 self.arm_positions["right_lower"]["current_y"]),
                (self.arm_positions["right_lower"]["current_x"] + self.params.arm_thickness * 0.6,
                 self.arm_positions["right_lower"]["current_y"] + self.params.arm_length * 0.4),
                (self.arm_positions["right_lower"]["current_x"],
                 self.arm_positions["right_lower"]["current_y"] + self.params.arm_length * 0.4)
            ],
            "color": self.color_palette["body"]
        }

        self.body_parts["left_upper_arm"] = left_upper_arm
        self.body_parts["left_lower_arm"] = left_lower_arm
        self.body_parts["right_upper_arm"] = right_upper_arm
        self.body_parts["right_lower_arm"] = right_lower_arm

        # Кисти рук
        hand_size = self.params.arm_thickness * 0.8
        if self.attacking:
            # Атакующая рука - сжатый кулак
            if self.attacking_with_right:
                right_hand = {
                    "type": "ellipse",
                    "rect": pygame.Rect(
                        self.arm_positions["right_lower"]["current_x"] - hand_size//2,
                        self.arm_positions["right_lower"]["current_y"] + self.params.arm_length * 0.4 - hand_size//2,
                        hand_size * 1.2,
                        hand_size * 1.2
                    ),
                    "color": self.color_palette["attack"]
                }
                left_hand = {
                    "type": "ellipse",
                    "rect": pygame.Rect(
                        self.arm_positions["left_lower"]["current_x"] - hand_size//2,
                        self.arm_positions["left_lower"]["current_y"] + self.params.arm_length * 0.4 - hand_size//2,
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
                        self.arm_positions["left_lower"]["current_y"] + self.params.arm_length * 0.4 - hand_size//2,
                        hand_size * 1.2,
                        hand_size * 1.2
                    ),
                    "color": self.color_palette["attack"]
                }
                right_hand = {
                    "type": "ellipse",
                    "rect": pygame.Rect(
                        self.arm_positions["right_lower"]["current_x"] - hand_size//2,
                        self.arm_positions["right_lower"]["current_y"] + self.params.arm_length * 0.4 - hand_size//2,
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
                    self.arm_positions["left_lower"]["current_y"] + self.params.arm_length * 0.4 - hand_size//2,
                    hand_size,
                    hand_size
                ),
                "color": self.color_palette["body"]
            }
            right_hand = {
                "type": "ellipse",
                "rect": pygame.Rect(
                    self.arm_positions["right_lower"]["current_x"] - hand_size//2,
                    self.arm_positions["right_lower"]["current_y"] + self.params.arm_length * 0.4 - hand_size//2,
                    hand_size,
                    hand_size
                ),
                "color": self.color_palette["body"]
            }

        self.body_parts["left_hand"] = left_hand
        self.body_parts["right_hand"] = right_hand

        # Ноги
        leg_length = self.params.height * 0.5
        leg_start_y = pelvis_y + pelvis_height

        # Левая нога (верхняя часть)
        left_upper_leg = {
            "type": "polygon",
            "points": [
                (center_x - 10, leg_start_y),
                (center_x - 10 - self.params.leg_thickness, leg_start_y),
                (center_x - 15 - self.params.leg_thickness, leg_start_y + leg_length//2),
                (center_x - 15, leg_start_y + leg_length//2)
            ],
            "color": self.color_palette["body"]
        }

        # Левая нога (нижняя часть)
        left_lower_leg = {
            "type": "polygon",
            "points": [
                (center_x - 15, leg_start_y + leg_length//2),
                (center_x - 15 - self.params.leg_thickness, leg_start_y + leg_length//2),
                (center_x - 12 - self.params.leg_thickness, leg_start_y + leg_length),
                (center_x - 12, leg_start_y + leg_length)
            ],
            "color": self.color_palette["body"]
        }

        # Правая нога (верхняя часть)
        right_upper_leg = {
            "type": "polygon",
            "points": [
                (center_x + 10, leg_start_y),
                (center_x + 10 + self.params.leg_thickness, leg_start_y),
                (center_x + 15 + self.params.leg_thickness, leg_start_y + leg_length//2),
                (center_x + 15, leg_start_y + leg_length//2)
            ],
            "color": self.color_palette["body"]
        }

        # Правая нога (нижняя часть)
        right_lower_leg = {
            "type": "polygon",
            "points": [
                (center_x + 15, leg_start_y + leg_length//2),
                (center_x + 15 + self.params.leg_thickness, leg_start_y + leg_length//2),
                (center_x + 12 + self.params.leg_thickness, leg_start_y + leg_length),
                (center_x + 12, leg_start_y + leg_length)
            ],
            "color": self.color_palette["body"]
        }

        self.body_parts["left_upper_leg"] = left_upper_leg
        self.body_parts["left_lower_leg"] = left_lower_leg
        self.body_parts["right_upper_leg"] = right_upper_leg
        self.body_parts["right_lower_leg"] = right_lower_leg

        # Ступни
        foot_length = self.params.leg_thickness * 2
        foot_height = self.params.leg_thickness * 0.7

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
                "rect": pygame.Rect(center_x - mawashi_width//2, base_y + 80,
                                  mawashi_width, mawashi_height),
                "color": (180, 60, 60)  # Красный пояс
            }
            self.body_parts["mawashi"] = mawashi

            # Прическа сумоиста
            topknot = {
                "type": "ellipse",
                "rect": pygame.Rect(center_x - 10, base_y - self.params.head_radius*2.2 - 5,
                                  20, 25),
                "color": self.color_palette["body"]
            }
            self.body_parts["topknot"] = topknot

        elif self.body_type == BodyType.NINJA:
            # Повязка ниндзя
            headband_width = 40
            headband_height = 8
            headband = {
                "type": "rect",
                "rect": pygame.Rect(center_x - headband_width//2,
                                  base_y - self.params.head_radius*1.8,
                                  headband_width, headband_height),
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
                "points": [(center_x, base_y - self.params.head_radius*2.2),
                          (center_x, base_y - self.params.head_radius*2.2 - 20)],
                "color": self.color_palette["highlight"],
                "width": 3
            }
            self.body_parts["antenna"] = antenna

    def update(self, ground_y: int, screen_width: int, opponent_x: Optional[float] = None):
        """Обновление состояния игрока"""
        if self.moving_left and self.x > 0:
            self.x -= self.params.speed
        if self.moving_right and self.x < screen_width - self.params.width:
            self.x += self.params.speed

        self.y = ground_y - self.params.height

        if self.attacking and self.attack_animation > 0:
            self.attack_animation -= 1
            if self.attack_animation <= 0:
                self.attacking = False
                self.already_hit_in_current_attack = False
                if not self.moving_left and not self.moving_right:
                    self.animation_state = AnimationState.IDLE

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.block_cooldown > 0:
            self.block_cooldown -= 1
            if self.block_cooldown <= 0:
                self.blocking = False
                if not self.moving_left and not self.moving_right and not self.attacking:
                    self.animation_state = AnimationState.IDLE

        if opponent_x is not None and self.blocking:
            if opponent_x < self.x + self.params.width // 2:
                self.block_direction = "left"
            else:
                self.block_direction = "right"

        self.update_body_parts()

    def take_damage(self, damage: int = None) -> bool:
        """Получение урона"""
        if not self.blocking:
            if damage is None:
                damage = self.params.damage
            self.health = max(0, self.health - damage)
            self.animation_state = AnimationState.HURT
            return True
        return False

    def heal(self, amount: int):
        """Лечение игрока"""
        self.health = min(self.max_health, self.health + amount)

    def get_rect(self) -> pygame.Rect:
        """Получение прямоугольника для коллизий"""
        return pygame.Rect(
            self.x,
            self.y - self.params.head_radius * 2,
            self.params.width,
            self.params.height + self.params.head_radius * 2
        )

    def get_attack_rect(self) -> pygame.Rect:
        """Получение прямоугольника для атаки"""
        if not self.attacking:
            return pygame.Rect(0, 0, 0, 0)

        if self.attacking_with_right:
            # Прямоугольник для правой атакующей руки
            hand_x = self.arm_positions["right_lower"]["current_x"]
            hand_y = self.arm_positions["right_lower"]["current_y"] + self.params.arm_length * 0.4

            return pygame.Rect(
                hand_x - 15,
                hand_y - 15,
                30,
                30
            )
        else:
            # Прямоугольник для левой атакующей руки
            hand_x = self.arm_positions["left_lower"]["current_x"]
            hand_y = self.arm_positions["left_lower"]["current_y"] + self.params.arm_length * 0.4

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

        center_x = self.x + self.params.width // 2
        block_width = 25
        block_height = 80

        if self.block_direction == "left":
            return pygame.Rect(
                center_x - self.params.shoulder_width//2 - block_width,
                self.y + 25,
                block_width,
                block_height
            )
        else:
            return pygame.Rect(
                center_x + self.params.shoulder_width//2,
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

    def get_stats(self) -> dict:
        """Получение статистики персонажа"""
        return {
            "health": self.health,
            "max_health": self.max_health,
            "speed": self.params.speed,
            "damage": self.params.damage,
            "body_type": self.body_type.value,
            "color_palette": self.color_palette_name
        }

class Bot(Player):
    """Класс бота, наследуется от игрока"""

    def __init__(self, x: int, y: int, is_left: bool = True,
                 body_type: BodyType = BodyType.ATHLETIC,
                 color_palette: str = "default",
                 difficulty: str = "medium"):
        super().__init__(x, y, is_left, body_type, color_palette)

        self.decision_cooldown = 0
        self.difficulty = difficulty
        self.last_action = None

        # Настройки в зависимости от сложности
        self.set_difficulty(difficulty)

    def set_difficulty(self, difficulty: str):
        """Установка уровня сложности"""
        difficulty_settings = {
            "easy": {"aggression": 0.4, "caution": 0.7, "reaction_time": 40},
            "medium": {"aggression": 0.6, "caution": 0.4, "reaction_time": 25},
            "hard": {"aggression": 0.8, "caution": 0.2, "reaction_time": 15},
            "insane": {"aggression": 0.9, "caution": 0.1, "reaction_time": 8}
        }

        settings = difficulty_settings.get(difficulty, difficulty_settings["medium"])
        self.aggression = settings["aggression"]
        self.caution = settings["caution"]
        self.reaction_time = settings["reaction_time"]

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

        # Стратегия в зависимости от расстояния
        if distance < 80:  # Очень близко
            if random.random() < self.aggression * 1.2:
                if random.random() < 0.8:
                    self.attack(player.x)
                    self.last_action = "attack"
                else:
                    self.block(player.x)
                    self.last_action = "block"
            elif random.random() < self.caution * 0.8:
                if player_is_left:
                    self.move_left()
                else:
                    self.move_right()
                self.last_action = "retreat"
            else:
                self.last_action = "wait"

        elif distance < 150:  # Ближняя дистанция
            if random.random() < self.aggression:
                if random.random() < 0.6:
                    self.attack(player.x)
                    self.last_action = "attack"
                else:
                    if player_is_left:
                        self.move_left()
                    else:
                        self.move_right()
                    self.last_action = "advance"
            elif random.random() < self.caution:
                self.block(player.x)
                self.last_action = "block"
            else:
                if player_is_left:
                    self.move_left()
                else:
                    self.move_right()
                self.last_action = "positioning"

        elif distance < 250:  # Средняя дистанция
            if random.random() < 0.6:
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

        else:  # Дальняя дистанция
            if random.random() < 0.8:
                if player_is_left:
                    self.move_left()
                else:
                    self.move_right()
                self.last_action = "advance"
            else:
                self.last_action = "wait"

        # Адаптация стратегии в зависимости от здоровья
        health_percentage = self.health / self.max_health

        if health_percentage < 0.3:  # Мало здоровья
            self.aggression = min(0.95, self.aggression + 0.2)
            self.caution = max(0.05, self.caution - 0.1)
        elif health_percentage < 0.6:  # Среднее здоровье
            self.aggression = min(0.8, self.aggression + 0.1)
            self.caution = max(0.2, self.caution - 0.05)

        # Адаптация на основе действий игрока
        if hasattr(player, 'last_action'):
            if player.last_action == "attack":
                if random.random() < 0.7:
                    self.block(player.x)
                    self.last_action = "counter_block"
            elif player.last_action == "block":
                if random.random() < 0.6:
                    if player_is_left:
                        self.move_right()
                    else:
                        self.move_left()
                    self.last_action = "flank"

        self.decision_cooldown = random.randint(
            max(5, self.reaction_time - 5),
            min(30, self.reaction_time + 5)
        )

    def update(self, ground_y: int, screen_width: int, opponent_x: Optional[float] = None):
        """Обновление бота с дополнительной логикой"""
        super().update(ground_y, screen_width, opponent_x)

        # Бот может автоматически блокировать при низком здоровье
        if self.health < self.max_health * 0.3 and random.random() < 0.3:
            if opponent_x is not None:
                self.block(opponent_x)

    def __str__(self) -> str:
        """Строковое представление бота"""
        return f"Bot(difficulty={self.difficulty}, health={self.health}, pos=({self.x}, {self.y}))"