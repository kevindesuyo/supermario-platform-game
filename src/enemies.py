"""
Enemy implementations
"""

import pygame
import math
from typing import List
from .entity import Entity
from .constants import (
    ENTITY_ENEMY, LAYER_ENTITIES, GRAVITY, TERMINAL_VELOCITY,
    RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE
)

class Enemy(Entity):
    """Base enemy class"""
    
    def __init__(self, x: float, y: float, width: int, height: int, enemy_type: str):
        super().__init__(x, y, width, height, ENTITY_ENEMY)
        self.layer = LAYER_ENTITIES
        self.enemy_type = enemy_type
        
        # AI state
        self.direction = -1  # -1 for left, 1 for right
        self.patrol_distance = 100
        self.start_x = x
        self.speed = 50
        self.grounded = False
        
        # Combat properties
        self.health = 1
        self.damage = 1
        self.can_be_stomped = True
        self.stomp_points = 100
        
        # State flags
        self.stunned = False
        self.stun_timer = 0.0
        self.dead = False
        self.death_timer = 0.0
        
    def take_damage(self, damage: int = 1) -> None:
        """Take damage"""
        self.health -= damage
        if self.health <= 0:
            self.die()
    
    def die(self) -> None:
        """Handle death"""
        self.dead = True
        self.death_timer = 1.0  # Death animation time
        self.velocity_y = -200  # Death bounce
        self.solid = False
    
    def stomp(self) -> int:
        """Handle being stomped by player"""
        if self.can_be_stomped:
            self.die()
            return self.stomp_points
        return 0
    
    def check_ground_collision(self, entities: List[Entity]) -> None:
        """Check for ground collision"""
        self.grounded = False
        
        test_rect = pygame.Rect(int(self.x), int(self.y + self.height), 
                               self.width, 1)
        
        for entity in entities:
            if (entity != self and entity.solid and 
                entity.entity_type == "platform" and 
                test_rect.colliderect(entity.rect)):
                self.grounded = True
                break
    
    def check_wall_collision(self, entities: List[Entity]) -> bool:
        """Check for wall collision"""
        # Check ahead for walls
        test_x = self.x + (self.width if self.direction > 0 else -1)
        test_rect = pygame.Rect(int(test_x), int(self.y), 1, self.height)
        
        for entity in entities:
            if (entity != self and entity.solid and 
                entity.entity_type == "platform" and 
                test_rect.colliderect(entity.rect)):
                return True
        return False
    
    def check_cliff_ahead(self, entities: List[Entity]) -> bool:
        """Check for cliff ahead"""
        # Check if there's ground ahead
        test_x = self.x + (self.width + 10 if self.direction > 0 else -10)
        test_rect = pygame.Rect(int(test_x), int(self.y + self.height), 1, 10)
        
        for entity in entities:
            if (entity != self and entity.solid and 
                entity.entity_type == "platform" and 
                test_rect.colliderect(entity.rect)):
                return False
        return True
    
    def update_ai(self, dt: float, entities: List[Entity]) -> None:
        """Update AI behavior - override in subclasses"""
        pass
    
    def update_physics(self, dt: float, entities: List[Entity]) -> None:
        """Update physics"""
        # Apply gravity
        if not self.grounded:
            self.velocity_y += GRAVITY * dt
            if self.velocity_y > TERMINAL_VELOCITY:
                self.velocity_y = TERMINAL_VELOCITY
        
        # Check ground collision
        self.check_ground_collision(entities)
        
        # Move horizontally
        self.x += self.velocity_x * dt
        
        # Move vertically
        self.y += self.velocity_y * dt
        
        # Handle platform collision
        for entity in entities:
            if (entity != self and entity.solid and 
                entity.entity_type == "platform" and 
                self.collides_with(entity)):
                
                collision_side = self.get_collision_side(entity)
                
                if collision_side == "bottom" and self.velocity_y > 0:
                    self.y = entity.y - self.height
                    self.velocity_y = 0
                    self.grounded = True
                elif collision_side == "top" and self.velocity_y < 0:
                    self.y = entity.bottom
                    self.velocity_y = 0
                elif collision_side in ["left", "right"]:
                    if collision_side == "left":
                        self.x = entity.x - self.width
                    else:
                        self.x = entity.right
                    self.direction *= -1  # Turn around
                    self.velocity_x = 0
    
    def update(self, dt: float, entities: List[Entity]) -> None:
        """Update enemy"""
        if not self.active:
            return
        
        # Update timers
        if self.stun_timer > 0:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.stunned = False
        
        if self.dead:
            self.death_timer -= dt
            if self.death_timer <= 0:
                self.destroy()
            return
        
        # Update AI and physics
        if not self.stunned:
            self.update_ai(dt, entities)
        
        self.update_physics(dt, entities)
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """Render enemy"""
        if not self.visible:
            return
        
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Different colors based on state
        if self.dead:
            color = (100, 100, 100)
        elif self.stunned:
            color = (255, 255, 0)
        else:
            color = self.get_color()
        
        pygame.draw.rect(screen, color, (screen_x, screen_y, self.width, self.height))
        
        # Draw direction indicator
        if not self.dead:
            eye_x = screen_x + (self.width - 5 if self.direction > 0 else 5)
            pygame.draw.circle(screen, (255, 255, 255), (eye_x, screen_y + 8), 3)
    
    def get_color(self) -> tuple:
        """Get enemy color - override in subclasses"""
        return RED

