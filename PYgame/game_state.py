"""
Класс Game и управление состояниями игры
"""

import pygame
import sys
import random
from typing import Optional, List, Tuple, Dict

try:
    from enums import GameState, BodyType
    from colors import ColorPalette
    from settings import Settings
    from player import Player, Bot
except ImportError:
    # Локальные определения для совместимости
    from enum import Enum

    class GameState(Enum):
        MENU = "menu"
        CHARACTER_SELECT_P1 = "character_select_p1"
        CHARACTER_SELECT_P2 = "character_select_p2"
        PLAYER_VS_PLAYER = "player_vs_player"
        PLAYER_VS_BOT = "player_vs_bot"
        SETTINGS = "settings"
        CONTROLS = "controls"
        EXIT = "exit"

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

    class Settings:
        def __init__(self):
            self.screen_width = 1024
            self.screen_height = 768
            self.fullscreen = False
            self.borderless = False
            self.current_resolution = (1024, 768)
            self.available_resolutions = [(800, 600), (1024, 768)]

    class Player:
        def __init__(self, x, y, is_left=True, body_type=None, color_palette="default"):
            self.x = x
            self.y = y
            self.health = 100
            self.max_health = 100
            self.width = 50
            self.height = 130

    class Bot(Player):
        pass

class HitEffect:
    """Класс для визуальных эффектов попаданий"""

    def __init__(self, x: int, y: int, effect_type: str = "hit"):
        self.x = x
        self.y = y
        self.effect_type = effect_type
        self.timer = 15
        self.max_timer = 15
        self.size = 35

        # Цвета в зависимости от типа эффекта
        self.colors = {
            "hit": [(230, 70, 70, 180), (255, 255, 255, 100)],
            "block": [(60, 120, 220, 120), (100, 160, 255, 60)],
            "critical": [(255, 215, 0, 200), (255, 255, 100, 100)]
        }

        self.current_colors = self.colors.get(effect_type, self.colors["hit"])

    def update(self):
        """Обновление эффекта"""
        self.timer -= 1
        return self.timer > 0

    def draw(self, screen: pygame.Surface):
        """Отрисовка эффекта"""
        progress = self.timer / self.max_timer
        current_size = self.size * progress

        # Создаем поверхность для эффекта
        effect_surface = pygame.Surface((int(current_size * 2), int(current_size * 2)), pygame.SRCALPHA)

        # Внешнее кольцо
        outer_color = self.current_colors[0]
        pygame.draw.circle(effect_surface, outer_color,
                          (int(current_size), int(current_size)),
                          int(current_size))

        # Внутреннее кольцо
        inner_color = self.current_colors[1]
        inner_radius = current_size * 0.6
        pygame.draw.circle(effect_surface, inner_color,
                          (int(current_size), int(current_size)),
                          int(inner_radius))

        # Центральная точка
        pygame.draw.circle(effect_surface, (255, 255, 255, int(255 * progress)),
                          (int(current_size), int(current_size)),
                          int(current_size * 0.2))

        screen.blit(effect_surface,
                   (self.x - int(current_size), self.y - int(current_size)))

