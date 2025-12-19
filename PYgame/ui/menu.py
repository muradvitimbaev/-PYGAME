"""
Модуль меню и настроек
"""

import pygame
from typing import List, Tuple, Optional

class Button:
    """Класс кнопки"""

    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 font: pygame.font.Font, normal_color: Tuple[int, int, int],
                 hover_color: Tuple[int, int, int], text_color: Tuple[int, int, int]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.is_clicked = False

        # Текст кнопки
        self.text_surface = font.render(text, True, text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool):
        """Обновление состояния кнопки"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.is_clicked = self.is_hovered and mouse_clicked
        return self.is_clicked

    def draw(self, screen: pygame.Surface):
        """Отрисовка кнопки"""
        # Цвет кнопки
        color = self.hover_color if self.is_hovered else self.normal_color

        # Рисуем фон
        pygame.draw.rect(screen, color, self.rect, border_radius=10)

        # Рисуем рамку
        border_color = (230, 235, 240) if self.is_hovered else (190, 195, 200)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=10)

        # Рисуем текст
        screen.blit(self.text_surface, self.text_rect)

class MenuItem:
    """Элемент меню"""

    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 font: pygame.font.Font, normal_color: Tuple[int, int, int],
                 selected_color: Tuple[int, int, int]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.normal_color = normal_color
        self.selected_color = selected_color
        self.is_selected = False
        self.is_hovered = False

        # Текст
        self.text_surface = font.render(text, True, normal_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def update(self, mouse_pos: Tuple[int, int]):
        """Обновление состояния элемента"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def set_selected(self, selected: bool):
        """Установка состояния выбора"""
        self.is_selected = selected
        color = self.selected_color if selected else self.normal_color
        self.text_surface = self.font.render(self.text, True, color)

    def draw(self, screen: pygame.Surface):
        """Отрисовка элемента"""

            # Фон для выделенного элемента
            bg_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            bg_surface.fill((60, 65, 70, 180))
            screen.blit(bg_surface, self.rect)

            # Рамка
            pygame.draw.rect(screen, self.selected_color, self.rect, 2, border_radius=5)

        # Текст
        screen.blit(self.text_surface, self.text_rect)

