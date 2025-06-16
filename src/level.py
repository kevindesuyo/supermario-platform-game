"""
Level system with tile-based maps
"""

import pygame
from typing import List, Dict, Any, Optional, Tuple
from .entity import Entity
from .constants import (
    TILE_SIZE, ENTITY_PLATFORM, LAYER_PLATFORMS, LAYER_BACKGROUND,
    GROUND_BROWN, GRASS_GREEN, SKY_BLUE, GRAY, DARK_GRAY
)

class Tile:
    """Individual tile in the level"""
    
    def __init__(self, tile_type: str, x: int, y: int, solid: bool = False):
        self.tile_type = tile_type
        self.x = x
        self.y = y
        self.solid = solid
        self.sprite_index = 0
        self.animated = False
        self.animation_speed = 0.1
        self.animation_timer = 0.0
        
class Platform(Entity):
    """Platform entity for collision detection"""
    
    def __init__(self, x: float, y: float, width: int, height: int, tile_type: str = "ground"):
        super().__init__(x, y, width, height, ENTITY_PLATFORM)
        self.layer = LAYER_PLATFORMS
        self.tile_type = tile_type
        
    def update(self, dt: float, entities: List[Entity]) -> None:
        """Platforms don't need to update"""
        pass
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """Render platform"""
        if not self.visible:
            return
        
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Choose color based on tile type
        if self.tile_type == "ground":
            color = GROUND_BROWN
        elif self.tile_type == "grass":
            color = GRASS_GREEN
        elif self.tile_type == "stone":
            color = GRAY
        else:
            color = DARK_GRAY
        
        pygame.draw.rect(screen, color, (screen_x, screen_y, self.width, self.height))
        
        # Draw border for visibility
        pygame.draw.rect(screen, (0, 0, 0), (screen_x, screen_y, self.width, self.height), 1)

