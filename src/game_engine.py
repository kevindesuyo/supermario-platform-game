"""
Main game engine and state management
"""

import pygame
from typing import List, Optional
from .constants import (
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER,
    SCREEN_WIDTH, SCREEN_HEIGHT, SKY_BLUE, WHITE, BLACK, RED, GREEN,
    KEYS_PAUSE
)
from .entity import EntityManager
from .player import Player
from .level import Level, LevelBuilder
from .enemies import EnemySpawner
from .effects import EffectsManager
from .collectibles import Coin, QuestionBlock, BrickBlock
from .powerups import Mushroom, FireFlower
from .goal import GoalFlag

class Camera:
    """Simple camera system for following the player"""
    
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.smooth_factor = 5.0
        
        # Camera bounds
        self.min_x = 0
        self.max_x = 0
        self.min_y = 0
        self.max_y = 0
    
    def set_bounds(self, min_x: float, max_x: float, min_y: float, max_y: float) -> None:
        """Set camera movement bounds"""
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
    
    def follow_target(self, target_x: float, target_y: float, dt: float) -> None:
        """Smoothly follow a target"""
        # Center camera on target
        self.target_x = target_x - SCREEN_WIDTH // 2
        self.target_y = target_y - SCREEN_HEIGHT // 2
        
        # Apply bounds
        self.target_x = max(self.min_x, min(self.max_x - SCREEN_WIDTH, self.target_x))
        self.target_y = max(self.min_y, min(self.max_y - SCREEN_HEIGHT, self.target_y))
        
        # Smooth movement
        self.x += (self.target_x - self.x) * self.smooth_factor * dt
        self.y += (self.target_y - self.y) * self.smooth_factor * dt

