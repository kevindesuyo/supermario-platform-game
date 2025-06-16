"""
Game constants and configuration
"""

# Screen settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "Super Mario Adventure"

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)

# Sky colors
SKY_BLUE = (135, 206, 250)
GROUND_BROWN = (139, 69, 19)
GRASS_GREEN = (34, 139, 34)

# Game physics
GRAVITY = 1200  # pixels per second squared
TERMINAL_VELOCITY = 800  # max falling speed
JUMP_SPEED = -600  # negative because Y axis is inverted

# Player settings
PLAYER_SPEED = 200  # pixels per second
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 32
PLAYER_ACCELERATION = 1000
PLAYER_FRICTION = 800

# Tile settings
TILE_SIZE = 32

# Game states
STATE_MENU = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_GAME_OVER = 3

# Entity types
ENTITY_PLAYER = "player"
ENTITY_ENEMY = "enemy"
ENTITY_POWERUP = "powerup"
ENTITY_PLATFORM = "platform"
ENTITY_PROJECTILE = "projectile"

# Layer system for rendering
LAYER_BACKGROUND = 0
LAYER_PLATFORMS = 1
LAYER_ENTITIES = 2
LAYER_PLAYER = 3
LAYER_EFFECTS = 4
LAYER_UI = 5

# Import pygame for key constants
import pygame

# Input keys
KEYS_LEFT = [pygame.K_LEFT, pygame.K_a]
KEYS_RIGHT = [pygame.K_RIGHT, pygame.K_d]
KEYS_JUMP = [pygame.K_SPACE, pygame.K_UP, pygame.K_w]
KEYS_RUN = [pygame.K_LSHIFT, pygame.K_RSHIFT]
KEYS_PAUSE = [pygame.K_ESCAPE, pygame.K_p]