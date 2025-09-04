"""
Collectible items like coins and blocks.
"""

import pygame
import math
from typing import List

from .entity import Entity
from .constants import LAYER_ENTITIES, WHITE, YELLOW


class Coin(Entity):
    """Simple coin collectible."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, 16, 16, "collectible")
        self.layer = LAYER_ENTITIES
        self.solid = False
        self._bob_time = 0.0
        self._base_y = y

    def update(self, dt: float, entities: List[Entity]) -> None:
        if not self.active:
            return

        # Simple bobbing animation
        self._bob_time += dt
        self.y = self._base_y + 3 * math.sin(self._bob_time * 6)

        # Collect if player touches
        for e in entities:
            if getattr(e, "entity_type", None) == "player" and e.active and self.collides_with(e):
                try:
                    e.collect_coin()
                except Exception:
                    pass
                self.destroy()
                break

    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        if not self.visible:
            return
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        # Gold coin
        pygame.draw.circle(screen, YELLOW, (sx + 8, sy + 8), 7)
        pygame.draw.line(screen, WHITE, (sx + 8, sy + 4), (sx + 8, sy + 12), 2)


class BumpableBlock(Entity):
    """A solid block that can be bumped from below."""

    def __init__(self, x: float, y: float, width: int = 32, height: int = 32):
        super().__init__(x, y, width, height, "block")
        self.solid = True
        self.layer = LAYER_ENTITIES
        self.bump_timer = 0.0
        self._bump_offset = 0

    def on_bumped(self, player: Entity) -> None:
        # Visual bump: nudge upward briefly
        self.bump_timer = 0.12

    def update(self, dt: float, entities: List[Entity]) -> None:
        if self.bump_timer > 0:
            self.bump_timer -= dt
            # simple bounce offset
            self._bump_offset = -2 if (int(self.bump_timer * 30) % 2 == 0) else 0
        else:
            self._bump_offset = 0

    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y) + self._bump_offset
        pygame.draw.rect(screen, (150, 100, 50), (sx, sy, self.width, self.height))
        pygame.draw.rect(screen, (0, 0, 0), (sx, sy, self.width, self.height), 1)


class QuestionBlock(BumpableBlock):
    """A '?' block that dispenses a coin or power-up once."""

    def __init__(self, x: float, y: float, contains: str = "coin"):
        super().__init__(x, y)
        self.contains = contains  # 'coin', 'mushroom', 'fire_flower'
        self.used = False

    def on_bumped(self, player: Entity) -> None:
        if self.used:
            return
        super().on_bumped(player)
        # Spawn content immediately above the block
        from .powerups import Mushroom, FireFlower
        from .collectibles import Coin
        spawn_x = self.x + (self.width - 16) / 2
        spawn_y = self.y - 16
        if self.contains == "coin":
            # Auto-collect a coin for quick feedback
            coin = Coin(spawn_x, spawn_y)
            # Mark coin collected instantly
            try:
                if hasattr(player, "collect_coin"):
                    player.collect_coin()
            except Exception:
                pass
            # Do not keep the coin entity around; just a quick popup would be ideal
        elif self.contains == "mushroom":
            # Defer actual adding; PlayingState will manage entity creation
            pass
        elif self.contains == "fire_flower":
            pass
        self.used = True

    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y) + self._bump_offset
        color = (160, 120, 40) if self.used else (220, 180, 60)
        pygame.draw.rect(screen, color, (sx, sy, self.width, self.height))
        pygame.draw.rect(screen, (0, 0, 0), (sx, sy, self.width, self.height), 2)
        if not self.used:
            # Draw question mark
            pygame.draw.rect(screen, (0, 0, 0), (sx + 10, sy + 8, 12, 6), 0)
            pygame.draw.rect(screen, (0, 0, 0), (sx + 14, sy + 16, 4, 4), 0)


class BrickBlock(BumpableBlock):
    """A brick block; breaks when big, otherwise just bumps."""

    def on_bumped(self, player: Entity) -> None:
        super().on_bumped(player)
        try:
            # If player is big (power_level >= 1), destroy the block
            if getattr(player, "power_level", 0) >= 1:
                self.destroy()
        except Exception:
            pass