class GameState:
    """Base class for game states"""
    
    def __init__(self, game_engine: 'GameEngine'):
        self.game_engine = game_engine
    
    def enter(self) -> None:
        """Called when entering this state"""
        pass
    
    def exit(self) -> None:
        """Called when exiting this state"""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events"""
        pass
    
    def update(self, dt: float) -> None:
        """Update state logic"""
        pass
    
    def render(self, screen: pygame.Surface) -> None:
        """Render state"""
        pass

class MenuState(GameState):
    """Main menu state"""
    
    def __init__(self, game_engine: 'GameEngine'):
        super().__init__(game_engine)
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.selected_option = 0
        self.menu_options = ["Start Game", "Quit"]
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle menu input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                if self.selected_option == 0:  # Start Game
                    self.game_engine.change_state(STATE_PLAYING)
                elif self.selected_option == 1:  # Quit
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def render(self, screen: pygame.Surface) -> None:
        """Render menu"""
        screen.fill(SKY_BLUE)
        
        # Title
        title_text = self.font_large.render("Super Mario Adventure", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(title_text, title_rect)
        
        # Menu options
        for i, option in enumerate(self.menu_options):
            color = WHITE if i == self.selected_option else (200, 200, 200)
            option_text = self.font_medium.render(option, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, 350 + i * 60))
            screen.blit(option_text, option_rect)
        
        # Instructions
        instruction_font = pygame.font.Font(None, 24)
        instruction_text = instruction_font.render("Use arrow keys and ENTER to select", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
        screen.blit(instruction_text, instruction_rect)

class PlayingState(GameState):
    """Main gameplay state"""
    
    def __init__(self, game_engine: 'GameEngine'):
        super().__init__(game_engine)
        self.entity_manager = EntityManager()
        self.effects_manager = EffectsManager()
        self.camera = Camera()
        
        self.level: Optional[Level] = None
        self.player: Optional[Player] = None
        
        # Game state
        self.score = 0
        self.time_remaining = 400
        self.level_complete = False
        self.level_intro_timer = 0.0
        self.level_complete_timer = 0.0
        
        # UI
        pygame.font.init()
        self.ui_font = pygame.font.Font(None, 36)
    
    def enter(self) -> None:
        """Initialize gameplay"""
        # Create test level
        self.level = LevelBuilder.create_test_level()
        
        # Create player
        spawn_x, spawn_y = self.level.spawn_point
        self.player = Player(spawn_x, spawn_y)
        self.entity_manager.add_entity(self.player)
        
        # Generate platforms from level
        platforms = self.level.generate_platforms()
        for platform in platforms:
            self.entity_manager.add_entity(platform)
        
        # Spawn enemies
        for spawn_data in self.level.enemy_spawns:
            enemy = EnemySpawner.create_enemy(
                spawn_data['type'], spawn_data['x'], spawn_data['y']
            )
            self.entity_manager.add_entity(enemy)

        # Spawn collectibles
        for spawn_data in self.level.collectible_spawns:
            if spawn_data['type'] == 'coin':
                self.entity_manager.add_entity(Coin(spawn_data['x'], spawn_data['y']))

        # Spawn power-ups (placed in the world; blocks can also produce them)
        for spawn_data in self.level.powerup_spawns:
            if spawn_data['type'] == 'mushroom':
                self.entity_manager.add_entity(Mushroom(spawn_data['x'], spawn_data['y']))
            elif spawn_data['type'] == 'fire_flower':
                self.entity_manager.add_entity(FireFlower(spawn_data['x'], spawn_data['y']))

        # Add a few blocks for interaction
        # Question blocks above first platform row
        self.entity_manager.add_entity(QuestionBlock(12 * 32, 14 * 32, contains='coin'))
        self.entity_manager.add_entity(QuestionBlock(13 * 32, 14 * 32, contains='mushroom'))
        self.entity_manager.add_entity(BrickBlock(14 * 32, 14 * 32))

        # Goal flag
        gx, gy = self.level.goal_point
        self.entity_manager.add_entity(GoalFlag(gx, gy))
        
        # Set camera bounds
        self.camera.set_bounds(0, self.level.pixel_width, 0, self.level.pixel_height)
        
        # Reset game state
        self.score = self.player.score if self.player else 0
        self.time_remaining = self.level.time_limit
        self.level_complete = False
        self.level_intro_timer = 1.0
        self.level_complete_timer = 0.0
    
    def exit(self) -> None:
        """Clean up gameplay"""
        self.entity_manager.clear()
        self.effects_manager.clear()
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle gameplay input"""
        if event.type == pygame.KEYDOWN:
            if event.key in KEYS_PAUSE:
                self.game_engine.change_state(STATE_PAUSED)
            elif event.key == pygame.K_r:
                # Restart level
                self.exit()
                self.enter()
    
    def update(self, dt: float) -> None:
        """Update gameplay"""
        if not self.player or not self.player.active:
            # Player died
            self.game_engine.change_state(STATE_GAME_OVER)
            return
        
        # Update time
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.player.take_damage()  # Time up
        
        # Intro freeze: small delay before control
        if self.level_intro_timer > 0:
            self.level_intro_timer -= dt
        else:
            # Respawn handling
            if getattr(self.player, 'needs_respawn', False):
                if self.level:
                    sx, sy = self.level.spawn_point
                    self.player.set_position(sx, sy)
                    self.player.velocity_x = 0
                    self.player.velocity_y = 0
                    self.player.needs_respawn = False

            # Update entities
            self.entity_manager.update(dt)
        
        # Update effects
        self.effects_manager.update(dt)
        
        # Update camera to follow player
        if self.player:
            self.camera.follow_target(self.player.center_x, self.player.center_y, dt)
        
        # Check player-enemy collisions
        if self.player and self.level_intro_timer <= 0:
            enemies = self.entity_manager.get_entities_by_type("enemy")
            for enemy in enemies:
                if self.player.collides_with(enemy):
                    self.handle_player_enemy_collision(enemy)

            # Check goal
            for e in self.entity_manager.entities:
                if getattr(e, 'entity_type', '') == 'goal' and self.player.collides_with(e):
                    self.level_complete = True
                    self.level_complete_timer = 2.0
        
        # Update score
        if self.player:
            self.score = self.player.score
        
        # Handle level completion countdown and bonus
        if self.level_complete:
            if self.level_complete_timer > 0:
                self.level_complete_timer -= dt
                if self.level_complete_timer <= 0 and self.player:
                    # Award time bonus and return to menu
                    time_bonus = int(self.time_remaining) * 50
                    self.player.score += time_bonus
                    self.effects_manager.create_score_popup(
                        self.player.x, self.player.y - 50, time_bonus, GREEN
                    )
                    self.game_engine.change_state(STATE_MENU)
    
    def handle_player_enemy_collision(self, enemy) -> None:
        """Handle collision between player and enemy"""
        if not self.player:
            return
        
        # Check if player is stomping enemy (coming from above)
        if (self.player.velocity_y > 0 and 
            self.player.bottom <= enemy.y + 10):
            # Player stomps enemy
            points = enemy.stomp()
            if points > 0:
                self.player.score += points
                self.effects_manager.create_score_popup(
                    enemy.center_x, enemy.y - 20, points, WHITE
                )
                self.effects_manager.create_explosion(
                    enemy.center_x, enemy.center_y, (255, 100, 0), 15
                )
            
            # Bounce player
            self.player.velocity_y = -300
        else:
            # Player takes damage
            self.player.take_damage()
            if self.player.active:
                # Create damage effect
                self.effects_manager.create_explosion(
                    self.player.center_x, self.player.center_y, RED, 10
                )
    
    def render(self, screen: pygame.Surface) -> None:
        """Render gameplay"""
        # Render level background
        if self.level:
            self.level.render_background(screen, self.camera.x, self.camera.y)
            self.level.render_tiles(screen, self.camera.x, self.camera.y)
        
        # Render entities
        self.entity_manager.render(screen, self.camera.x, self.camera.y)
        
        # Render effects
        self.effects_manager.render(screen, self.camera.x, self.camera.y)
        
        # Render UI
        self.render_ui(screen)
    
    def render_ui(self, screen: pygame.Surface) -> None:
        """Render game UI"""
        # Score
        score_text = self.ui_font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Time
        time_text = self.ui_font.render(f"Time: {int(self.time_remaining):03d}", True, WHITE)
        screen.blit(time_text, (10, 50))
        
        # Lives
        if self.player:
            lives_text = self.ui_font.render(f"Lives: {self.player.lives}", True, WHITE)
            screen.blit(lives_text, (10, 90))
            
            # Coins
            coins_text = self.ui_font.render(f"Coins: {self.player.coins}", True, WHITE)
            screen.blit(coins_text, (10, 130))
        
        # Level complete message
        if self.level_complete:
            complete_text = self.ui_font.render("Level Complete!", True, GREEN)
            complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(complete_text, complete_rect)
        elif self.level_intro_timer > 0:
            ready_text = self.ui_font.render("Ready!", True, WHITE)
            ready_rect = ready_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(ready_text, ready_rect)