class Level:
    """Level manager with tile-based system"""
    
    def __init__(self, width: int, height: int):
        self.width = width  # Width in tiles
        self.height = height  # Height in tiles
        self.pixel_width = width * TILE_SIZE
        self.pixel_height = height * TILE_SIZE
        
        # Tile data
        self.tiles: List[List[Optional[Tile]]] = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(None)
            self.tiles.append(row)
        
        # Background properties
        self.background_color = SKY_BLUE
        self.parallax_layers: List[Dict[str, Any]] = []
        
        # Level properties
        self.spawn_point = (100, 100)
        self.goal_point = (self.pixel_width - 100, 100)
        self.time_limit = 400  # seconds
        
        # Entity spawn data
        self.enemy_spawns: List[Dict[str, Any]] = []
        self.powerup_spawns: List[Dict[str, Any]] = []
        self.collectible_spawns: List[Dict[str, Any]] = []
        
    def set_tile(self, x: int, y: int, tile_type: str, solid: bool = False) -> None:
        """Set a tile at grid position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = Tile(tile_type, x, y, solid)
    
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at grid position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
    
    def get_tile_at_pixel(self, pixel_x: float, pixel_y: float) -> Optional[Tile]:
        """Get tile at pixel position"""
        grid_x = int(pixel_x // TILE_SIZE)
        grid_y = int(pixel_y // TILE_SIZE)
        return self.get_tile(grid_x, grid_y)
    
    def world_to_grid(self, pixel_x: float, pixel_y: float) -> Tuple[int, int]:
        """Convert world coordinates to grid coordinates"""
        return (int(pixel_x // TILE_SIZE), int(pixel_y // TILE_SIZE))
    
    def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """Convert grid coordinates to world coordinates"""
        return (grid_x * TILE_SIZE, grid_y * TILE_SIZE)
    
    def add_enemy_spawn(self, x: float, y: float, enemy_type: str, **kwargs) -> None:
        """Add enemy spawn point"""
        self.enemy_spawns.append({
            'x': x, 'y': y, 'type': enemy_type, **kwargs
        })
    
    def add_powerup_spawn(self, x: float, y: float, powerup_type: str, **kwargs) -> None:
        """Add power-up spawn point"""
        self.powerup_spawns.append({
            'x': x, 'y': y, 'type': powerup_type, **kwargs
        })
    
    def add_collectible_spawn(self, x: float, y: float, collectible_type: str, **kwargs) -> None:
        """Add collectible spawn point"""
        self.collectible_spawns.append({
            'x': x, 'y': y, 'type': collectible_type, **kwargs
        })
    
    def generate_platforms(self) -> List[Platform]:
        """Generate platform entities from solid tiles"""
        platforms = []
        
        # Group adjacent solid tiles into larger platforms for better performance
        visited = set()
        
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in visited:
                    tile = self.get_tile(x, y)
                    if tile and tile.solid:
                        # Find the extent of this platform
                        platform_tiles = self._flood_fill_platform(x, y, visited)
                        if platform_tiles:
                            # Create platform from grouped tiles
                            min_x = min(tx for tx, ty in platform_tiles)
                            max_x = max(tx for tx, ty in platform_tiles)
                            min_y = min(ty for tx, ty in platform_tiles)
                            max_y = max(ty for tx, ty in platform_tiles)
                            
                            # For now, create individual platforms for each tile
                            # TODO: Optimize by merging adjacent tiles
                            for tx, ty in platform_tiles:
                                world_x, world_y = self.grid_to_world(tx, ty)
                                tile_obj = self.get_tile(tx, ty)
                                platform = Platform(world_x, world_y, TILE_SIZE, TILE_SIZE, 
                                                   tile_obj.tile_type if tile_obj else "ground")
                                platforms.append(platform)
        
        return platforms
    
    def _flood_fill_platform(self, start_x: int, start_y: int, visited: set) -> List[Tuple[int, int]]:
        """Flood fill to find connected solid tiles"""
        if (start_x, start_y) in visited:
            return []
        
        tile = self.get_tile(start_x, start_y)
        if not tile or not tile.solid:
            return []
        
        # Simple flood fill for connected solid tiles of the same type
        stack = [(start_x, start_y)]
        platform_tiles = []
        tile_type = tile.tile_type
        
        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            
            current_tile = self.get_tile(x, y)
            if not current_tile or not current_tile.solid or current_tile.tile_type != tile_type:
                continue
            
            visited.add((x, y))
            platform_tiles.append((x, y))
            
            # Add adjacent tiles (4-directional)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in visited:
                    stack.append((nx, ny))
        
        return platform_tiles
    
    def render_background(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """Render background layers"""
        # Fill with background color
        screen.fill(self.background_color)
        
        # Render parallax layers
        for layer in self.parallax_layers:
            # TODO: Implement parallax scrolling
            pass
    
    def render_tiles(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """Render non-solid decorative tiles"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Calculate visible tile range
        start_x = max(0, int(camera_x // TILE_SIZE) - 1)
        end_x = min(self.width, int((camera_x + screen_width) // TILE_SIZE) + 2)
        start_y = max(0, int(camera_y // TILE_SIZE) - 1)
        end_y = min(self.height, int((camera_y + screen_height) // TILE_SIZE) + 2)
        
        # Render visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.get_tile(x, y)
                if tile and not tile.solid:  # Only render decorative tiles
                    world_x, world_y = self.grid_to_world(x, y)
                    screen_x = int(world_x - camera_x)
                    screen_y = int(world_y - camera_y)
                    
                    # Simple colored square for now
                    if tile.tile_type == "decoration":
                        pygame.draw.rect(screen, (255, 255, 0), 
                                       (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
    
    def update(self, dt: float) -> None:
        """Update level (animate tiles, etc.)"""
        # Update animated tiles
        for y in range(self.height):
            for x in range(self.width):
                tile = self.get_tile(x, y)
                if tile and tile.animated:
                    tile.animation_timer += dt
                    if tile.animation_timer >= tile.animation_speed:
                        tile.animation_timer = 0
                        tile.sprite_index = (tile.sprite_index + 1) % 4  # Assume 4 frame animation

class LevelBuilder:
    """Helper class for building levels"""
    
    @staticmethod
    def create_test_level() -> Level:
        """Create a simple test level"""
        level = Level(50, 25)  # 50x25 tiles
        
        # Create ground
        for x in range(50):
            level.set_tile(x, 20, "ground", True)
            level.set_tile(x, 21, "ground", True)
            level.set_tile(x, 22, "ground", True)
            level.set_tile(x, 23, "ground", True)
            level.set_tile(x, 24, "ground", True)
        
        # Create some platforms
        for x in range(10, 15):
            level.set_tile(x, 15, "grass", True)
        
        for x in range(20, 25):
            level.set_tile(x, 12, "stone", True)
        
        for x in range(30, 35):
            level.set_tile(x, 18, "grass", True)
        
        # Create some walls
        for y in range(10, 20):
            level.set_tile(40, y, "stone", True)
        
        # Add spawn points
        level.spawn_point = (50, 19 * TILE_SIZE)
        level.goal_point = (45 * TILE_SIZE, 19 * TILE_SIZE)
        
        # Add enemy spawns
        level.add_enemy_spawn(300, 19 * TILE_SIZE, "goomba")
        level.add_enemy_spawn(600, 19 * TILE_SIZE, "koopa")
        level.add_enemy_spawn(900, 19 * TILE_SIZE, "goomba")
        
        # Add power-up spawns
        level.add_powerup_spawn(400, 14 * TILE_SIZE, "mushroom")
        level.add_powerup_spawn(800, 11 * TILE_SIZE, "fire_flower")
        
        # Add collectible spawns
        for i in range(5):
            level.add_collectible_spawn(200 + i * 100, 19 * TILE_SIZE, "coin")
        
        return level
    
    @staticmethod
    def load_level_from_file(filename: str) -> Optional[Level]:
        """Load level from file (TODO: implement file format)"""
        # TODO: Implement level loading from file
        return None
    
    @staticmethod
    def save_level_to_file(level: Level, filename: str) -> bool:
        """Save level to file (TODO: implement file format)"""
        # TODO: Implement level saving to file
        return False