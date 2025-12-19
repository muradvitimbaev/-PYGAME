"""
Duelist Game - Главная точка входа
"""

import pygame
import sys

# Локальный импорт
from duelist_game import main as game_main

def main():
    """Точка входа в игру"""
    try:

        game_main()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        input("Нажмите Enter для выхода...")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())