class Goomba(Enemy):
    """Simple walking enemy"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 24, 24, "goomba")
        self.speed = 30
        self.patrol_distance = 80
    
    def update_ai(self, dt: float, entities: List[Entity]) -> None:
        """Simple patrol AI"""
        # Turn around at walls or cliffs
        if self.check_wall_collision(entities) or self.check_cliff_ahead(entities):
            self.direction *= -1
        
        # Turn around if moved too far from start
        if abs(self.x - self.start_x) > self.patrol_distance:
            self.direction *= -1
        
        # Move
        self.velocity_x = self.direction * self.speed
    
    def get_color(self) -> tuple:
        return (139, 69, 19)  # Brown

class Koopa(Enemy):
    """Turtle enemy that can hide in shell"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 28, 32, "koopa")
        self.speed = 40
        self.patrol_distance = 120
        self.shell_mode = False
        self.shell_timer = 0.0
        self.can_be_stomped = True
    
    def stomp(self) -> int:
        """Handle being stomped"""
        if not self.shell_mode:
            # Enter shell mode
            self.shell_mode = True
            self.shell_timer = 5.0
            self.height = 20
            self.velocity_x = 0
            self.stunned = True
            self.stun_timer = 0.5
            return self.stomp_points
        else:
            # Kick shell
            player_entities = [e for e in [] if e.entity_type == "player"]  # TODO: Get player reference
            if player_entities:
                player = player_entities[0]
                if player.center_x < self.center_x:
                    self.velocity_x = 200
                    self.direction = 1
                else:
                    self.velocity_x = -200
                    self.direction = -1
                self.stunned = False
                self.stun_timer = 0
            return self.stomp_points
    
    def update_ai(self, dt: float, entities: List[Entity]) -> None:
        """Koopa AI with shell behavior"""
        if self.shell_mode:
            self.shell_timer -= dt
            if self.shell_timer <= 0:
                # Exit shell mode
                self.shell_mode = False
                self.height = 32
                self.velocity_x = 0
        
        if not self.shell_mode and not self.stunned:
            # Normal patrol behavior
            if self.check_wall_collision(entities) or self.check_cliff_ahead(entities):
                self.direction *= -1
            
            if abs(self.x - self.start_x) > self.patrol_distance:
                self.direction *= -1
            
            self.velocity_x = self.direction * self.speed
    
    def get_color(self) -> tuple:
        if self.shell_mode:
            return GREEN
        return (0, 128, 0)  # Dark green

class Piranha(Enemy):
    """Plant enemy that pops up from pipes"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 32, 32, "piranha")
        self.speed = 0  # Doesn't move horizontally
        self.can_be_stomped = False
        self.pop_timer = 0.0
        self.pop_duration = 2.0
        self.hide_duration = 2.0
        self.popped_up = False
        self.original_y = y
        self.pipe_height = 40
        
        # Start hidden
        self.y = self.original_y + self.pipe_height
        self.visible = False
    
    def update_ai(self, dt: float, entities: List[Entity]) -> None:
        """Pop up and down behavior"""
        self.pop_timer += dt
        
        if self.popped_up:
            # Currently popped up
            if self.pop_timer >= self.pop_duration:
                # Time to hide
                self.popped_up = False
                self.pop_timer = 0.0
                self.visible = False
                self.solid = False
                self.y = self.original_y + self.pipe_height
        else:
            # Currently hidden
            if self.pop_timer >= self.hide_duration:
                # Time to pop up
                self.popped_up = True
                self.pop_timer = 0.0
                self.visible = True
                self.solid = True
                self.y = self.original_y
    
    def get_color(self) -> tuple:
        return RED

class FlyingEnemy(Enemy):
    """Flying enemy with sine wave movement"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 24, 24, "flying")
        self.speed = 60
        self.can_be_stomped = True
        self.fly_amplitude = 50
        self.fly_frequency = 2.0
        self.time_offset = 0.0
        self.original_y = y
    
    def update_ai(self, dt: float, entities: List[Entity]) -> None:
        """Sine wave flying pattern"""
        self.time_offset += dt
        
        # Horizontal movement
        self.velocity_x = self.direction * self.speed
        
        # Vertical sine wave
        sine_value = math.sin(self.time_offset * self.fly_frequency)
        target_y = self.original_y + sine_value * self.fly_amplitude
        
        # Smooth movement toward target Y
        y_diff = target_y - self.y
        self.velocity_y = y_diff * 2.0
        
        # Turn around at boundaries
        if abs(self.x - self.start_x) > self.patrol_distance:
            self.direction *= -1
    
    def get_color(self) -> tuple:
        return PURPLE

class EnemySpawner:
    """Factory for creating enemies"""
    
    @staticmethod
    def create_enemy(enemy_type: str, x: float, y: float) -> Enemy:
        """Create enemy by type"""
        if enemy_type == "goomba":
            return Goomba(x, y)
        elif enemy_type == "koopa":
            return Koopa(x, y)
        elif enemy_type == "piranha":
            return Piranha(x, y)
        elif enemy_type == "flying":
            return FlyingEnemy(x, y)
        else:
            # Default to goomba
            return Goomba(x, y)