class Menu:
    """Класс меню"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.items: List[MenuItem] = []
        self.selected_index = 0
        self.buttons: List[Button] = []

        # Шрифты
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 36)
        self.hint_font = pygame.font.Font(None, 24)

        # Цвета
        self.colors = {
            'title': (210, 90, 90),
            'subtitle': (160, 160, 180),
            'menu_normal': (230, 235, 240),
            'menu_selected': (210, 90, 90),
            'hint': (120, 125, 130),
            'bg_overlay': (0, 0, 0, 180)
        }

    def create_menu_items(self, items: List[str]):
        """Создание элементов меню"""
        self.items.clear()
        menu_width = 400
        menu_height = 45
        start_y = 300

        for i, item in enumerate(items):
            x = self.screen_width // 2 - menu_width // 2
            y = start_y + i * 60
            menu_item = MenuItem(x, y, menu_width, menu_height, item,
                               self.menu_font, self.colors['menu_normal'],
                               self.colors['menu_selected'])
            self.items.append(menu_item)

        # Выделяем первый элемент
        if self.items:
            self.items[0].set_selected(True)

    def create_button(self, x: int, y: int, width: int, height: int, text: str) -> Button:
        """Создание кнопки"""
        button = Button(x, y, width, height, text, self.menu_font,
                       (70, 75, 80), (90, 95, 100), (230, 235, 240))
        self.buttons.append(button)
        return button

    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool) -> Optional[int]:
        """Обновление меню"""
        # Обновляем кнопки
        for button in self.buttons:
            if button.update(mouse_pos, mouse_clicked):
                # Находим индекс кнопки
                return self.buttons.index(button)

        # Обновляем элементы меню
        hovered_index = -1
        for i, item in enumerate(self.items):
            if item.update(mouse_pos):
                hovered_index = i
                if mouse_clicked:
                    self.set_selected(i)
                    return i

        return None

    def handle_keyboard(self, event: pygame.event.Event) -> Optional[int]:
        """Обработка клавиатуры"""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                new_index = (self.selected_index - 1) % len(self.items)
                self.set_selected(new_index)
                return new_index
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                new_index = (self.selected_index + 1) % len(self.items)
                self.set_selected(new_index)
                return new_index
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                return self.selected_index

        return None

    def set_selected(self, index: int):
        """Установка выбранного элемента"""
        if 0 <= index < len(self.items):
            # Снимаем выделение с текущего
            if self.selected_index < len(self.items):
                self.items[self.selected_index].set_selected(False)

            # Выделяем новый
            self.selected_index = index
            self.items[index].set_selected(True)

    def draw_title(self, screen: pygame.Surface, title: str, subtitle: str = ""):
        """Отрисовка заголовка"""
        # Заголовок
        title_surface = self.title_font.render(title, True, self.colors['title'])
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 120))
        screen.blit(title_surface, title_rect)

        # Подзаголовок
        if subtitle:
            subtitle_surface = self.menu_font.render(subtitle, True, self.colors['subtitle'])
            subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width // 2, 190))
            screen.blit(subtitle_surface, subtitle_rect)

    def draw_hint(self, screen: pygame.Surface, hint: str):
        """Отрисовка подсказки"""
        hint_surface = self.hint_font.render(hint, True, self.colors['hint'])
        hint_rect = hint_surface.get_rect(center=(self.screen_width // 2,
                                                 self.screen_height - 50))
        screen.blit(hint_surface, hint_rect)

    def draw(self, screen: pygame.Surface):
        """Отрисовка меню"""
        # Отрисовываем элементы меню
        for item in self.items:
            item.draw(screen)

        # Отрисовываем кнопки
        for button in self.buttons:
            button.draw(screen)

class SettingsMenu(Menu):
    """Меню настроек"""

    def __init__(self, screen_width: int, screen_height: int):
        super().__init__(screen_width, screen_height)

        # Настройки
        self.settings_items = []
        self.checkmarks = {}  # Индексы отмеченных элементов

    def create_settings_list(self, items: List[str], checkmarks: List[int] = None):
        """Создание списка настроек"""
        self.settings_items.clear()
        item_width = 350
        item_height = 40
        start_y = 150

        for i, item in enumerate(items):
            x = self.screen_width // 2 - item_width // 2
            y = start_y + i * 45
            menu_item = MenuItem(x, y, item_width, item_height, item,
                               self.menu_font, self.colors['menu_normal'],
                               self.colors['menu_selected'])
            self.settings_items.append(menu_item)

        # Устанавливаем отметки
        if checkmarks:
            for idx in checkmarks:
                if 0 <= idx < len(self.settings_items):
                    self.checkmarks[idx] = True

    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool) -> Optional[int]:
        """Обновление меню настроек"""
        # Обновляем элементы
        clicked_index = -1
        for i, item in enumerate(self.settings_items):
            if item.update(mouse_pos):
                if mouse_clicked:
                    clicked_index = i
                item.set_selected(True)
            else:
                item.set_selected(False)

        return clicked_index if clicked_index >= 0 else None

    def set_checkmark(self, index: int, checked: bool):
        """Установка/снятие отметки"""
        if checked:
            self.checkmarks[index] = True
        elif index in self.checkmarks:
            del self.checkmarks[index]

        # Обновляем текст элемента
        if 0 <= index < len(self.settings_items):
            item = self.settings_items[index]
            text = item.text

            # Убираем существующую отметку
            if text.startswith("✓ "):
                text = text[2:]

            # Добавляем отметку если нужно
            if checked:
                text = "✓ " + text

            item.text = text
            item.text_surface = self.menu_font.render(text, True,
                item.selected_color if item.is_selected else item.normal_color)

    def draw(self, screen: pygame.Surface):
        """Отрисовка меню настроек"""
        # Отрисовываем элементы
        for item in self.settings_items:
            item.draw(screen)

class ControlsMenu:
    """Меню управления"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Шрифты
        self.title_font = pygame.font.Font(None, 72)
        self.section_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 24)
        self.button_font = pygame.font.Font(None, 28)

        # Цвета
        self.colors = {
            'title': (210, 90, 90),
            'section': (210, 90, 90),
            'text': (230, 235, 240),
            'highlight': (90, 160, 240),
            'panel_bg': (40, 45, 50, 200),
            'panel_border': (190, 195, 200),
            'button_normal': (70, 75, 80),
            'button_hover': (90, 95, 100),
            'button_text': (230, 235, 240)
        }

        # Кнопка "Назад"
        self.back_button = None
        self.create_back_button()

        # Правила игры
        self.rules = [
            "• Каждый боец имеет уникальное здоровье (85-150)",
            "• 1 успешный удар = 10 урона",
            "• Блок защищает от удара с правильной стороны",
            "• Разные типы телосложения имеют разные характеристики",
            "• Первый, чье здоровье достигнет 0, проигрывает"
        ]

        # Типы телосложения
        self.body_types = [
            "• АТЛЕТ: Сбалансированные характеристики",
            "• ПРОВОРНЫЙ: Быстрый но хрупкий",
            "• ТЯЖЕЛОВЕС: Медленный но выносливый",
            "• СУМОИСТ: Очень выносливый, очень медленный",
            "• НИНДЗЯ: Очень быстрый, мало здоровья",
            "• КИБОРГ: Хороший баланс с технологиями"
        ]

        # Управление
        self.controls_p1 = [
            "ИГРОК 1 (ЛЕВЫЙ):",
            "A / ← - Движение влево",
            "D / → - Движение вправо",
            "ЛЕВЫЙ ALT - Удар",
            "W / ↑ - Блок"
        ]

        self.controls_p2 = [
            "ИГРОК 2 (ПРАВЫЙ):",
            "← - Движение влево",
            "→ - Движение вправо",
            "ПРАВЫЙ ALT - Удар",
            "↑ - Блок"
        ]

    def create_back_button(self):
        """Создание кнопки 'Назад'"""
        button_width = 300
        button_height = 50
        x = self.screen_width // 2 - button_width // 2
        y = self.screen_height - 100

        self.back_button = {
            'rect': pygame.Rect(x, y, button_width, button_height),
            'text': "ВЕРНУТЬСЯ В МЕНЮ",
            'hovered': False
        }

    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool) -> bool:
        """Обновление меню управления"""
        # Проверяем наведение на кнопку
        self.back_button['hovered'] = self.back_button['rect'].collidepoint(mouse_pos)

        # Проверяем клик
        if self.back_button['hovered'] and mouse_clicked:
            return True

        return False

    def draw(self, screen: pygame.Surface):
        """Отрисовка меню управления"""
        # Заголовок
        title = self.title_font.render("ПРАВИЛА И УПРАВЛЕНИЕ", True, self.colors['title'])
        title_rect = title.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title, title_rect)

        # Две колонки
        left_x = self.screen_width // 4
        right_x = 3 * self.screen_width // 4
        y_offset = 150

        # Левая колонка - Правила
        rules_title = self.section_font.render("ОСНОВНЫЕ ПРАВИЛА:", True, self.colors['section'])
        rules_title_rect = rules_title.get_rect(center=(left_x, y_offset))
        screen.blit(rules_title, rules_title_rect)

        for i, rule in enumerate(self.rules):
            rule_text = self.text_font.render(rule, True, self.colors['text'])
            rule_rect = rule_text.get_rect(center=(left_x, y_offset + 40 + i * 30))
            screen.blit(rule_text, rule_rect)

        # Правая колонка - Типы телосложения
        types_title = self.section_font.render("ТИПЫ ТЕЛОСЛОЖЕНИЯ:", True, self.colors['section'])
        types_title_rect = types_title.get_rect(center=(right_x, y_offset))
        screen.blit(types_title, types_title_rect)

        for i, type_text in enumerate(self.body_types):
            text = self.text_font.render(type_text, True, self.colors['text'])
            text_rect = text.get_rect(center=(right_x, y_offset + 40 + i * 30))
            screen.blit(text, text_rect)

        # Управление - таблица
        controls_y = y_offset + 250

        controls_title = self.section_font.render("УПРАВЛЕНИЕ:", True, self.colors['section'])
        controls_title_rect = controls_title.get_rect(center=(self.screen_width // 2, controls_y))
        screen.blit(controls_title, controls_title_rect)

        # Таблица управления
        table_width = 600
        table_start_x = self.screen_width // 2 - table_width // 2
        table_start_y = controls_y + 40

        # Игрок 1
        panel1_width = table_width // 2 - 20
        panel1 = pygame.Surface((panel1_width, 150), pygame.SRCALPHA)
        panel1.fill(self.colors['panel_bg'])
        screen.blit(panel1, (table_start_x, table_start_y))
        pygame.draw.rect(screen, self.colors['panel_border'],
                        (table_start_x, table_start_y, panel1_width, 150), 2, border_radius=5)

        for i, control in enumerate(self.controls_p1):
            color = self.colors['section'] if i == 0 else self.colors['text']
            text = self.text_font.render(control, True, color)
            text_x = table_start_x + panel1_width // 2 - text.get_width() // 2
            screen.blit(text, (text_x, table_start_y + 10 + i * 30))

        # Игрок 2
        panel2_x = table_start_x + table_width // 2 + 10
        panel2 = pygame.Surface((panel1_width, 150), pygame.SRCALPHA)
        panel2.fill(self.colors['panel_bg'])
        screen.blit(panel2, (panel2_x, table_start_y))
        pygame.draw.rect(screen, self.colors['panel_border'],
                        (panel2_x, table_start_y, panel1_width, 150), 2, border_radius=5)

        for i, control in enumerate(self.controls_p2):
            color = self.colors['section'] if i == 0 else self.colors['text']
            text = self.text_font.render(control, True, color)
            text_x = panel2_x + panel1_width // 2 - text.get_width() // 2
            screen.blit(text, (text_x, table_start_y + 10 + i * 30))

        # Кнопка "Назад"
        button_color = self.colors['button_hover'] if self.back_button['hovered'] else self.colors['button_normal']
        text_color = self.colors['button_text']

        pygame.draw.rect(screen, button_color, self.back_button['rect'], border_radius=10)
        pygame.draw.rect(screen, self.colors['button_text'], self.back_button['rect'], 2, border_radius=10)

        button_text = self.button_font.render(self.back_button['text'], True, text_color)
        button_text_rect = button_text.get_rect(center=self.back_button['rect'].center)
        screen.blit(button_text, button_text_rect)

        # Подсказка для мыши
        mouse_hint = self.text_font.render("Можно использовать МЫШЬ для выбора пунктов меню",
                                          True, self.colors['highlight'])
        mouse_hint_rect = mouse_hint.get_rect(center=(self.screen_width // 2, table_start_y + 180))
        screen.blit(mouse_hint, mouse_hint_rect)

        # Подсказки внизу
        hints = [
            "ESC / ЛКМ на кнопке - Назад в меню",
            "WASD / ←↑↓→ / МЫШЬ - Навигация"
        ]

        for i, hint in enumerate(hints):
            hint_text = self.text_font.render(hint, True, self.colors['text'])
            hint_rect = hint_text.get_rect(center=(self.screen_width // 2,
                                                  self.screen_height - 40 + i * 25))
            screen.blit(hint_text, hint_rect)