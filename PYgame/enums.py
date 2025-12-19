"""
Перечисления для игры
"""

from enum import Enum, auto

class GameState(Enum):
    """Состояния игры"""
    MENU = "menu"
    CHARACTER_SELECT_P1 = "character_select_p1"
    CHARACTER_SELECT_P2 = "character_select_p2"
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

class Difficulty(Enum):
    """Уровни сложности бота"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    INSANE = "insane"

class GameMode(Enum):
    """Режимы игры"""
    SINGLE_PLAYER = "single_player"
    MULTIPLAYER = "multiplayer"
    TRAINING = "training"

class MenuSection(Enum):
    """Разделы меню"""
    MAIN = "main"
    SETTINGS = "settings"
    CONTROLS = "controls"
    CHARACTER_SELECT = "character_select"

class AnimationState(Enum):
    """Состояния анимации"""
    IDLE = "idle"
    WALKING = "walking"
    ATTACKING = "attacking"
    BLOCKING = "blocking"
    HURT = "hurt"
    VICTORY = "victory"
    DEFEAT = "defeat"

class SoundType(Enum):
    """Типы звуков"""
    HIT = "hit"
    BLOCK = "block"
    SELECT = "select"
    CONFIRM = "confirm"
    BACK = "back"
    VICTORY = "victory"
    DEFEAT = "defeat"
    MENU_NAVIGATE = "menu_navigate"
    ATTACK = "attack"

class EffectType(Enum):
    """Типы визуальных эффектов"""
    HIT = "hit"
    BLOCK = "block"
    HEAL = "heal"
    SPEED_BOOST = "speed_boost"
    POWER_UP = "power_up"
    CRITICAL_HIT = "critical_hit"

class PlayerType(Enum):
    """Типы игроков"""
    HUMAN = "human"
    BOT = "bot"
    NETWORK = "network"

class MatchResult(Enum):
    """Результаты матча"""
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"
    IN_PROGRESS = "in_progress"
    TIMEOUT = "timeout"