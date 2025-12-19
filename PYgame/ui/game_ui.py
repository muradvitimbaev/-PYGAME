"""
Игровой интерфейс
"""

import pygame
from typing import Tuple, Optional
from dataclasses import dataclass

@dataclass
class HealthBar:
    """Полоса здоровья"""
    x: int
    y: int
    width: int
    height: int
    max_health: int
    current_health: int
    name: str

    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Отрисовка полосы здоровья"""
        # Процент здоровья
        health_percent = self.current_health / self.max_health if self.max_health > 0 else 0

        # Цвет в зависимости от процента
        if health_percent > 0.5:
            color = (70, 210, 90)  # Зеленый
        elif health_percent > 0.25:
            color = (230, 210, 70)  # Желтый
        else:
            color = (230, 70, 70)  # Красный

        # Фон полосы
        pygame.draw.rect(screen, (40, 45, 50),
                        (self.x, self.y, self.width, self.height), border_radius=6)

        # Текущее здоровье
        health_width = max(0, int((self.width - 4) * health_percent))
        if health_width > 0:
            pygame.draw.rect(screen, color,
                           (self.x + 2, self.y + 2, health_width, self.height - 4),
                           border_radius=5)

        # Рамка
        pygame.draw.rect(screen, (190, 195, 200),
                        (self.x, self.y, self.width, self.height), 2, border_radius=6)

        # Текст с именем и здоровьем
        health_text = f"{self.name}: {self.current_health}/{self.max_health}"
        text_surface = font.render(health_text, True, (230, 235, 240))

        # Позиция текста
        if self.x < screen.get_width() // 2:
            text_x = self.x + 5
        else:
            text_x = self.x + self.width - text_surface.get_width() - 5

        screen.blit(text_surface, (text_x, self.y + 5))

class GameUI:
    """Игровой интерфейс"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Шрифты
        self.title_font = pygame.font.Font(None, 72)
        self.large_font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 36)
        self.normal_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)

        # Цвета
        self.colors = {
            'title': (250, 210, 90),
            'winner': (210, 90, 90),
            'text': (230, 235, 240),
            'hint': (160, 165, 170),
            'time': (230, 190, 90),
            'hits': (250, 230, 110),
            'button_normal': (70, 75, 80),
            'button_hover': (90, 95, 100),
            'button_text': (230, 235, 240),
            'overlay': (0, 0, 0, 200)
        }

        # Полосы здоровья
        self.health_bar_p1 = None
        self.health_bar_p2 = None

        # Верхняя панель
        self.top_panel_height = 80

        # Кнопка возврата в меню
        self.return_button = None

        # Таймер
        self.round_time = 0

    def create_health_bars(self, p1_name: str, p1_max_health: int,
                          p2_name: str, p2_max_health: int):
        """Создание полос здоровья"""
        # Полоса здоровья игрока 1 (слева)
        self.health_bar_p1 = HealthBar(
            x=20,
            y=20,
            width=304,
            height=34,
            max_health=p1_max_health,
            current_health=p1_max_health,
            name=p1_name
        )

        # Полоса здоровья игрока 2/бота (справа)
        p2_x = self.screen_width - 324
        self.health_bar_p2 = HealthBar(
            x=p2_x,
            y=20,
            width=304,
            height=34,
            max_health=p2_max_health,
            current_health=p2_max_health,
            name=p2_name
        )

    def update_health(self, p1_health: int, p2_health: int):
        """Обновление здоровья"""
        if self.health_bar_p1:
            self.health_bar_p1.current_health = p1_health

        if self.health_bar_p2:
            self.health_bar_p2.current_health = p2_health

    def update_time(self, time_seconds: int):
        """Обновление времени"""
        self.round_time = time_seconds

    def draw_top_panel(self, screen: pygame.Surface):
        """Отрисовка верхней панели"""
        # Фон панели
        panel = pygame.Surface((self.screen_width, self.top_panel_height), pygame.SRCALPHA)
        panel.fill((20, 25, 30, 220))
        screen.blit(panel, (0, 0))

        # Полосы здоровья
        if self.health_bar_p1:
            self.health_bar_p1.draw(screen, self.normal_font)

        if self.health_bar_p2:
            self.health_bar_p2.draw(screen, self.normal_font)

        # Таймер
        minutes = self.round_time // 3600
        seconds = (self.round_time % 3600) // 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        time_surface = self.medium_font.render(time_text, True, self.colors['time'])
        time_rect = time_surface.get_rect(center=(self.screen_width // 2, 40))
        screen.blit(time_surface, time_rect)

        # Информация об ударах до победы
        if self.health_bar_p1 and self.health_bar_p2:
            hits_to_win_p1 = max(0, (self.health_bar_p1.current_health + 9) // 10)
            hits_to_win_p2 = max(0, (self.health_bar_p2.current_health + 9) // 10)

            hits_text = f"Ударов до победы: {hits_to_win_p1} - {hits_to_win_p2}"
            hits_surface = self.small_font.render(hits_text, True, self.colors['hits'])
            hits_rect = hits_surface.get_rect(center=(self.screen_width // 2, 70))
            screen.blit(hits_surface, hits_rect)

    def draw_winner_screen(self, screen: pygame.Surface, winner: str,
                          stats: dict = None) -> Optional[bool]:
        """Отрисовка экрана победителя"""
        # Затемнение фона
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(self.colors['overlay'])
        screen.blit(overlay, (0, 0))

        # Текст "ПОБЕДА!"
        win_text = self.large_font.render("ПОБЕДА!", True, self.colors['title'])
        win_rect = win_text.get_rect(center=(self.screen_width // 2,
                                            self.screen_height // 2 - 100))
        screen.blit(win_text, win_rect)

        # Имя победителя
        winner_text = self.title_font.render(winner, True, self.colors['winner'])
        winner_rect = winner_text.get_rect(center=(self.screen_width // 2,
                                                  self.screen_height // 2))
        screen.blit(winner_text, winner_rect)

        # Статистика
        stats_y = self.screen_height // 2 + 60

        if stats:
            # Оставшееся здоровье
            if 'winner_health' in stats:
                health_text = f"Оставшееся здоровье: {stats['winner_health']}"
                health_surface = self.normal_font.render(health_text, True, self.colors['text'])
                health_rect = health_surface.get_rect(center=(self.screen_width // 2, stats_y))
                screen.blit(health_surface, health_rect)
                stats_y += 40

            # Нанесено ударов
            if 'hits_taken' in stats:
                hits_text = f"Нанесено ударов: {stats['hits_taken']}"
                hits_surface = self.normal_font.render(hits_text, True, self.colors['text'])
                hits_rect = hits_surface.get_rect(center=(self.screen_width // 2, stats_y))
                screen.blit(hits_surface, hits_rect)
                stats_y += 40

        # Время раунда
        minutes = self.round_time // 3600
        seconds = (self.round_time % 3600) // 60
        time_text = f"Время раунда: {minutes:02d}:{seconds:02d}"
        time_surface = self.normal_font.render(time_text, True, self.colors['text'])
        time_rect = time_surface.get_rect(center=(self.screen_width // 2, stats_y))
        screen.blit(time_surface, time_rect)

        # Кнопка возврата в меню
        return_y = self.screen_height - 150
        return_width = 350
        return_height = 60
        return_x = self.screen_width // 2 - return_width // 2

        # Проверяем наведение мыши
        mouse_pos = pygame.mouse.get_pos()
        return_rect = pygame.Rect(return_x, return_y, return_width, return_height)
        return_hovered = return_rect.collidepoint(mouse_pos)

        # Сохраняем кнопку для обработки кликов
        self.return_button = {
            'rect': return_rect,
            'hovered': return_hovered
        }

        # Цвет кнопки
        button_color = self.colors['button_hover'] if return_hovered else self.colors['button_normal']
        text_color = self.colors['button_text']

        # Рисуем кнопку
        pygame.draw.rect(screen, button_color, return_rect, border_radius=10)
        pygame.draw.rect(screen, self.colors['button_text'], return_rect, 2, border_radius=10)

        return_text = "ВЕРНУТЬСЯ В МЕНЮ"
        return_surface = self.medium_font.render(return_text, True, text_color)
        return_text_rect = return_surface.get_rect(center=(self.screen_width // 2,
                                                         return_y + return_height // 2))
        screen.blit(return_surface, return_text_rect)

        # Подсказки
        hints = [
            "Нажмите ESC или кликните по кнопке выше",
            "чтобы вернуться в главное меню"
        ]

        for i, hint in enumerate(hints):
            hint_surface = self.small_font.render(hint, True, self.colors['hint'])
            hint_rect = hint_surface.get_rect(center=(self.screen_width // 2,
                                                     return_y + return_height + 20 + i * 25))
            screen.blit(hint_surface, hint_rect)

        # Возвращаем True если мышь над кнопкой
        return return_hovered

    def check_return_button_click(self, mouse_pos: Tuple[int, int],
                                 mouse_clicked: bool) -> bool:
        """Проверка клика по кнопке возврата"""
        if self.return_button and self.return_button['rect'].collidepoint(mouse_pos):
            self.return_button['hovered'] = True
            if mouse_clicked:
                return True
        elif self.return_button:
            self.return_button['hovered'] = False

        return False

    def draw_pause_menu(self, screen: pygame.Surface) -> dict:
        """Отрисовка меню паузы"""
        # Затемнение фона
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(self.colors['overlay'])
        screen.blit(overlay, (0, 0))

        # Заголовок
        title = self.title_font.render("ПАУЗА", True, self.colors['title'])
        title_rect = title.get_rect(center=(self.screen_width // 2,
                                           self.screen_height // 2 - 100))
        screen.blit(title, title_rect)

        # Кнопки
        button_width = 300
        button_height = 50
        button_spacing = 70

        # Кнопка "Продолжить"
        continue_x = self.screen_width // 2 - button_width // 2
        continue_y = self.screen_height // 2 - button_height // 2

        continue_rect = pygame.Rect(continue_x, continue_y, button_width, button_height)

        # Кнопка "Выйти в меню"
        menu_x = self.screen_width // 2 - button_width // 2
        menu_y = continue_y + button_spacing

        menu_rect = pygame.Rect(menu_x, menu_y, button_width, button_height)

        # Проверяем наведение мыши
        mouse_pos = pygame.mouse.get_pos()
        continue_hovered = continue_rect.collidepoint(mouse_pos)
        menu_hovered = menu_rect.collidepoint(mouse_pos)

        # Отрисовка кнопок
        buttons = []

        # Кнопка "Продолжить"
        continue_color = self.colors['button_hover'] if continue_hovered else self.colors['button_normal']
        pygame.draw.rect(screen, continue_color, continue_rect, border_radius=10)
        pygame.draw.rect(screen, self.colors['button_text'], continue_rect, 2, border_radius=10)

        continue_text = self.medium_font.render("ПРОДОЛЖИТЬ", True, self.colors['button_text'])
        continue_text_rect = continue_text.get_rect(center=continue_rect.center)
        screen.blit(continue_text, continue_text_rect)

        buttons.append({
            'rect': continue_rect,
            'hovered': continue_hovered,
            'action': 'continue'
        })

        # Кнопка "Выйти в меню"
        menu_color = self.colors['button_hover'] if menu_hovered else self.colors['button_normal']
        pygame.draw.rect(screen, menu_color, menu_rect, border_radius=10)
        pygame.draw.rect(screen, self.colors['button_text'], menu_rect, 2, border_radius=10)

        menu_text = self.medium_font.render("ВЫЙТИ В МЕНЮ", True, self.colors['button_text'])
        menu_text_rect = menu_text.get_rect(center=menu_rect.center)
        screen.blit(menu_text, menu_text_rect)

        buttons.append({
            'rect': menu_rect,
            'hovered': menu_hovered,
            'action': 'menu'
        })

        # Подсказка
        hint = self.small_font.render("Нажмите ESC для выхода из паузы", True, self.colors['hint'])
        hint_rect = hint.get_rect(center=(self.screen_width // 2, menu_y + button_height + 30))
        screen.blit(hint, hint_rect)

        return {
            'buttons': buttons,
            'mouse_pos': mouse_pos
        }

    def draw_countdown(self, screen: pygame.Surface, count: int):
        """Отрисовка отсчета перед началом раунда"""
        if count <= 0:
            return

        # Затемнение фона
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Отсчет
        count_text = str(count) if count > 0 else "FIGHT!"
        color = self.colors['title'] if count > 0 else (210, 90, 90)

        # Размер шрифта в зависимости от числа
        if count > 0:
            font_size = 200 - (count - 1) * 30
            font = pygame.font.Font(None, font_size)
        else:
            font = self.title_font

        count_surface = font.render(count_text, True, color)
        count_rect = count_surface.get_rect(center=(self.screen_width // 2,
                                                   self.screen_height // 2))
        screen.blit(count_surface, count_rect)

    def draw_hit_effect(self, screen: pygame.Surface, effects: list):
        """Отрисовка эффектов попаданий"""
        for effect in effects:
            # Упрощенная версия эффекта
            if hasattr(effect, 'draw'):
                effect.draw(screen)
            elif isinstance(effect, dict):
                # Поддержка старого формата
                x = effect.get('x', 0)
                y = effect.get('y', 0)
                timer = effect.get('timer', 0)
                size = effect.get('size', 35)
                color = effect.get('color', (230, 70, 70, 180))

                progress = timer / 15.0
                current_size = size * progress
                alpha = int(255 * progress)

                effect_surface = pygame.Surface((int(current_size * 2), int(current_size * 2)), pygame.SRCALPHA)

                # Внешнее кольцо
                pygame.draw.circle(effect_surface, (*color[:3], alpha//2),
                                 (int(current_size), int(current_size)), int(current_size))

                # Внутреннее кольцо
                inner_radius = current_size * 0.6
                pygame.draw.circle(effect_surface, (255, 255, 255, alpha),
                                 (int(current_size), int(current_size)), int(inner_radius))

                screen.blit(effect_surface, (x - int(current_size), y - int(current_size)))