"""
Quick headless sanity check for the Super Mario project.
Runs a few update/render ticks using SDL's dummy video driver.
"""

import os
import sys
import time

# Use dummy video driver for headless environments
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from src.game_engine import GameEngine
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, STATE_PLAYING


def run_ticks(ticks: int = 5, fps: int = 60) -> int:
    pygame.init()
    try:
        # Create an off-screen surface; display init may still be required on some systems
        try:
            pygame.display.init()
            pygame.display.set_mode((1, 1))
        except pygame.error:
            # Fallback: continue with off-screen rendering
            pass

        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        engine = GameEngine(screen)
        engine.change_state(STATE_PLAYING)

        dt = 1.0 / fps
        for i in range(ticks):
            # Pump events minimally
            for event in pygame.event.get():
                engine.handle_event(event)
            engine.update(dt)
            engine.render()
        return 0
    except Exception as e:
        print("Headless check failed:", repr(e))
        return 1
    finally:
        pygame.quit()


if __name__ == "__main__":
    sys.exit(run_ticks())

