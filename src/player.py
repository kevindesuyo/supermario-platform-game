"""
Player character implementation
"""

import pygame
from typing import List
from .entity import Entity
from .constants import (
    PLAYER_SPEED, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_ACCELERATION, PLAYER_FRICTION,
    GRAVITY, TERMINAL_VELOCITY, JUMP_SPEED, ENTITY_PLAYER, LAYER_PLAYER,
    KEYS_LEFT, KEYS_RIGHT, KEYS_JUMP, KEYS_RUN, RED, WHITE, BLUE
)

class Player(Entity):
    """Player character with platformer physics"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT, ENTITY_PLAYER)
        self.layer = LAYER_PLAYER
        
        # Movement state
        self.grounded = False
        self.can_jump = True
        self.jump_buffer_time = 0.0
        self.coyote_time = 0.0
        self.wall_slide_timer = 0.0
        
        # Movement parameters
        self.max_speed = PLAYER_SPEED
        self.acceleration = PLAYER_ACCELERATION
        self.friction = PLAYER_FRICTION
        self.jump_speed = JUMP_SPEED
        self.run_multiplier = 2.0
        
        # Animation states
        self.facing_right = True
        self.animation_state = "idle"
        self.animation_timer = 0.0
        
        # Power-up state
        self.power_level = 0  # 0=small, 1=big, 2=fire, etc.
        self.invulnerable = False
        self.invulnerable_timer = 0.0
        
        # Stats
        self.lives = 3
        self.score = 0
        self.coins = 0
        
        # Input state
        self.input_left = False
        self.input_right = False
        self.input_jump = False
        self.input_run = False
        
    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Handle keyboard input"""
        self.input_left = any(keys[key] for key in KEYS_LEFT)
        self.input_right = any(keys[key] for key in KEYS_RIGHT)
        self.input_jump = any(keys[key] for key in KEYS_JUMP)
        self.input_run = any(keys[key] for key in KEYS_RUN)
    
    def update_physics(self, dt: float) -> None:
        """Update physics simulation"""
        # Horizontal movement
        target_velocity = 0.0
        if self.input_left:
            target_velocity = -self.max_speed
            self.facing_right = False
        elif self.input_right:
            target_velocity = self.max_speed
            self.facing_right = True
        
        # Apply run multiplier
        if self.input_run:
            target_velocity *= self.run_multiplier
        
        # Apply acceleration or friction
        if target_velocity == 0:
            # Apply friction
            if abs(self.velocity_x) < self.friction * dt:
                self.velocity_x = 0
            else:
                friction_direction = -1 if self.velocity_x > 0 else 1
                self.velocity_x += friction_direction * self.friction * dt
        else:
            # Apply acceleration toward target velocity
            velocity_diff = target_velocity - self.velocity_x
            if abs(velocity_diff) < self.acceleration * dt:
                self.velocity_x = target_velocity
            else:
                acceleration_direction = 1 if velocity_diff > 0 else -1
                self.velocity_x += acceleration_direction * self.acceleration * dt
        
        # Jumping
        if self.input_jump and self.jump_buffer_time > 0:
            if self.can_jump or self.coyote_time > 0:
                self.velocity_y = self.jump_speed
                self.can_jump = False
                self.jump_buffer_time = 0
                self.coyote_time = 0
                self.grounded = False
        
        # Apply gravity
        if not self.grounded:
            self.velocity_y += GRAVITY * dt
            # Terminal velocity
            if self.velocity_y > TERMINAL_VELOCITY:
                self.velocity_y = TERMINAL_VELOCITY
        
        # Update timers
        if self.jump_buffer_time > 0:
            self.jump_buffer_time -= dt
        if self.coyote_time > 0:
            self.coyote_time -= dt
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
    
    def update_animation(self, dt: float) -> None:
        """Update animation state"""
        self.animation_timer += dt
        
        # Determine animation state
        if not self.grounded:
            if self.velocity_y < 0:
                self.animation_state = "jump"
            else:
                self.animation_state = "fall"
        elif abs(self.velocity_x) > 10:
            self.animation_state = "run" if self.input_run else "walk"
        else:
            self.animation_state = "idle"
    
    def check_ground_collision(self, entities: List[Entity]) -> None:
        """Check for ground collision"""
        self.grounded = False
        
        # Create a test rectangle slightly below the player
        test_rect = pygame.Rect(int(self.x), int(self.y + self.height), 
                               self.width, 1)
        
        for entity in entities:
            if (entity != self and entity.solid and 
                entity.entity_type == "platform" and 
                test_rect.colliderect(entity.rect)):
                self.grounded = True
                self.can_jump = True
                self.coyote_time = 0.2  # Coyote time in seconds
                break
    
    def handle_platform_collision(self, entities: List[Entity]) -> None:
        """Handle collision with platforms"""
        for entity in entities:
            if (entity != self and entity.solid and 
                entity.entity_type == "platform" and 
                self.collides_with(entity)):
                
                collision_side = self.get_collision_side(entity)
                
                if collision_side == "bottom" and self.velocity_y > 0:
                    # Landing on top of platform
                    self.y = entity.y - self.height
                    self.velocity_y = 0
                    self.grounded = True
                    self.can_jump = True
                elif collision_side == "top" and self.velocity_y < 0:
                    # Hitting platform from below
                    self.y = entity.bottom
                    self.velocity_y = 0
                elif collision_side == "left" and self.velocity_x > 0:
                    # Hitting platform from the left
                    self.x = entity.x - self.width
                    self.velocity_x = 0
                elif collision_side == "right" and self.velocity_x < 0:
                    # Hitting platform from the right
                    self.x = entity.right
                    self.velocity_x = 0
    
    def update(self, dt: float, entities: List[Entity]) -> None:
        """Update player logic"""
        if not self.active:
            return
        
        # Store previous position
        prev_x, prev_y = self.x, self.y
        
        # Handle input buffering
        keys = pygame.key.get_pressed()
        self.handle_input(keys)
        
        if self.input_jump:
            self.jump_buffer_time = 0.1  # Buffer jump input
        
        # Update physics
        self.update_physics(dt)
        
        # Move horizontally
        self.x += self.velocity_x * dt
        self.handle_platform_collision(entities)
        
        # Move vertically
        self.y += self.velocity_y * dt
        self.handle_platform_collision(entities)
        
        # Check if on ground
        self.check_ground_collision(entities)
        
        # Update animation
        self.update_animation(dt)
        
        # Prevent falling through world
        if self.y > 1000:  # Arbitrary death height
            self.take_damage()
    
    def take_damage(self) -> None:
        """Handle taking damage"""
        if self.invulnerable:
            return
        
        if self.power_level > 0:
            # Lose power-up
            self.power_level -= 1
            self.invulnerable = True
            self.invulnerable_timer = 2.0
        else:
            # Lose life
            self.lives -= 1
            if self.lives <= 0:
                self.destroy()
            else:
                # Respawn logic would go here
                self.invulnerable = True
                self.invulnerable_timer = 3.0
    
    def collect_coin(self) -> None:
        """Collect a coin"""
        self.coins += 1
        self.score += 100
        if self.coins >= 100:
            self.coins = 0
            self.lives += 1
    
    def power_up(self) -> None:
        """Increase power level"""
        if self.power_level < 2:
            self.power_level += 1
            self.score += 1000
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """Render player to screen"""
        if not self.visible:
            return
        
        # Calculate screen position
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Flicker effect when invulnerable
        if self.invulnerable and int(self.invulnerable_timer * 10) % 2:
            return
        
        # Draw simple colored rectangle for now
        color = RED if self.power_level == 2 else BLUE if self.power_level == 1 else WHITE
        pygame.draw.rect(screen, color, (screen_x, screen_y, self.width, self.height))
        
        # Draw facing direction indicator
        if self.facing_right:
            pygame.draw.circle(screen, (255, 255, 0), 
                             (screen_x + self.width - 5, screen_y + 5), 3)
        else:
            pygame.draw.circle(screen, (255, 255, 0), 
                             (screen_x + 5, screen_y + 5), 3)