class PausedState(GameState):
    """Paused game state"""
    
    def __init__(self, game_engine: 'GameEngine'):
        super().__init__(game_engine)
        pygame.font.init()
        self.font = pygame.font.Font(None, 72)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pause input"""
        if event.type == pygame.KEYDOWN:
            if event.key in KEYS_PAUSE:
                self.game_engine.change_state(STATE_PLAYING)
    
    def render(self, screen: pygame.Surface) -> None:
        """Render pause overlay"""
        # Darken screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_text, pause_rect)
        
        # Instructions
        instruction_font = pygame.font.Font(None, 36)
        instruction_text = instruction_font.render("Press ESC or P to resume", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(instruction_text, instruction_rect)

class GameOverState(GameState):
    """Game over state"""
    
    def __init__(self, game_engine: 'GameEngine'):
        super().__init__(game_engine)
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.restart_timer = 3.0
    
    def enter(self) -> None:
        """Initialize game over"""
        self.restart_timer = 3.0
    
    def update(self, dt: float) -> None:
        """Update game over timer"""
        self.restart_timer -= dt
        if self.restart_timer <= 0:
            self.game_engine.change_state(STATE_MENU)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle game over input"""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self.game_engine.change_state(STATE_MENU)
    
    def render(self, screen: pygame.Surface) -> None:
        """Render game over screen"""
        screen.fill(BLACK)
        
        # Game over text
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, game_over_rect)
        
        # Instructions
        if self.restart_timer > 0:
            timer_text = self.font_medium.render(f"Returning to menu in {int(self.restart_timer) + 1}...", 
                                               True, WHITE)
        else:
            timer_text = self.font_medium.render("Press ENTER to return to menu", True, WHITE)
        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(timer_text, timer_rect)

class GameEngine:
    """Main game engine managing states and core systems"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.current_state = STATE_MENU
        self.states = {
            STATE_MENU: MenuState(self),
            STATE_PLAYING: PlayingState(self),
            STATE_PAUSED: PausedState(self),
            STATE_GAME_OVER: GameOverState(self)
        }
        
        # Initialize with menu state
        self.states[self.current_state].enter()
    
    def change_state(self, new_state: int) -> None:
        """Change game state"""
        if new_state in self.states and new_state != self.current_state:
            # Exit current state
            self.states[self.current_state].exit()
            
            # Enter new state
            self.current_state = new_state
            self.states[self.current_state].enter()
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events"""
        self.states[self.current_state].handle_event(event)
    
    def update(self, dt: float) -> None:
        """Update current state"""
        self.states[self.current_state].update(dt)
    
    def render(self) -> None:
        """Render current state"""
        self.states[self.current_state].render(self.screen)
