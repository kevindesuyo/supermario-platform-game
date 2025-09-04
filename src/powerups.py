"""
Power-up items implementation.
"""

import pygame
from typing import List

from .entity import Entity
from .constants import LAYER_ENTITIES, GRAVITY, TERMINAL_VELOCITY, RED, GREEN


class PowerUp(Entity):
    """Base power-up with simple physics."""

    def __init__(self, x: float, y: float, width: int = 20, height: int = 20, kind: str = "powerup"):
        super().__init__(x, y, width, height, "powerup")
        self.layer = LAYER_ENTITIES
        self.solid = False
        self.kind = kind
        self.grounded = False
        self.speed = 60
        self.direction = 1

    def apply_to(self, player: Entity) -> None:
        """Override in subclasses to modify player."""
        pass

    def update(self, dt: float, entities: List[Entity]) -> None:
        # Gravity
        if not self.grounded:
            self.velocity_y += GRAVITY * dt
            if self.velocity_y > TERMINAL_VELOCITY:
                self.velocity_y = TERMINAL_VELOCITY

        # Horizontal motion (default: drift to the right)
        self.velocity_x = self.direction * self.speed

        # Move and handle collisions with platforms
        from .constants import ENTITY_PLATFORM

        self.x += self.velocity_x * dt
        for e in entities:
            if (e is not self and e.solid and getattr(e, "entity_type", None) == ENTITY_PLATFORM and self.collides_with(e)):
                # Bounce off walls
                if self.x < e.x:
                    self.x = e.x - self.width
                else:
                    self.x = e.right
                self.direction *= -1
                break

        self.y += self.velocity_y * dt
        self.grounded = False
        for e in entities:
            if (e is not self and e.solid and getattr(e, "entity_type", None) == ENTITY_PLATFORM and self.collides_with(e)):
                # Land on platform
                if self.y < e.y:
                    self.y = e.y - self.height
                    self.grounded = True
                    self.velocity_y = 0
                else:
                    # Hit from below
                    self.y = e.bottom
                    self.velocity_y = 0
                break

        # Check pickup by player
        for e in entities:
            if getattr(e, "entity_type", None) == "player" and e.active and self.collides_with(e):
                try:
                    self.apply_to(e)
                except Exception:
                    pass
                self.destroy()
                break

    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        pygame.draw.rect(screen, (255, 255, 255), (sx, sy, self.width, self.height), 1)


class Mushroom(PowerUp):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 20, 20, kind="mushroom")

    def apply_to(self, player: Entity) -> None:
        # Make the player big (power_level >= 1)
        if hasattr(player, "power_level"):
            if getattr(player, "power_level", 0) < 1:
                player.power_level = 1
                if hasattr(player, "score"):
                    player.score += 1000

    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        # Simple red mushroom cap
        pygame.draw.rect(screen, (210, 0, 0), (sx, sy + 4, self.width, self.height - 4))
        pygame.draw.rect(screen, (255, 255, 255), (sx + 6, sy, self.width - 12, 8))


class FireFlower(PowerUp):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 20, 20, kind="fire_flower")
        self.speed = 0  # stationary by default

    def apply_to(self, player: Entity) -> None:
        if hasattr(player, "power_level"):
            if getattr(player, "power_level", 0) < 2:
                player.power_level = 2
                if hasattr(player, "score"):
                    player.score += 1000

    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        # Simple flower icon
        pygame.draw.rect(screen, (255, 140, 0), (sx + 4, sy, 12, 12))
        pygame.draw.rect(screen, (0, 200, 0), (sx + 8, sy + 12, 4, 8))

