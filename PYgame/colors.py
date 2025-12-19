"""
Цветовые палитры для игры
"""

class ColorPalette:
    """Цветовые палитры для персонажей"""

    PALETTES = {
        "default": {
            "body": (30, 30, 40),
            "highlight": (60, 60, 80),
            "attack": (220, 60, 60),
            "block": (60, 120, 220),
            "secondary": (80, 80, 100),
            "accent": (240, 180, 60)
        },
        "red": {
            "body": (50, 20, 25),
            "highlight": (80, 40, 45),
            "attack": (240, 80, 80),
            "block": (80, 160, 240),
            "secondary": (90, 50, 55),
            "accent": (255, 200, 100)
        },
        "blue": {
            "body": (20, 30, 50),
            "highlight": (40, 60, 90),
            "attack": (240, 100, 60),
            "block": (100, 180, 250),
            "secondary": (50, 70, 100),
            "accent": (255, 220, 120)
        },
        "green": {
            "body": (25, 40, 25),
            "highlight": (45, 70, 45),
            "attack": (230, 80, 80),
            "block": (80, 180, 230),
            "secondary": (55, 90, 55),
            "accent": (240, 200, 80)
        },
        "purple": {
            "body": (40, 20, 50),
            "highlight": (70, 40, 80),
            "attack": (240, 120, 60),
            "block": (120, 80, 240),
            "secondary": (90, 60, 100),
            "accent": (250, 200, 140)
        },
        "gold": {
            "body": (60, 50, 30),
            "highlight": (90, 80, 50),
            "attack": (240, 140, 60),
            "block": (140, 200, 240),
            "secondary": (110, 100, 70),
            "accent": (255, 220, 100)
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

    @staticmethod
    def get_display_name(palette_name: str) -> str:
        """Возвращает отображаемое имя палитры"""
        display_names = {
            "default": "По умолчанию",
            "red": "Красный",
            "blue": "Синий",
            "green": "Зеленый",
            "purple": "Фиолетовый",
            "gold": "Золотой"
        }
        return display_names.get(palette_name, "Неизвестно")

class UIPalette:
    """Цветовая палитра для интерфейса"""

    # Основные цвета интерфейса
    PRIMARY = (20, 25, 30)
    SECONDARY = (40, 45, 50)
    TERTIARY = (60, 65, 70)

    # Текст
    TEXT_PRIMARY = (230, 235, 240)
    TEXT_SECONDARY = (160, 165, 170)
    TEXT_DISABLED = (100, 105, 110)
    TEXT_HIGHLIGHT = (210, 90, 90)
    TEXT_INFO = (90, 160, 240)
    TEXT_SUCCESS = (70, 210, 90)
    TEXT_WARNING = (230, 210, 70)
    TEXT_ERROR = (230, 70, 70)

    # Кнопки
    BUTTON_NORMAL = (70, 75, 80)
    BUTTON_HOVER = (90, 95, 100)
    BUTTON_ACTIVE = (110, 115, 120)
    BUTTON_DISABLED = (50, 55, 60)

    # Панели
    PANEL_BACKGROUND = (30, 35, 40, 200)
    PANEL_BORDER = (190, 195, 200)
    PANEL_HIGHLIGHT = (210, 90, 90)

    # Полосы здоровья
    HEALTH_HIGH = (70, 210, 90)
    HEALTH_MEDIUM = (230, 210, 70)
    HEALTH_LOW = (230, 70, 70)
    HEALTH_BACKGROUND = (40, 45, 50)
    HEALTH_BORDER = (190, 195, 200)

    # Эффекты
    EFFECT_HIT = (230, 70, 70, 180)
    EFFECT_BLOCK = (60, 120, 220, 120)
    EFFECT_HEAL = (70, 210, 90, 150)
    EFFECT_CRITICAL = (255, 215, 0, 200)

    @staticmethod
    def get_health_color(percentage: float) -> tuple:
        """Возвращает цвет здоровья в зависимости от процента"""
        if percentage > 0.5:
            return UIPalette.HEALTH_HIGH
        elif percentage > 0.25:
            return UIPalette.HEALTH_MEDIUM
        else:
            return UIPalette.HEALTH_LOW

class BackgroundPalette:
    """Цветовая палитра для фонов"""

    # Небо (градиент)
    SKY_TOP = (15, 20, 30)
    SKY_MID = (25, 35, 45)
    SKY_BOTTOM = (35, 45, 55)
    SKY_HORIZON = (45, 55, 65)

    # Облака
    CLOUD_DARK = (50, 60, 70, 100)
    CLOUD_MEDIUM = (55, 65, 75, 80)
    CLOUD_LIGHT = (60, 70, 80, 60)

    # Горы
    MOUNTAIN_DARK = (30, 40, 50)
    MOUNTAIN_MEDIUM = (35, 45, 55)
    MOUNTAIN_LIGHT = (40, 50, 60)

    # Деревья
    TREE_TRUNK = (45, 40, 35)
    TREE_CROWN = (25, 35, 30)

    # Земля
    GROUND_DARK = (40, 45, 50)
    GROUND_MEDIUM = (45, 50, 55)
    GROUND_LIGHT = (50, 55, 60)

    # Трава
    GRASS = (45, 65, 45)

    # Арена
    ARENA_FLOOR = (45, 50, 55)
    ARENA_CENTER_LINE = (85, 90, 95, 150)

class MenuPalette:
    """Цветовая палитра для меню"""

    # Заголовки
    TITLE_PRIMARY = (210, 90, 90)
    TITLE_SHADOW = (10, 10, 15)
    TITLE_GLOW = (255, 100, 100, 100)

    # Подзаголовки
    SUBTITLE = (160, 160, 180)

    # Пункты меню
    MENU_ITEM_NORMAL = (230, 235, 240)
    MENU_ITEM_HOVER = (210, 90, 90)
    MENU_ITEM_SELECTED = (240, 100, 100)
    MENU_ITEM_DISABLED = (100, 105, 110)

    # Фон пунктов меню
    MENU_ITEM_BG_NORMAL = (40, 45, 50, 0)
    MENU_ITEM_BG_HOVER = (60, 65, 70, 180)

    # Маркеры выбора
    SELECTION_MARKER = (210, 90, 90)

    # Подсказки
    HINT = (120, 125, 130)
    HINT_HIGHLIGHT = (90, 160, 240)