"""
Класс Settings для хранения настроек игры
"""

import json
import os
from typing import List, Tuple
from dataclasses import dataclass, asdict

try:
    from enums import Difficulty
except ImportError:
    # Для совместимости
    class Difficulty:
        EASY = "easy"
        MEDIUM = "medium"
        HARD = "hard"
        INSANE = "insane"

@dataclass
class AudioSettings:
    """Настройки аудио"""
    master_volume: float = 1.0
    music_volume: float = 0.7
    sfx_volume: float = 0.8
    ui_volume: float = 0.9
    mute: bool = False

    def __post_init__(self):
        """Проверка корректности значений"""
        self.master_volume = max(0.0, min(1.0, self.master_volume))
        self.music_volume = max(0.0, min(1.0, self.music_volume))
        self.sfx_volume = max(0.0, min(1.0, self.sfx_volume))
        self.ui_volume = max(0.0, min(1.0, self.ui_volume))

@dataclass
class VideoSettings:
    """Настройки видео"""
    screen_width: int = 1024
    screen_height: int = 768
    fullscreen: bool = False
    borderless: bool = False
    vsync: bool = True
    fps_limit: int = 60

    def __post_init__(self):
        """Проверка корректности значений"""
        self.screen_width = max(800, self.screen_width)
        self.screen_height = max(600, self.screen_height)
        self.fps_limit = max(30, min(240, self.fps_limit))

@dataclass
class GameplaySettings:
    """Настройки геймплея"""
    bot_difficulty: str = Difficulty.MEDIUM
    round_time_limit: int = 180  # Секунд
    max_health: int = 100
    match_points: int = 2  # Очки для победы в матче
    damage_multiplier: float = 1.0
    enable_special_moves: bool = True
    enable_combos: bool = True

    def __post_init__(self):
        """Проверка корректности значений"""
        if isinstance(self.bot_difficulty, str):
            self.bot_difficulty = self.bot_difficulty.lower()
        self.round_time_limit = max(60, min(300, self.round_time_limit))
        self.max_health = max(50, min(200, self.max_health))
        self.match_points = max(1, min(5, self.match_points))
        self.damage_multiplier = max(0.5, min(2.0, self.damage_multiplier))

@dataclass
class ControlSettings:
    """Настройки управления"""
    # Игрок 1
    p1_move_left: list = None
    p1_move_right: list = None
    p1_attack: list = None
    p1_block: list = None
    p1_special: list = None

    # Игрок 2
    p2_move_left: list = None
    p2_move_right: list = None
    p2_attack: list = None
    p2_block: list = None
    p2_special: list = None

    # Общие
    pause_key: list = None
    menu_key: list = None

    def __post_init__(self):
        """Инициализация значений по умолчанию"""
        import pygame

        if self.p1_move_left is None:
            self.p1_move_left = [pygame.K_a, pygame.K_LEFT]
        if self.p1_move_right is None:
            self.p1_move_right = [pygame.K_d, pygame.K_RIGHT]
        if self.p1_attack is None:
            self.p1_attack = [pygame.K_LALT]
        if self.p1_block is None:
            self.p1_block = [pygame.K_w, pygame.K_UP]
        if self.p1_special is None:
            self.p1_special = [pygame.K_LSHIFT]

        if self.p2_move_left is None:
            self.p2_move_left = [pygame.K_LEFT]
        if self.p2_move_right is None:
            self.p2_move_right = [pygame.K_RIGHT]
        if self.p2_attack is None:
            self.p2_attack = [pygame.K_RALT]
        if self.p2_block is None:
            self.p2_block = [pygame.K_UP]
        if self.p2_special is None:
            self.p2_special = [pygame.K_RSHIFT]

        if self.pause_key is None:
            self.pause_key = [pygame.K_ESCAPE]
        if self.menu_key is None:
            self.menu_key = [pygame.K_ESCAPE]

