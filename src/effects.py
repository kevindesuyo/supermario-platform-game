"""
Visual and sound effects system
"""

import pygame
import math
import random
from typing import List, Tuple, Optional
from .entity import Entity
from .constants import LAYER_EFFECTS, WHITE, YELLOW, RED, GREEN, BLUE

class Particle:
    """Individual particle for effects"""
    
    def __init__(self, x: float, y: float, velocity_x: float, velocity_y: float, 
                 color: Tuple[int, int, int], size: float, lifetime: float):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = 300  # Gravity for particles
        
    def update(self, dt: float) -> bool:
        """Update particle, returns False if dead"""
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.velocity_y += self.gravity * dt
        
        self.lifetime -= dt
        return self.lifetime > 0
    
    def render(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """Render particle"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Fade alpha based on lifetime
        alpha_ratio = self.lifetime / self.max_lifetime
        alpha = int(255 * alpha_ratio)
        
        # Create surface with alpha
        particle_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(particle_surface, color_with_alpha, 
                         (int(self.size), int(self.size)), int(self.size))
        
        screen.blit(particle_surface, (screen_x - int(self.size), screen_y - int(self.size)))

class Effect(Entity):
    """Base class for visual effects"""
    
    def __init__(self, x: float, y: float, effect_type: str):
        super().__init__(x, y, 0, 0, "effect")
        self.layer = LAYER_EFFECTS
        self.solid = False
        self.effect_type = effect_type
        self.duration = 1.0
        self.timer = 0.0
        
    def update(self, dt: float, entities: List[Entity]) -> None:
        """Update effect"""
        self.timer += dt
        if self.timer >= self.duration:
            self.destroy()

class ExplosionEffect(Effect):
    """Explosion particle effect"""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int] = YELLOW, 
                 particle_count: int = 20):
        super().__init__(x, y, "explosion")
        self.particles: List[Particle] = []
        self.duration = 2.0
        
        # Create particles
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed - 100  # Slight upward bias
            
            particle_color = (
                min(255, color[0] + random.randint(-50, 50)),
                min(255, color[1] + random.randint(-50, 50)),
                min(255, color[2] + random.randint(-50, 50))
            )
            
            size = random.uniform(2, 6)
            lifetime = random.uniform(0.5, 1.5)
            
            particle = Particle(x, y, velocity_x, velocity_y, particle_color, size, lifetime)
            self.particles.append(particle)
    
    def update(self, dt: float, entities: List[Entity]) -> None:
        """Update explosion particles"""
        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # Remove effect when all particles are gone
        if not self.particles:
            self.destroy()
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """Render explosion particles"""
        for particle in self.particles:
            particle.render(screen, camera_x, camera_y)

class ScorePopup(Effect):
    """Floating score text effect"""
    
    def __init__(self, x: float, y: float, score: int, color: Tuple[int, int, int] = WHITE):
        super().__init__(x, y, "score_popup")
        self.score = score
        self.color = color
        self.duration = 1.5
        self.float_speed = -60  # Negative to float upward
        self.font_size = 24
        
        # Initialize font
        pygame.font.init()
        self.font = pygame.font.Font(None, self.font_size)
        self.text = self.font.render(str(score), True, self.color)
    
    def update(self, dt: float, entities: List[Entity]) -> None:
        """Update floating text"""
        self.y += self.float_speed * dt
        super().update(dt, entities)
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """Render floating text"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Fade alpha based on time
        alpha_ratio = 1.0 - (self.timer / self.duration)
        alpha = int(255 * alpha_ratio)
        
        # Create faded text surface
        faded_text = self.text.copy()
        faded_text.set_alpha(alpha)
        
        screen.blit(faded_text, (screen_x, screen_y))

class TrailEffect(Effect):
    """Trail effect for moving objects"""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int] = WHITE):
        super().__init__(x, y, "trail")
        self.trail_points: List[Tuple[float, float, float]] = []  # x, y, timestamp
        self.color = color
        self.max_trail_length = 10
        self.trail_lifetime = 0.5
        
    def add_point(self, x: float, y: float) -> None:
        """Add a new point to the trail"""
        current_time = pygame.time.get_ticks() / 1000.0
        self.trail_points.append((x, y, current_time))
        
        # Remove old points
        while (len(self.trail_points) > self.max_trail_length or
               (self.trail_points and 
                current_time - self.trail_points[0][2] > self.trail_lifetime)):
            self.trail_points.pop(0)
    
    def update(self, dt: float, entities: List[Entity]) -> None:
        """Update trail"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Remove old points
        self.trail_points = [(x, y, t) for x, y, t in self.trail_points 
                            if current_time - t <= self.trail_lifetime]
        
        # Remove effect if no points
        if not self.trail_points:
            self.destroy()
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """Render trail"""
        if len(self.trail_points) < 2:
            return
        
        current_time = pygame.time.get_ticks() / 1000.0
        
        for i, (x, y, timestamp) in enumerate(self.trail_points):
            screen_x = int(x - camera_x)
            screen_y = int(y - camera_y)
            
            # Calculate alpha based on age and position in trail
            age_ratio = (current_time - timestamp) / self.trail_lifetime
            position_ratio = i / len(self.trail_points)
            alpha = int(255 * (1.0 - age_ratio) * position_ratio)
            
            if alpha > 0:
                size = int(8 * (1.0 - age_ratio))
                if size > 0:
                    trail_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    color_with_alpha = (*self.color, alpha)
                    pygame.draw.circle(trail_surface, color_with_alpha, (size, size), size)
                    screen.blit(trail_surface, (screen_x - size, screen_y - size))

class PowerUpEffect(Effect):
    """Power-up collection effect"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "powerup")
        self.duration = 1.0
        self.rings: List[Tuple[float, Tuple[int, int, int]]] = []
        
        # Create expanding rings
        colors = [WHITE, YELLOW, (255, 215, 0)]  # Gold
        for i, color in enumerate(colors):
            self.rings.append((i * 0.1, color))  # Staggered timing
    
    def update(self, dt: float, entities: List[Entity]) -> None:
        """Update power-up effect"""
        super().update(dt, entities)
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """Render expanding rings"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        for start_time, color in self.rings:
            ring_time = self.timer - start_time
            if ring_time > 0:
                radius = int(ring_time * 100)  # Expand at 100 pixels/second
                alpha = int(255 * max(0, 1.0 - ring_time / self.duration))
                
                if radius < 100 and alpha > 0:
                    ring_surface = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
                    color_with_alpha = (*color, alpha)
                    pygame.draw.circle(ring_surface, color_with_alpha, 
                                     (radius + 2, radius + 2), radius, 3)
                    screen.blit(ring_surface, (screen_x - radius - 2, screen_y - radius - 2))

class SoundManager:
    """Simple sound effect manager"""
    
    def __init__(self):
        self.sounds = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.enabled = True
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init()
        except pygame.error:
            self.enabled = False
            print("Warning: Sound system not available")
    
    def load_sound(self, name: str, filename: str) -> bool:
        """Load a sound effect"""
        if not self.enabled:
            return False
        
        try:
            sound = pygame.mixer.Sound(filename)
            sound.set_volume(self.sfx_volume)
            self.sounds[name] = sound
            return True
        except (pygame.error, FileNotFoundError):
            print(f"Warning: Could not load sound {filename}")
            return False
    
    def play_sound(self, name: str) -> None:
        """Play a sound effect"""
        if self.enabled and name in self.sounds:
            self.sounds[name].play()
    
    def set_sfx_volume(self, volume: float) -> None:
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume)
    
    def play_music(self, filename: str, loops: int = -1) -> bool:
        """Play background music"""
        if not self.enabled:
            return False
        
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)
            return True
        except (pygame.error, FileNotFoundError):
            print(f"Warning: Could not load music {filename}")
            return False
    
    def stop_music(self) -> None:
        """Stop background music"""
        if self.enabled:
            pygame.mixer.music.stop()

class EffectsManager:
    """Manager for visual effects"""
    
    def __init__(self):
        self.effects: List[Effect] = []
        self.sound_manager = SoundManager()
    
    def add_effect(self, effect: Effect) -> None:
        """Add a visual effect"""
        self.effects.append(effect)
    
    def create_explosion(self, x: float, y: float, color: Tuple[int, int, int] = YELLOW, 
                        particle_count: int = 20) -> None:
        """Create explosion effect"""
        effect = ExplosionEffect(x, y, color, particle_count)
        self.add_effect(effect)
    
    def create_score_popup(self, x: float, y: float, score: int, 
                          color: Tuple[int, int, int] = WHITE) -> None:
        """Create floating score text"""
        effect = ScorePopup(x, y, score, color)
        self.add_effect(effect)
    
    def create_powerup_effect(self, x: float, y: float) -> None:
        """Create power-up collection effect"""
        effect = PowerUpEffect(x, y)
        self.add_effect(effect)
    
    def update(self, dt: float) -> None:
        """Update all effects"""
        # Update effects
        for effect in self.effects[:]:
            if effect.active:
                effect.update(dt, [])
            else:
                self.effects.remove(effect)
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """Render all effects"""
        for effect in self.effects:
            if effect.visible:
                effect.render(screen, camera_x, camera_y)
    
    def clear(self) -> None:
        """Clear all effects"""
        self.effects.clear()