class Game:
    """Основной класс игры, управляющий состояниями"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.state = GameState.MENU
        self.screen = None
        self.clock = pygame.time.Clock()
        self.fonts = {}
        self.background_image = None

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
        self.hit_effects: List[HitEffect] = []
        self.battle_finished = False

        # Статистика матча
        self.match_stats = {
            "player1_hits": 0,
            "player2_hits": 0,
            "player1_blocks": 0,
            "player2_blocks": 0,
            "round_duration": 0
        }

        # Инициализация Pygame
        self.init_pygame()

        # Создание фона
        self.create_background()

        # Загрузка шрифтов
        self.load_fonts()

    def init_pygame(self):
        """Инициализация Pygame и создание окна"""
        pygame.init()
        pygame.font.init()

        # Создание окна с текущими настройками
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

        # Настройка мыши
        pygame.mouse.set_visible(True)

        # Установка позиции земли
        self.ground_y = self.settings.screen_height - 120

    def load_fonts(self):
        """Загрузка шрифтов"""
        try:
            # Основные шрифты
            self.fonts["title"] = pygame.font.Font(None, 72)
            self.fonts["large"] = pygame.font.Font(None, 48)
            self.fonts["medium"] = pygame.font.Font(None, 36)
            self.fonts["normal"] = pygame.font.Font(None, 28)
            self.fonts["small"] = pygame.font.Font(None, 24)
            self.fonts["tiny"] = pygame.font.Font(None, 18)
        except:
            # Резервные системные шрифты
            self.fonts["title"] = pygame.font.SysFont("arial", 72, bold=True)
            self.fonts["large"] = pygame.font.SysFont("arial", 48, bold=True)
            self.fonts["medium"] = pygame.font.SysFont("arial", 36)
            self.fonts["normal"] = pygame.font.SysFont("arial", 28)
            self.fonts["small"] = pygame.font.SysFont("arial", 24)
            self.fonts["tiny"] = pygame.font.SysFont("arial", 18)

    def create_background(self):
        """Создание тематического фона для игры"""
        width, height = self.settings.screen_width, self.settings.screen_height

        # Создаем поверхность для фона
        self.background_image = pygame.Surface((width, height))

        # Градиентное небо
        for y in range(height):
            # Интерполяция цвета от темного к светлому
            if y < height * 0.4:
                ratio = y / (height * 0.4)
                r = int(15 + ratio * 10)
                g = int(20 + ratio * 15)
                b = int(30 + ratio * 15)
            elif y < height * 0.7:
                ratio = (y - height * 0.4) / (height * 0.3)
                r = int(25 + ratio * 10)
                g = int(35 + ratio * 10)
                b = int(45 + ratio * 10)
            else:
                ratio = (y - height * 0.7) / (height * 0.3)
                r = int(35 + ratio * 10)
                g = int(45 + ratio * 10)
                b = int(55 + ratio * 10)

            pygame.draw.line(self.background_image, (r, g, b), (0, y), (width, y))

        # Добавляем облака
        self.add_clouds()

        # Добавляем горы
        self.add_mountains()

        # Добавляем деревья
        self.add_trees()

    def add_clouds(self):
        """Добавление облаков на фон"""
        width, height = self.background_image.get_size()

        cloud_colors = [
            (50, 60, 70, 100),
            (55, 65, 75, 80),
            (60, 70, 80, 60)
        ]

        # Позиции и размеры облаков
        cloud_positions = [
            (200, 100, 120, 40),
            (500, 150, 180, 50),
            (800, 80, 150, 45),
            (100, 200, 100, 35),
            (700, 250, 200, 55)
        ]

        for x, y, w, h in cloud_positions:
            # Создаем несколько слоев для каждого облака
            for i, color in enumerate(cloud_colors):
                cloud_surface = pygame.Surface((w + i*20, h + i*10), pygame.SRCALPHA)
                pygame.draw.ellipse(cloud_surface, color, (0, 0, w + i*20, h + i*10))
                self.background_image.blit(cloud_surface, (x - i*10, y - i*5))

    def add_mountains(self):
        """Добавление гор на фон"""
        width, height = self.background_image.get_size()

        mountain_colors = [
            (40, 50, 60),
            (35, 45, 55),
            (30, 40, 50)
        ]

        # Вершины гор
        mountain_peaks = [
            [(0, height*0.6), (200, height*0.3), (400, height*0.6)],
            [(300, height*0.6), (500, height*0.4), (700, height*0.6)],
            [(600, height*0.6), (800, height*0.35), (1000, height*0.6)],
            [(900, height*0.6), (1100, height*0.45), (1300, height*0.6)]
        ]

        # Ограничиваем шириной экрана
        mountain_peaks = [
            [(max(0, x), y) for x, y in peaks]
            for peaks in mountain_peaks
        ]

        for i, peaks in enumerate(mountain_peaks):
            color = mountain_colors[i % len(mountain_colors)]
            pygame.draw.polygon(self.background_image, color, peaks)

    def add_trees(self):
        """Добавление деревьев на фон"""
        width, height = self.background_image.get_size()

        tree_base_y = height * 0.7

        # Добавляем несколько деревьев
        for x in range(50, width, 150):
            tree_height = random.randint(80, 120)
            tree_width = random.randint(40, 60)

            # Ствол
            trunk_width = tree_width // 4
            trunk_height = tree_height // 3
            pygame.draw.rect(self.background_image, (45, 40, 35),
                           (x - trunk_width//2, tree_base_y, trunk_width, trunk_height))

            # Крона (пирамида)
            crown_points = [
                (x, tree_base_y - tree_height),
                (x - tree_width//2, tree_base_y - tree_height//3),
                (x + tree_width//2, tree_base_y - tree_height//3)
            ]
            pygame.draw.polygon(self.background_image, (25, 35, 30), crown_points)

    def handle_events(self):
        """Обработка всех событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = GameState.EXIT
                return

            # Обработка событий мыши
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                self.handle_mouse_click(mouse_pos)

            # Обработка событий клавиатуры в зависимости от состояния
            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
            elif event.type == pygame.KEYUP:
                self.handle_keyup(event)

    def handle_mouse_click(self, mouse_pos: Tuple[int, int]):
        """Обработка кликов мыши"""
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
            self.handle_game_mouse_click(mouse_pos)

    def handle_keydown(self, event):
        """Обработка нажатия клавиш"""
        if event.key == pygame.K_ESCAPE:
            self.handle_escape_key()

        # Обработка в зависимости от состояния
        if self.state == GameState.MENU:
            self.handle_menu_keydown(event)
        elif self.state == GameState.CHARACTER_SELECT_P1:
            self.handle_character_select_p1_keydown(event)
        elif self.state == GameState.CHARACTER_SELECT_P2:
            self.handle_character_select_p2_keydown(event)
        elif self.state == GameState.SETTINGS:
            self.handle_settings_keydown(event)
        elif self.state == GameState.CONTROLS:
            self.handle_controls_keydown(event)
        elif self.state in [GameState.PLAYER_VS_PLAYER, GameState.PLAYER_VS_BOT]:
            self.handle_game_keydown(event)

    def handle_keyup(self, event):
        """Обработка отпускания клавиш"""
        if self.state in [GameState.PLAYER_VS_PLAYER, GameState.PLAYER_VS_BOT]:
            self.handle_game_keyup(event)

    def handle_escape_key(self):
        """Обработка клавиши ESC"""
        if self.state == GameState.MENU:
            self.state = GameState.EXIT
        elif self.state in [GameState.SETTINGS, GameState.CONTROLS]:
            self.state = GameState.MENU
        elif self.state in [GameState.CHARACTER_SELECT_P1, GameState.CHARACTER_SELECT_P2]:
            self.state = GameState.MENU
        elif self.state in [GameState.PLAYER_VS_PLAYER, GameState.PLAYER_VS_BOT]:
            if self.battle_finished:
                self.return_to_menu()
            else:
                # Пауза или возврат в меню
                self.return_to_menu()

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
            text = self.fonts["medium"].render(item, True, (230, 235, 240))
            text_rect = text.get_rect(center=(self.settings.screen_width // 2, 300 + i * 60))

            # Расширяем область клика для удобства
            click_rect = text_rect.inflate(20, 10)
            if click_rect.collidepoint(mouse_pos):
                self.menu_selection = i
                self.execute_menu_action()
                break

    def handle_menu_keydown(self, event):
        """Обработка клавиш в главном меню"""
        menu_items_count = 5

        if event.key in [pygame.K_UP, pygame.K_w]:
            self.menu_selection = (self.menu_selection - 1) % menu_items_count
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            self.menu_selection = (self.menu_selection + 1) % menu_items_count
        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            self.execute_menu_action()

    def execute_menu_action(self):
        """Выполнение выбранного действия в меню"""
        if self.menu_selection == 0:  # Бой с ботом
            self.state = GameState.CHARACTER_SELECT_P1
            self.player1_selection = 0
            self.player1_color_selection = 0
        elif self.menu_selection == 1:  # Игрок против игрока
            self.state = GameState.CHARACTER_SELECT_P1
            self.player1_selection = 0
            self.player1_color_selection = 0
        elif self.menu_selection == 2:  # Правила и управление
            self.state = GameState.CONTROLS
            self.controls_selection = 0
        elif self.menu_selection == 3:  # Настройки
            self.state = GameState.SETTINGS
            self.settings_selection = 0
        elif self.menu_selection == 4:  # Выход
            self.state = GameState.EXIT

    def handle_character_select_p1_mouse_click(self, mouse_pos):
        """Обработка кликов мыши в выборе персонажа для игрока 1"""
        # Проверяем клик по цветам
        color_names = ColorPalette.get_palette_names()
        color_start_x = self.settings.screen_width // 2 - (len(color_names) * 50) // 2

        for i in range(len(color_names)):
            color_x = color_start_x + i * 50
            color_rect = pygame.Rect(color_x, 650, 45, 45)
            if color_rect.collidepoint(mouse_pos):
                self.player1_color_selection = i
                return

        # Проверяем клик по стрелкам выбора типа
        left_arrow_rect = pygame.Rect(self.settings.screen_width // 2 - 200, 400, 50, 50)
        right_arrow_rect = pygame.Rect(self.settings.screen_width // 2 + 150, 400, 50, 50)

        if left_arrow_rect.collidepoint(mouse_pos):
            body_types = list(BodyType)
            self.player1_selection = (self.player1_selection - 1) % len(body_types)
        elif right_arrow_rect.collidepoint(mouse_pos):
            body_types = list(BodyType)
            self.player1_selection = (self.player1_selection + 1) % len(body_types)

        # Проверяем клик по кнопке подтверждения
        confirm_rect = pygame.Rect(
            self.settings.screen_width // 2 - 150,
            self.settings.screen_height - 120,
            300, 50
        )

        if confirm_rect.collidepoint(mouse_pos):
            self.confirm_p1_selection()

        # Проверяем клик по кнопке "Назад"
        back_rect = pygame.Rect(20, 20, 100, 40)
        if back_rect.collidepoint(mouse_pos):
            self.state = GameState.MENU

    def handle_character_select_p1_keydown(self, event):
        """Обработка клавиш в выборе персонажа для игрока 1"""
        body_types = list(BodyType)
        color_names = ColorPalette.get_palette_names()

        if event.key in [pygame.K_LEFT, pygame.K_a]:
            self.player1_selection = (self.player1_selection - 1) % len(body_types)
        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
            self.player1_selection = (self.player1_selection + 1) % len(body_types)
        elif event.key in [pygame.K_UP, pygame.K_w]:
            self.player1_color_selection = (self.player1_color_selection - 1) % len(color_names)
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            self.player1_color_selection = (self.player1_color_selection + 1) % len(color_names)
        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            self.confirm_p1_selection()

    def confirm_p1_selection(self):
        """Подтверждение выбора для игрока 1"""
        body_types = list(BodyType)
        color_names = ColorPalette.get_palette_names()

        self.selected_body_type_p1 = body_types[self.player1_selection]
        self.selected_color_p1 = color_names[self.player1_color_selection]

        # В зависимости от режима игры
        if self.menu_selection == 0:  # Бой с ботом
            self.start_player_vs_bot()
        else:  # Игрок против игрока
            self.state = GameState.CHARACTER_SELECT_P2
            self.player2_selection = 0
            self.player2_color_selection = 0

    def handle_character_select_p2_mouse_click(self, mouse_pos):
        """Обработка кликов мыши в выборе персонажа для игрока 2"""
        # Проверяем клик по цветам
        color_names = ColorPalette.get_palette_names()
        color_start_x = self.settings.screen_width // 2 - (len(color_names) * 50) // 2

        for i in range(len(color_names)):
            color_x = color_start_x + i * 50
            color_rect = pygame.Rect(color_x, 650, 45, 45)
            if color_rect.collidepoint(mouse_pos):
                self.player2_color_selection = i
                return

        # Проверяем клик по стрелкам
        left_arrow_rect = pygame.Rect(self.settings.screen_width // 2 - 200, 400, 50, 50)
        right_arrow_rect = pygame.Rect(self.settings.screen_width // 2 + 150, 400, 50, 50)

        if left_arrow_rect.collidepoint(mouse_pos):
            body_types = list(BodyType)
            self.player2_selection = (self.player2_selection - 1) % len(body_types)
        elif right_arrow_rect.collidepoint(mouse_pos):
            body_types = list(BodyType)
            self.player2_selection = (self.player2_selection + 1) % len(body_types)

        # Проверяем клик по кнопке начала боя
        start_rect = pygame.Rect(
            self.settings.screen_width // 2 - 150,
            self.settings.screen_height - 120,
            300, 50
        )

        if start_rect.collidepoint(mouse_pos):
            self.confirm_p2_selection()

        # Проверяем клик по кнопке "Назад"
        back_rect = pygame.Rect(20, 20, 100, 40)
        if back_rect.collidepoint(mouse_pos):
            self.state = GameState.CHARACTER_SELECT_P1

    def handle_character_select_p2_keydown(self, event):
        """Обработка клавиш в выборе персонажа для игрока 2"""
        body_types = list(BodyType)
        color_names = ColorPalette.get_palette_names()

        if event.key in [pygame.K_LEFT, pygame.K_a]:
            self.player2_selection = (self.player2_selection - 1) % len(body_types)
        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
            self.player2_selection = (self.player2_selection + 1) % len(body_types)
        elif event.key in [pygame.K_UP, pygame.K_w]:
            self.player2_color_selection = (self.player2_color_selection - 1) % len(color_names)
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            self.player2_color_selection = (self.player2_color_selection + 1) % len(color_names)
        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            self.confirm_p2_selection()

    def confirm_p2_selection(self):
        """Подтверждение выбора для игрока 2"""
        body_types = list(BodyType)
        color_names = ColorPalette.get_palette_names()

        self.selected_body_type_p2 = body_types[self.player2_selection]
        self.selected_color_p2 = color_names[self.player2_color_selection]

        self.start_player_vs_player()

    def handle_settings_mouse_click(self, mouse_pos):
        """Обработка кликов мыши в настройках"""
        items_count = 3 + len(self.settings.available_resolutions)

        for i in range(items_count):
            item_y = 150 + i * 45
            click_rect = pygame.Rect(self.settings.screen_width // 2 - 150, item_y - 20, 300, 40)

            if click_rect.collidepoint(mouse_pos):
                self.settings_selection = i
                self.execute_settings_action()
                break

    def handle_settings_keydown(self, event):
        """Обработка клавиш в настройках"""
        items_count = 3 + len(self.settings.available_resolutions)

        if event.key in [pygame.K_UP, pygame.K_w]:
            self.settings_selection = (self.settings_selection - 1) % items_count
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            self.settings_selection = (self.settings_selection + 1) % items_count
        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            self.execute_settings_action()

    def execute_settings_action(self):
        """Выполнение выбранного действия в настройках"""
        if self.settings_selection == 0:  # Оконный режим
            self.settings.set_fullscreen(False)
            self.settings.set_borderless(False)
            self.init_pygame()
        elif self.settings_selection == 1:  # Оконный без рамки
            self.settings.set_borderless(True)
            self.init_pygame()
        elif self.settings_selection == 2:  # Полноэкранный
            self.settings.set_fullscreen(True)
            self.init_pygame()
        else:  # Разрешения экрана
            res_index = self.settings_selection - 3
            if res_index < len(self.settings.available_resolutions):
                width, height = self.settings.available_resolutions[res_index]
                self.settings.set_resolution(width, height)
                self.init_pygame()
                self.create_background()

    def handle_controls_mouse_click(self, mouse_pos):
        """Обработка кликов мыши в меню управления"""
        # Кнопка "Назад"
        back_rect = pygame.Rect(
            self.settings.screen_width // 2 - 150,
            self.settings.screen_height - 100,
            300, 50
        )

        if back_rect.collidepoint(mouse_pos):
            self.state = GameState.MENU

    def handle_controls_keydown(self, event):
        """Обработка клавиш в меню управления"""
        if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            self.state = GameState.MENU

    def handle_game_mouse_click(self, mouse_pos):
        """Обработка кликов мыши в игровом режиме"""
        # Если бой завершен, проверяем клик по кнопке возврата
        if self.battle_finished and self.winner:
            return_width = 350
            return_height = 60
            return_x = self.settings.screen_width // 2 - return_width // 2
            return_y = self.settings.screen_height - 150

            return_rect = pygame.Rect(return_x, return_y, return_width, return_height)
            if return_rect.collidepoint(mouse_pos):
                self.return_to_menu()

    def handle_game_keydown(self, event):
        """Обработка нажатия клавиш в игровом режиме"""
        if self.battle_finished:
            return

        # Управление игроком 1
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

        # Управление игроком 2 (только в режиме PvP)
        if self.state == GameState.PLAYER_VS_PLAYER:
            if event.key == pygame.K_LEFT:
                self.player2.move_left()
            elif event.key == pygame.K_RIGHT:
                self.player2.move_right()
            elif event.key == pygame.K_RALT:
                self.player2.attack(self.player1.x)
            elif event.key == pygame.K_UP:
                self.player2.block(self.player1.x)

    def handle_game_keyup(self, event):
        """Обработка отпускания клавиш в игровом режиме"""
        if self.battle_finished:
            return

        # Игрок 1
        if event.key in [pygame.K_a, pygame.K_d]:
            self.player1.stop_moving()

        # Игрок 2
        if self.state == GameState.PLAYER_VS_PLAYER:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                self.player2.stop_moving()

    def start_player_vs_bot(self):
        """Начало игры против бота"""
        self.state = GameState.PLAYER_VS_BOT

        # Создание игрока 1
        self.player1 = Player(
            200,
            self.ground_y - 100,
            is_left=True,
            body_type=self.selected_body_type_p1,
            color_palette=self.selected_color_p1
        )

        # Создание бота со случайным типом и цветом
        bot_type = random.choice(list(BodyType))
        bot_color = random.choice(ColorPalette.get_palette_names())

        self.bot = Bot(
            self.settings.screen_width - 300,
            self.ground_y - 100,
            is_left=False,
            body_type=bot_type,
            color_palette=bot_color
        )

        # Сброс состояния игры
        self.reset_game_state()

    def start_player_vs_player(self):
        """Начало игры игрок против игрока"""
        self.state = GameState.PLAYER_VS_PLAYER

        # Создание игрока 1
        self.player1 = Player(
            200,
            self.ground_y - 100,
            is_left=True,
            body_type=self.selected_body_type_p1,
            color_palette=self.selected_color_p1
        )

        # Создание игрока 2
        self.player2 = Player(
            self.settings.screen_width - 300,
            self.ground_y - 100,
            is_left=False,
            body_type=self.selected_body_type_p2,
            color_palette=self.selected_color_p2
        )

        # Сброс состояния игры
        self.reset_game_state()

    def reset_game_state(self):
        """Сброс состояния игры"""
        self.winner = None
        self.round_time = 0
        self.hit_effects.clear()
        self.battle_finished = False

        # Сброс статистики
        self.match_stats = {
            "player1_hits": 0,
            "player2_hits": 0,
            "player1_blocks": 0,
            "player2_blocks": 0,
            "round_duration": 0
        }

    def update(self):
        """Обновление игрового состояния"""
        if self.state in [GameState.PLAYER_VS_PLAYER, GameState.PLAYER_VS_BOT]:
            self.update_game()

    def update_game(self):
        """Обновление игрового состояния"""
        if self.battle_finished:
            self.update_hit_effects()
            return

        self.game_time += 1
        self.round_time += 1

        self.update_hit_effects()

        # Обновление в зависимости от режима
        if self.state == GameState.PLAYER_VS_BOT:
            self.update_pvb_mode()
        elif self.state == GameState.PLAYER_VS_PLAYER:
            self.update_pvp_mode()

        # Проверка окончания боя
        self.check_battle_end()

    def update_pvb_mode(self):
        """Обновление в режиме игрок против бота"""
        # Обновление игрока
        self.player1.update(self.ground_y, self.settings.screen_width, self.bot.x)

        # Обновление бота
        self.bot.update(self.ground_y, self.settings.screen_width, self.player1.x)
        self.bot.make_decision(self.player1, self.settings.screen_width)

        # Проверка коллизий
        self.check_collisions(self.player1, self.bot)

    def update_pvp_mode(self):
        """Обновление в режиме игрок против игрока"""
        # Обновление игроков
        self.player1.update(self.ground_y, self.settings.screen_width, self.player2.x)
        self.player2.update(self.ground_y, self.settings.screen_width, self.player1.x)

        # Проверка коллизий
        self.check_collisions(self.player1, self.player2)

    def update_hit_effects(self):
        """Обновление эффектов попаданий"""
        # Удаляем завершившиеся эффекты
        self.hit_effects = [effect for effect in self.hit_effects if effect.update()]

    def check_collisions(self, player1: Player, player2: Player):
        """Проверка коллизий между двумя игроками"""
        # Проверка атаки игрока 1
        if (player1.attacking and
            not player1.already_hit_in_current_attack and
            player1.get_attack_rect().colliderect(player2.get_rect())):

            if self.check_block(player2, player1):
                player1.already_hit_in_current_attack = True
                self.create_hit_effect(
                    player2.x + player2.width // 2,
                    player2.y + player2.height // 2,
                    "block"
                )
                self.match_stats["player2_blocks"] += 1
            else:
                damage_dealt = player2.take_damage()
                if damage_dealt:
                    self.create_hit_effect(
                        player2.x + player2.width // 2,
                        player2.y + player2.height // 2,
                        "hit"
                    )
                    player1.already_hit_in_current_attack = True
                    self.match_stats["player1_hits"] += 1

        # Проверка атаки игрока 2
        if (player2.attacking and
            not player2.already_hit_in_current_attack and
            player2.get_attack_rect().colliderect(player1.get_rect())):

            if self.check_block(player1, player2):
                player2.already_hit_in_current_attack = True
                self.create_hit_effect(
                    player1.x + player1.width // 2,
                    player1.y + player1.height // 2,
                    "block"
                )
                self.match_stats["player1_blocks"] += 1
            else:
                damage_dealt = player1.take_damage()
                if damage_dealt:
                    self.create_hit_effect(
                        player1.x + player1.width // 2,
                        player1.y + player1.height // 2,
                        "hit"
                    )
                    player2.already_hit_in_current_attack = True
                    self.match_stats["player2_hits"] += 1

    def check_block(self, defender: Player, attacker: Player) -> bool:
        """Проверка успешности блока"""
        if not defender.blocking:
            return False

        # Определяем сторону атаки
        if attacker.attacking_with_right:
            # Атака правой рукой
            if defender.block_direction == "right" and attacker.x < defender.x:
                return True
        else:
            # Атака левой рукой
            if defender.block_direction == "left" and attacker.x > defender.x:
                return True

        return False

    def create_hit_effect(self, x: int, y: int, effect_type: str = "hit"):
        """Создание визуального эффекта попадания"""
        self.hit_effects.append(HitEffect(x, y, effect_type))

    def check_battle_end(self):
        """Проверка окончания боя"""
        if self.state == GameState.PLAYER_VS_BOT:
            if self.player1.health <= 0:
                self.winner = "БОТ"
                self.battle_finished = True
            elif self.bot.health <= 0:
                self.winner = "ИГРОК 1"
                self.battle_finished = True

        elif self.state == GameState.PLAYER_VS_PLAYER:
            if self.player1.health <= 0:
                self.winner = "ИГРОК 2"
                self.battle_finished = True
            elif self.player2.health <= 0:
                self.winner = "ИГРОК 1"
                self.battle_finished = True

        # Сохраняем продолжительность раунда
        if self.battle_finished:
            self.match_stats["round_duration"] = self.round_time

    def return_to_menu(self):
        """Возврат в главное меню"""
        self.state = GameState.MENU
        self.winner = None
        self.battle_finished = False
        self.round_time = 0
        self.hit_effects.clear()

        # Сбрасываем игроков
        self.player1 = None
        self.player2 = None
        self.bot = None

    def draw(self):
        """Основной метод отрисовки"""
        # Очистка экрана
        self.screen.fill((0, 0, 0))

        # Отрисовка в зависимости от состояния
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.CHARACTER_SELECT_P1:
            self.draw_character_select_p1()
        elif self.state == GameState.CHARACTER_SELECT_P2:
            self.draw_character_select_p2()
        elif self.state == GameState.SETTINGS:
            self.draw_settings()
        elif self.state == GameState.CONTROLS:
            self.draw_controls()
        elif self.state in [GameState.PLAYER_VS_PLAYER, GameState.PLAYER_VS_BOT]:
            self.draw_game()

        pygame.display.flip()

    def draw_menu(self):
        """Отрисовка главного меню"""
        # Фон
        bg_scaled = pygame.transform.scale(self.background_image,
                                          (self.settings.screen_width,
                                           self.settings.screen_height))
        self.screen.blit(bg_scaled, (0, 0))

        # Затемнение фона
        overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Заголовок
        title = self.fonts["title"].render("ДУЭЛЯНТЫ", True, (210, 90, 90))
        title_rect = title.get_rect(center=(self.settings.screen_width // 2, 120))
        self.screen.blit(title, title_rect)

        subtitle = self.fonts["medium"].render("Арена Силуэтов", True, (160, 160, 180))
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
            color = (210, 90, 90) if i == self.menu_selection else (230, 235, 240)

            # Фон для выделенного пункта
            if i == self.menu_selection:
                item_width = 400
                item_height = 45
                item_x = self.settings.screen_width // 2 - item_width // 2
                item_y = 295 + i * 60

                highlight_surface = pygame.Surface((item_width, item_height), pygame.SRCALPHA)
                highlight_surface.fill((60, 65, 70, 180))
                self.screen.blit(highlight_surface, (item_x, item_y))

                pygame.draw.rect(self.screen, color,
                               (item_x, item_y, item_width, item_height), 2, border_radius=5)

            text = self.fonts["medium"].render(item, True, color)
            text_rect = text.get_rect(center=(self.settings.screen_width // 2, 300 + i * 60))
            self.screen.blit(text, text_rect)

        # Подсказки
        hint = self.fonts["small"].render(
            "Используйте ↑↓←→/WASD или МЫШЬ для навигации, ENTER/ЛКМ для выбора",
            True, (120, 125, 130)
        )
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

    def draw_character_select(self, player_name: str, selection: int,
                             color_selection: int, is_p1: bool = True):
        """Общий метод отрисовки выбора персонажа"""
        # Фон
        self.screen.fill((30, 35, 40))

        # Заголовок
        title = self.fonts["title"].render(f"ВЫБОР ПЕРСОНАЖА - {player_name}", True, (230, 110, 110))
        title_rect = title.get_rect(center=(self.settings.screen_width // 2, 80))
        self.screen.blit(title, title_rect)

        # Режим игры
        mode_text = "БОЙ С БОТОМ" if self.menu_selection == 0 else "ИГРОК ПРОТИВ ИГРОКА"
        subtitle = self.fonts["medium"].render(f"Режим: {mode_text}", True, (210, 90, 90))
        subtitle_rect = subtitle.get_rect(center=(self.settings.screen_width // 2, 140))
        self.screen.blit(subtitle, subtitle_rect)

        # Отображение персонажа и элементов управления
        # (Этот код аналогичен тому, что уже есть в duelist_game.py)
        # Для экономии места, здесь будет сокращенная версия

        # Кнопка подтверждения/начала боя
        confirm_text = "ПОДТВЕРДИТЬ ВЫБОР" if is_p1 else "НАЧАТЬ БОЙ"
        confirm_surface = self.fonts["medium"].render(confirm_text, True, (230, 235, 240))
        confirm_rect = confirm_surface.get_rect(
            center=(self.settings.screen_width // 2, self.settings.screen_height - 95)
        )

        # Фон кнопки
        button_bg = pygame.Rect(confirm_rect.x - 20, confirm_rect.y - 10,
                               confirm_rect.width + 40, confirm_rect.height + 20)
        pygame.draw.rect(self.screen, (70, 75, 80), button_bg, border_radius=10)
        pygame.draw.rect(self.screen, (230, 235, 240), button_bg, 2, border_radius=10)

        self.screen.blit(confirm_surface, confirm_rect)

    def draw_settings(self):
        """Отрисовка экрана настроек"""
        self.screen.fill((30, 35, 40))

        # Заголовок
        title = self.fonts["title"].render("НАСТРОЙКИ", True, (210, 90, 90))
        title_rect = title.get_rect(center=(self.settings.screen_width // 2, 80))
        self.screen.blit(title, title_rect)

        # Список настроек
        settings_items = [
            "Оконный режим",
            "Оконный без рамки",
            "Полноэкранный"
        ]

        # Добавляем разрешения экрана
        settings_items += [f"{w} x {h}" for w, h in self.settings.available_resolutions]

        for i, item in enumerate(settings_items):
            # Отметка выбранного варианта
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

            # Цвет текста
            color = (210, 90, 90) if i == self.settings_selection else (230, 235, 240)

            text = self.fonts["medium"].render(item, True, color)
            text_rect = text.get_rect(center=(self.settings.screen_width // 2, 150 + i * 45))
            self.screen.blit(text, text_rect)

    def draw_controls(self):
        """Отрисовка меню правил и управления"""
        self.screen.fill((30, 35, 40))

        # Заголовок
        title = self.fonts["title"].render("ПРАВИЛА И УПРАВЛЕНИЕ", True, (210, 90, 90))
        title_rect = title.get_rect(center=(self.settings.screen_width // 2, 80))
        self.screen.blit(title, title_rect)

        # Содержимое
        # (Здесь должен быть полный текст правил и управления)
        # Для экономии места оставляем базовую структуру

        # Кнопка "Назад"
        back_text = self.fonts["medium"].render("ВЕРНУТЬСЯ В МЕНЮ", True, (230, 235, 240))
        back_rect = back_text.get_rect(
            center=(self.settings.screen_width // 2, self.settings.screen_height - 100)
        )

        # Фон кнопки
        button_bg = pygame.Rect(back_rect.x - 20, back_rect.y - 10,
                               back_rect.width + 40, back_rect.height + 20)
        pygame.draw.rect(self.screen, (70, 75, 80), button_bg, border_radius=10)
        pygame.draw.rect(self.screen, (230, 235, 240), button_bg, 2, border_radius=10)

        self.screen.blit(back_text, back_rect)

    def draw_game(self):
        """Отрисовка игрового экрана"""
        # Фон
        bg_scaled = pygame.transform.scale(self.background_image,
                                          (self.settings.screen_width,
                                           self.settings.screen_height))
        self.screen.blit(bg_scaled, (0, 0))

        # Земля
        ground_height = 120
        ground_y = self.settings.screen_height - ground_height

        # Текстура земли
        for y in range(ground_y, self.settings.screen_height, 4):
            color_value = int(40 + (y - ground_y)//2)
            pygame.draw.line(self.screen, (color_value, color_value + 5, color_value + 10),
                            (0, y), (self.settings.screen_width, y))

        # Эффекты попаданий
        for effect in self.hit_effects:
            effect.draw(self.screen)

        # Отрисовка игроков
        if self.state == GameState.PLAYER_VS_BOT:
            if self.player1:
                self.player1.draw(self.screen)
            if self.bot:
                self.bot.draw(self.screen)
            self.draw_game_info("ИГРОК 1", self.player1.health if self.player1 else 0,
                               "БОТ", self.bot.health if self.bot else 0)

        elif self.state == GameState.PLAYER_VS_PLAYER:
            if self.player1:
                self.player1.draw(self.screen)
            if self.player2:
                self.player2.draw(self.screen)
            self.draw_game_info("ИГРОК 1", self.player1.health if self.player1 else 0,
                               "ИГРОК 2", self.player2.health if self.player2 else 0)

        # Отрисовка победителя
        if self.winner:
            self.draw_winner_screen()

    def draw_game_info(self, p1_name: str, p1_health: int,
                      p2_name: str, p2_health: int):
        """Отрисовка игровой информации"""
        # Верхняя панель
        panel_height = 80
        panel = pygame.Surface((self.settings.screen_width, panel_height), pygame.SRCALPHA)
        panel.fill((20, 25, 30, 220))
        self.screen.blit(panel, (0, 0))

        # Время
        minutes = self.round_time // 3600
        seconds = (self.round_time % 3600) // 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        time_surface = self.fonts["medium"].render(time_text, True, (230, 190, 90))
        time_rect = time_surface.get_rect(center=(self.settings.screen_width // 2, 40))
        self.screen.blit(time_surface, time_rect)

        # Полоса здоровья игрока 1
        p1_max = self.player1.max_health if self.player1 else 100
        p1_percent = p1_health / p1_max if p1_max > 0 else 0
        p1_width = 300 * p1_percent

        # Цвет полосы здоровья
        p1_color = (70, 210, 90) if p1_percent > 0.5 else (230, 210, 70) if p1_percent > 0.25 else (230, 70, 70)

        pygame.draw.rect(self.screen, (40, 45, 50), (20, 20, 304, 34), border_radius=6)
        pygame.draw.rect(self.screen, p1_color, (22, 22, p1_width, 30), border_radius=5)
        pygame.draw.rect(self.screen, (190, 195, 200), (20, 20, 304, 34), 2, border_radius=6)

        p1_text = f"{p1_name}: {p1_health}/{p1_max}"
        p1_surface = self.fonts["normal"].render(p1_text, True, (230, 235, 240))
        self.screen.blit(p1_surface, (25, 25))

        # Полоса здоровья игрока 2/бота
        if self.state == GameState.PLAYER_VS_BOT:
            p2_max = self.bot.max_health if self.bot else 100
        else:
            p2_max = self.player2.max_health if self.player2 else 100

        p2_percent = p2_health / p2_max if p2_max > 0 else 0
        p2_width = 300 * p2_percent

        p2_color = (70, 210, 90) if p2_percent > 0.5 else (230, 210, 70) if p2_percent > 0.25 else (230, 70, 70)

        p2_x = self.settings.screen_width - 324
        pygame.draw.rect(self.screen, (40, 45, 50), (p2_x, 20, 304, 34), border_radius=6)
        pygame.draw.rect(self.screen, p2_color, (p2_x + 2, 22, p2_width, 30), border_radius=5)
        pygame.draw.rect(self.screen, (190, 195, 200), (p2_x, 20, 304, 34), 2, border_radius=6)

        p2_text = f"{p2_name}: {p2_health}/{p2_max}"
        p2_surface = self.fonts["normal"].render(p2_text, True, (230, 235, 240))
        p2_text_x = self.settings.screen_width - p2_surface.get_width() - 25
        self.screen.blit(p2_surface, (p2_text_x, 25))

    def draw_winner_screen(self):
        """Отрисовка экрана победителя"""
        # Затемнение фона
        overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Текст победы
        win_text = self.fonts["large"].render("ПОБЕДА!", True, (250, 210, 90))
        win_rect = win_text.get_rect(center=(self.settings.screen_width // 2,
                                            self.settings.screen_height // 2 - 100))
        self.screen.blit(win_text, win_rect)

        # Имя победителя
        winner_text = self.fonts["title"].render(self.winner, True, (210, 90, 90))
        winner_rect = winner_text.get_rect(center=(self.settings.screen_width // 2,
                                                  self.settings.screen_height // 2))
        self.screen.blit(winner_text, winner_rect)

        # Статистика
        stats_y = self.settings.screen_height // 2 + 60

        # Время раунда
        minutes = self.round_time // 3600
        seconds = (self.round_time % 3600) // 60
        time_text = f"Время: {minutes:02d}:{seconds:02d}"
        time_surface = self.fonts["normal"].render(time_text, True, (230, 235, 240))
        time_rect = time_surface.get_rect(center=(self.settings.screen_width // 2, stats_y))
        self.screen.blit(time_surface, time_rect)

        # Кнопка возврата в меню
        return_y = self.settings.screen_height - 150
        return_text = self.fonts["medium"].render("ВЕРНУТЬСЯ В МЕНЮ", True, (230, 235, 240))
        return_rect = return_text.get_rect(center=(self.settings.screen_width // 2, return_y))

        # Фон кнопки
        button_bg = pygame.Rect(return_rect.x - 20, return_rect.y - 10,
                               return_rect.width + 40, return_rect.height + 20)
        pygame.draw.rect(self.screen, (70, 75, 80), button_bg, border_radius=10)
        pygame.draw.rect(self.screen, (230, 235, 240), button_bg, 2, border_radius=10)

        self.screen.blit(return_text, return_rect)

        # Подсказка
        hint_text = self.fonts["small"].render("Нажмите ESC или кликните по кнопке", True, (160, 165, 170))
        hint_rect = hint_text.get_rect(center=(self.settings.screen_width // 2, return_y + 50))
        self.screen.blit(hint_text, hint_rect)

    def run(self):
        """Основной игровой цикл"""
        print("=" * 65)
        print("          ДУЭЛЯНТЫ - АРЕНА СИЛУЭТОВ")
        print("=" * 65)
        print("⚔️  6 Уникальных типов телосложения")
        print("❤️  Здоровье от 85 до 150")
        print("⚡ Разная скорость и урон")
        print("🎨 6 Цветовых схем")
        print("🤖 Интеллектуальный ИИ-противник")
        print("=" * 65)

        while self.state != GameState.EXIT:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()