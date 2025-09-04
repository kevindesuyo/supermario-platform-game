"""
Goal/flag entity to complete a level.
"""

import pygame
from typing import List

from .entity import Entity
from .constants import LAYER_ENTITIES


class GoalFlag(Entity):
    def __init__(self, x: float, y: float, height: int = 100):
        super().__init__(x, y - height, 12, height, "goal")
        self.layer = LAYER_ENTITIES
        self.solid = False

    def update(self, dt: float, entities: List[Entity]) -> None:
        pass

    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        # Pole
        pygame.draw.rect(screen, (200, 200, 200), (sx + 5, sy, 2, self.height))
        # Flag
        pygame.draw.polygon(screen, (30, 200, 30), [
            (sx + 7, sy + 10), (sx + 50, sy + 20), (sx + 7, sy + 30)
        ])

