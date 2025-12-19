"""
Модуль выбора персонажа
"""

import pygame
from typing import List, Tuple, Optional
from enum import Enum

try:
    from enums import BodyType
    from colors import ColorPalette
    from player import Player
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

    class ColorPalette:
        @staticmethod
        def get_palette(name: str) -> dict:
            return {"body": (30, 30, 40)}

        @staticmethod
        def get_palette_names() -> list:
            return ["default", "red", "blue", "green", "purple", "gold"]

        @staticmethod
        def get_display_name(palette_name: str) -> str:
            names = {
                "default": "По умолчанию",
                "red": "Красный",
                "blue": "Синий",
                "green": "Зеленый",
                "purple": "Фиолетовый",
                "gold": "Золотой"
            }
            return names.get(palette_name, "Неизвестно")

    class Player:
        def __init__(self, x, y, is_left=True, body_type=None, color_palette="default"):
            self.x = x
            self.y = y
            self.width = 50
            self.height = 130
            self.color_palette = ColorPalette.get_palette(color_palette)

class CharacterSelector:
    """Класс для выбора персонажа"""

    def __init__(self, screen_width: int, screen_height: int, player_name: str):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player_name = player_name

        # Выбор типа телосложения
        self.body_types = list(BodyType)
        self.selected_body_type_index = 0
        self.selected_body_type = self.body_types[0]

        # Выбор цвета
        self.color_palettes = ColorPalette.get_palette_names()
        self.selected_color_index = 0
        self.selected_color = self.color_palettes[0]

        # Предпросмотр персонажа
        self.preview_player = None
        self.create_preview_player()

        # Шрифты
        self.title_font = pygame.font.Font(None, 72)
        self.section_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)

        # Цвета
        self.colors = {
            'title': (230, 110, 110),
            'highlight': (210, 90, 90),
            'text': (230, 235, 240),
            'hint': (120, 125, 130),
            'arrow_normal': (230, 235, 240),
            'arrow_hover': (210, 90, 90),
            'color_border': (190, 195, 200),
            'color_border_selected': (210, 90, 90),
            'button_normal': (70, 75, 80),
            'button_hover': (90, 95, 100),
            'button_text': (230, 235, 240)
        }

        # Кнопки
        self.confirm_button = None
        self.back_button = None
        self.create_buttons()

        # Названия типов телосложения
        self.body_type_names = {
            BodyType.ATHLETIC: "АТЛЕТ",
            BodyType.LEAN: "ПРОВОРНЫЙ",
            BodyType.HEAVY: "ТЯЖЕЛОВЕС",
            BodyType.SUMO: "СУМОИСТ",
            BodyType.NINJA: "НИНДЗЯ",
            BodyType.ROBOTIC: "КИБОРГ"
        }

        # Статистика типов
        self.body_type_stats = {
            BodyType.ATHLETIC: {"HP": 100, "СКОРОСТЬ": 5.5, "УРОН": 10},
            BodyType.LEAN: {"HP": 90, "СКОРОСТЬ": 6.0, "УРОН": 9},
            BodyType.HEAVY: {"HP": 120, "СКОРОСТЬ": 4.5, "УРОН": 12},
            BodyType.SUMO: {"HP": 150, "СКОРОСТЬ": 3.5, "УРОН": 15},
            BodyType.NINJA: {"HP": 85, "СКОРОСТЬ": 6.5, "УРОН": 8},
            BodyType.ROBOTIC: {"HP": 110, "СКОРОСТЬ": 5.0, "УРОН": 11}
        }

    def create_preview_player(self):
        """Создание персонажа для предпросмотра"""
        self.preview_player = Player(
            self.screen_width // 2 - 30,
            350,
            is_left=True,
            body_type=self.selected_body_type,
            color_palette=self.selected_color
        )

    def create_buttons(self):
        """Создание кнопок"""
        # Кнопка подтверждения
        confirm_width = 300
        confirm_height = 50
        confirm_x = self.screen_width // 2 - confirm_width // 2
        confirm_y = self.screen_height - 120

        self.confirm_button = {
            'rect': pygame.Rect(confirm_x, confirm_y, confirm_width, confirm_height),
            'text': "ПОДТВЕРДИТЬ ВЫБОР",
            'hovered': False
        }

        # Кнопка "Назад"
        back_width = 100
        back_height = 40
        back_x = 20
        back_y = 20

        self.back_button = {
            'rect': pygame.Rect(back_x, back_y, back_width, back_height),
            'text': "НАЗАД",
            'hovered': False
        }

    def update_body_type(self, delta: int):
        """Обновление выбранного типа телосложения"""
        new_index = (self.selected_body_type_index + delta) % len(self.body_types)
        self.selected_body_type_index = new_index
        self.selected_body_type = self.body_types[new_index]
        self.create_preview_player()

    def update_color(self, delta: int):
        """Обновление выбранного цвета"""
        new_index = (self.selected_color_index + delta) % len(self.color_palettes)
        self.selected_color_index = new_index
        self.selected_color = self.color_palettes[new_index]
        self.create_preview_player()

    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool) -> dict:
        """Обновление состояния выбора"""
        result = {
            'body_type_changed': False,
            'color_changed': False,
            'confirm_clicked': False,
            'back_clicked': False,
            'color_selected': None
        }

        # Проверяем наведение на кнопки
        self.confirm_button['hovered'] = self.confirm_button['rect'].collidepoint(mouse_pos)
        self.back_button['hovered'] = self.back_button['rect'].collidepoint(mouse_pos)

        # Проверяем клики на кнопки
        if self.confirm_button['hovered'] and mouse_clicked:
            result['confirm_clicked'] = True

        if self.back_button['hovered'] and mouse_clicked:
            result['back_clicked'] = True

        # Проверяем клики на стрелки выбора типа
        left_arrow_rect = pygame.Rect(self.screen_width // 2 - 200, 400, 50, 50)
        right_arrow_rect = pygame.Rect(self.screen_width // 2 + 150, 400, 50, 50)

        if left_arrow_rect.collidepoint(mouse_pos) and mouse_clicked:
            self.update_body_type(-1)
            result['body_type_changed'] = True

        if right_arrow_rect.collidepoint(mouse_pos) and mouse_clicked:
            self.update_body_type(1)
            result['body_type_changed'] = True

        # Проверяем клики на цвета
        color_start_x = self.screen_width // 2 - (len(self.color_palettes) * 50) // 2

        for i in range(len(self.color_palettes)):
            color_x = color_start_x + i * 50
            color_rect = pygame.Rect(color_x, 650, 45, 45)

            if color_rect.collidepoint(mouse_pos) and mouse_clicked:
                self.selected_color_index = i
                self.selected_color = self.color_palettes[i]
                self.create_preview_player()
                result['color_changed'] = True
                result['color_selected'] = i

        return result

    def handle_keyboard(self, event: pygame.event.Event) -> dict:
        """Обработка клавиатуры"""
        result = {
            'body_type_changed': False,
            'color_changed': False,
            'confirm_pressed': False,
            'back_pressed': False
        }

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                self.update_body_type(-1)
                result['body_type_changed'] = True
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.update_body_type(1)
                result['body_type_changed'] = True
            elif event.key in [pygame.K_UP, pygame.K_w]:
                self.update_color(-1)
                result['color_changed'] = True
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.update_color(1)
                result['color_changed'] = True
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                result['confirm_pressed'] = True
            elif event.key == pygame.K_ESCAPE:
                result['back_pressed'] = True

        return result

    def get_selection(self) -> dict:
        """Получение текущего выбора"""
        return {
            'body_type': self.selected_body_type,
            'color': self.selected_color,
            'body_type_index': self.selected_body_type_index,
            'color_index': self.selected_color_index
        }

    def set_selection(self, body_type_index: int, color_index: int):
        """Установка выбора"""
        if 0 <= body_type_index < len(self.body_types):
            self.selected_body_type_index = body_type_index
            self.selected_body_type = self.body_types[body_type_index]

        if 0 <= color_index < len(self.color_palettes):
            self.selected_color_index = color_index
            self.selected_color = self.color_palettes[color_index]

        self.create_preview_player()

    def draw(self, screen: pygame.Surface, game_mode: str = "БОЙ С БОТОМ"):
        """Отрисовка экрана выбора персонажа"""
        # Фон
        screen.fill((30, 35, 40))

        # Заголовок
        title = self.title_font.render(f"ВЫБОР ПЕРСОНАЖА - {self.player_name}", True, self.colors['title'])
        title_rect = title.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title, title_rect)

        # Режим игры
        subtitle = self.section_font.render(f"Режим: {game_mode}", True, self.colors['highlight'])
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 140))
        screen.blit(subtitle, subtitle_rect)

        # Стрелки выбора типа
        mouse_pos = pygame.mouse.get_pos()
        left_arrow_rect = pygame.Rect(self.screen_width // 2 - 200, 400, 50, 50)
        right_arrow_rect = pygame.Rect(self.screen_width // 2 + 150, 400, 50, 50)

        left_hovered = left_arrow_rect.collidepoint(mouse_pos)
        right_hovered = right_arrow_rect.collidepoint(mouse_pos)

        # Левая стрелка
        left_color = self.colors['arrow_hover'] if left_hovered else self.colors['arrow_normal']
        pygame.draw.polygon(screen, left_color, [
            (left_arrow_rect.centerx + 10, left_arrow_rect.top + 10),
            (left_arrow_rect.centerx + 10, left_arrow_rect.bottom - 10),
            (left_arrow_rect.left + 10, left_arrow_rect.centery)
        ])
        pygame.draw.rect(screen, left_color, left_arrow_rect, 2, border_radius=5)

        # Правая стрелка
        right_color = self.colors['arrow_hover'] if right_hovered else self.colors['arrow_normal']
        pygame.draw.polygon(screen, right_color, [
            (right_arrow_rect.centerx - 10, right_arrow_rect.top + 10),
            (right_arrow_rect.centerx - 10, right_arrow_rect.bottom - 10),
            (right_arrow_rect.right - 10, right_arrow_rect.centery)
        ])
        pygame.draw.rect(screen, right_color, right_arrow_rect, 2, border_radius=5)

        # Предпросмотр персонажа
        if self.preview_player:
            # Обновляем позицию для анимации
            opponent_x = self.screen_width // 2 + 100
            ground_y = 450
            self.preview_player.update(ground_y, self.screen_width, opponent_x)
            self.preview_player.draw(screen)

        # Название типа
        type_name = self.body_type_names.get(self.selected_body_type, "НЕИЗВЕСТНО")
        name_text = self.section_font.render(type_name, True, self.colors['highlight'])
        name_rect = name_text.get_rect(center=(self.screen_width // 2, 500))
        screen.blit(name_text, name_rect)

        # Выбор цвета
        color_title = self.text_font.render("ЦВЕТОВАЯ СХЕМА:", True, self.colors['text'])
        color_title_rect = color_title.get_rect(center=(self.screen_width // 2, 530))
        screen.blit(color_title, color_title_rect)

        # Палитра цветов
        color_start_x = self.screen_width // 2 - (len(self.color_palettes) * 50) // 2

        for i, palette_name in enumerate(self.color_palettes):
            color_x = color_start_x + i * 50
            color_rect = pygame.Rect(color_x, 650, 45, 45)

            # Проверяем наведение
            color_hovered = color_rect.collidepoint(mouse_pos)

            # Цвет палитры
            palette = ColorPalette.get_palette(palette_name)
            color = palette["body"]

            # Рамка
            border_color = self.colors['color_border_selected'] if (i == self.selected_color_index or color_hovered) else self.colors['color_border']
            border_width = 3 if (i == self.selected_color_index or color_hovered) else 1

            pygame.draw.rect(screen, color, color_rect, border_radius=10)
            pygame.draw.rect(screen, border_color, color_rect, border_width, border_radius=10)

            # Отображаем название при наведении или выборе
            if i == self.selected_color_index or color_hovered:
                display_name = ColorPalette.get_display_name(palette_name)
                name_text = self.small_font.render(display_name, True, self.colors['highlight'])
                name_rect = name_text.get_rect(center=(color_rect.centerx, color_rect.bottom + 20))
                screen.blit(name_text, name_rect)

        # Статистика персонажа
        stats_y = 570
        current_stats = self.body_type_stats.get(self.selected_body_type, {})
        stats_texts = [
            f"Здоровье: {current_stats.get('HP', 0)}",
            f"Скорость: {current_stats.get('СКОРОСТЬ', 0)}",
            f"Урон: {current_stats.get('УРОН', 0)}"
        ]

        for i, stat_text in enumerate(stats_texts):
            stat_surface = self.small_font.render(stat_text, True, self.colors['text'])
            stat_rect = stat_surface.get_rect(center=(self.screen_width // 2, stats_y + i * 25))
            screen.blit(stat_surface, stat_rect)

        # Кнопка подтверждения
        confirm_color = self.colors['button_hover'] if self.confirm_button['hovered'] else self.colors['button_normal']
        confirm_text_color = self.colors['button_text']

        pygame.draw.rect(screen, confirm_color, self.confirm_button['rect'], border_radius=10)
        pygame.draw.rect(screen, self.colors['button_text'], self.confirm_button['rect'], 2, border_radius=10)

        confirm_text = self.text_font.render(self.confirm_button['text'], True, confirm_text_color)
        confirm_text_rect = confirm_text.get_rect(center=self.confirm_button['rect'].center)
        screen.blit(confirm_text, confirm_text_rect)

        # Кнопка "Назад"
        back_color = self.colors['button_hover'] if self.back_button['hovered'] else self.colors['button_normal']

        pygame.draw.rect(screen, back_color, self.back_button['rect'], border_radius=5)
        pygame.draw.rect(screen, self.colors['button_text'], self.back_button['rect'], 2, border_radius=5)

        back_text = self.small_font.render(self.back_button['text'], True, self.colors['button_text'])
        back_text_rect = back_text.get_rect(center=self.back_button['rect'].center)
        screen.blit(back_text, back_text_rect)

        # Подсказки
        hints = [
            "←→/AD - Выбор типа, ↑↓/WS - Выбор цвета",
            "ENTER/ПРОБЕЛ - Подтвердить, ЛКМ - Кликнуть по элементам",
            "ESC или кнопка 'НАЗАД' - Возврат"
        ]

        for i, hint in enumerate(hints):
            hint_text = self.small_font.render(hint, True, self.colors['hint'])
            hint_rect = hint_text.get_rect(center=(self.screen_width // 2,
                                                  self.screen_height - 40 + i * 20))
            screen.blit(hint_text, hint_rect)