class Settings:
    """Основной класс настроек игры"""

    def __init__(self):
        self.audio = AudioSettings()
        self.video = VideoSettings()
        self.gameplay = GameplaySettings()
        self.controls = ControlSettings()

        # Доступные разрешения экрана
        self.available_resolutions = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1366, 768),
            (1600, 900),
            (1920, 1080),
            (2560, 1440)
        ]

        # Путь к файлу настроек
        self.settings_file = "settings.json"

        # Загружаем настройки
        self.load()

    @property
    def current_resolution(self) -> Tuple[int, int]:
        """Текущее разрешение экрана"""
        return (self.video.screen_width, self.video.screen_height)

    @current_resolution.setter
    def current_resolution(self, resolution: Tuple[int, int]):
        """Установка разрешения экрана"""
        width, height = resolution
        self.video.screen_width = width
        self.video.screen_height = height

    def set_resolution(self, width: int, height: int):
        """Установка разрешения экрана"""
        self.video.screen_width = width
        self.video.screen_height = height

    def set_fullscreen(self, fullscreen: bool):
        """Установка полноэкранного режима"""
        self.video.fullscreen = fullscreen
        self.video.borderless = False if fullscreen else self.video.borderless

    def set_borderless(self, borderless: bool):
        """Установка режима без рамок"""
        self.video.borderless = borderless
        self.video.fullscreen = False if borderless else self.video.fullscreen

    def save(self):
        """Сохранение настроек в файл"""
        try:
            settings_data = {
                'audio': asdict(self.audio),
                'video': asdict(self.video),
                'gameplay': asdict(self.gameplay),
                'controls': asdict(self.controls)
            }

            # Преобразуем списки клавиш в строки для JSON
            for key, value in settings_data['controls'].items():
                if isinstance(value, list):
                    settings_data['controls'][key] = [str(v) for v in value]

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
            return False

    def load(self):
        """Загрузка настроек из файла"""
        if not os.path.exists(self.settings_file):
            return False

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)

            # Загружаем настройки аудио
            if 'audio' in settings_data:
                audio_data = settings_data['audio']
                self.audio = AudioSettings(**audio_data)

            # Загружаем настройки видео
            if 'video' in settings_data:
                video_data = settings_data['video']
                self.video = VideoSettings(**video_data)

            # Загружаем настройки геймплея
            if 'gameplay' in settings_data:
                gameplay_data = settings_data['gameplay']
                self.gameplay = GameplaySettings(**gameplay_data)

            # Загружаем настройки управления
            if 'controls' in settings_data:
                controls_data = settings_data['controls']
                # Преобразуем строки обратно в ключи
                import pygame
                for key, value in controls_data.items():
                    if isinstance(value, list):
                        try:
                            controls_data[key] = [pygame.key.key_code(v) if v.isalpha() else int(v)
                                                for v in value]
                        except:
                            pass
                self.controls = ControlSettings(**controls_data)

            return True
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
            return False

    def reset_to_defaults(self):
        """Сброс настроек к значениям по умолчанию"""
        self.audio = AudioSettings()
        self.video = VideoSettings()
        self.gameplay = GameplaySettings()
        self.controls = ControlSettings()
        return self.save()

    def get_available_resolutions(self) -> List[Tuple[int, int]]:
        """Получение списка доступных разрешений"""
        return self.available_resolutions

    def get_resolution_index(self) -> int:
        """Получение индекса текущего разрешения в списке доступных"""
        current = (self.video.screen_width, self.video.screen_height)
        try:
            return self.available_resolutions.index(current)
        except ValueError:
            return 1  # 1024x768 по умолчанию

    def set_resolution_by_index(self, index: int):
        """Установка разрешения по индексу"""
        if 0 <= index < len(self.available_resolutions):
            width, height = self.available_resolutions[index]
            self.set_resolution(width, height)
            return True
        return False

    def __str__(self) -> str:
        """Строковое представление настроек"""
        return (f"Settings(\n"
                f"  Audio: {self.audio}\n"
                f"  Video: {self.video}\n"
                f"  Gameplay: {self.gameplay}\n"
                f"  Controls: {self.controls}\n"
                f")")