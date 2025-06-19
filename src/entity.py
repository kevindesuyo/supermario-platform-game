"""
Base entity system for game objects
"""

import pygame
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any

class Entity(ABC):
    """Base class for all game entities"""
    
    def __init__(self, x: float, y: float, width: int, height: int, entity_type: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.entity_type = entity_type
        
        # Physics properties
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.acceleration_x = 0.0
        self.acceleration_y = 0.0
        
        # State flags
        self.active = True
        self.visible = True
        self.solid = True
        self.on_ground = False
        
        # Rendering properties
        self.layer = 2  # Default to entity layer
        self.flip_x = False
        self.flip_y = False
        self.scale = 1.0
        
        # Animation properties
        self.animation_frame = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.1
        
        # Component storage
        self.components: Dict[str, Any] = {}
        
    @property
    def rect(self) -> pygame.Rect:
        """Get collision rectangle"""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    @property
    def center_x(self) -> float:
        """Get center X coordinate"""
        return self.x + self.width / 2
    
    @property
    def center_y(self) -> float:
        """Get center Y coordinate"""
        return self.y + self.height / 2
    
    @property
    def bottom(self) -> float:
        """Get bottom Y coordinate"""
        return self.y + self.height
    
    @property
    def right(self) -> float:
        """Get right X coordinate"""
        return self.x + self.width
    
    def add_component(self, name: str, component: Any) -> None:
        """Add a component to this entity"""
        self.components[name] = component
    
    def get_component(self, name: str) -> Optional[Any]:
        """Get a component by name"""
        return self.components.get(name)
    
    def has_component(self, name: str) -> bool:
        """Check if entity has a component"""
        return name in self.components
    
    def move(self, dx: float, dy: float) -> None:
        """Move entity by offset"""
        self.x += dx
        self.y += dy
    
    def set_position(self, x: float, y: float) -> None:
        """Set absolute position"""
        self.x = x
        self.y = y
    
    def collides_with(self, other: 'Entity') -> bool:
        """Check collision with another entity"""
        if not (self.active and other.active and self.solid and other.solid):
            return False
        return self.rect.colliderect(other.rect)
    
    def get_collision_side(self, other: 'Entity') -> Optional[str]:
        """Get which side of this entity is colliding with other"""
        if not self.collides_with(other):
            return None
        
        # Calculate overlap amounts
        left_overlap = self.right - other.x
        right_overlap = other.right - self.x
        top_overlap = self.bottom - other.y
        bottom_overlap = other.bottom - self.y
        
        # Ensure positive overlaps
        left_overlap = max(0, left_overlap)
        right_overlap = max(0, right_overlap)
        top_overlap = max(0, top_overlap)
        bottom_overlap = max(0, bottom_overlap)
        
        # Find minimum overlap (avoid zero values)
        overlaps = [o for o in [left_overlap, right_overlap, top_overlap, bottom_overlap] if o > 0]
        if not overlaps:
            return None
            
        min_overlap = min(overlaps)
        
        if min_overlap == left_overlap:
            return "right"  # Other is to the right
        elif min_overlap == right_overlap:
            return "left"   # Other is to the left
        elif min_overlap == top_overlap:
            return "bottom" # Other is below
        else:
            return "top"    # Other is above
    
    @abstractmethod
    def update(self, dt: float, entities: List['Entity']) -> None:
        """Update entity logic"""
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """Render entity to screen"""
        pass
    
    def destroy(self) -> None:
        """Mark entity for removal"""
        self.active = False

class EntityManager:
    """Manages collections of entities"""
    
    def __init__(self):
        self.entities: List[Entity] = []
        self.entities_to_add: List[Entity] = []
        self.entities_to_remove: List[Entity] = []
    
    def add_entity(self, entity: Entity) -> None:
        """Add entity to manager"""
        self.entities_to_add.append(entity)
    
    def remove_entity(self, entity: Entity) -> None:
        """Remove entity from manager"""
        if entity in self.entities:
            self.entities_to_remove.append(entity)
    
    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """Get all entities of a specific type"""
        return [e for e in self.entities if e.entity_type == entity_type and e.active]
    
    def get_entities_in_area(self, x: float, y: float, width: float, height: float) -> List[Entity]:
        """Get all entities in a specific area"""
        area_rect = pygame.Rect(int(x), int(y), int(width), int(height))
        return [e for e in self.entities if e.active and e.rect.colliderect(area_rect)]
    
    def update(self, dt: float) -> None:
        """Update all entities"""
        # Add new entities
        self.entities.extend(self.entities_to_add)
        self.entities_to_add.clear()
        
        # Remove dead entities
        for entity in self.entities_to_remove:
            if entity in self.entities:
                self.entities.remove(entity)
        self.entities_to_remove.clear()
        
        # Remove inactive entities
        self.entities = [e for e in self.entities if e.active]
        
        # Update all entities
        for entity in self.entities:
            entity.update(dt, self.entities)
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """Render all entities sorted by layer"""
        # Sort by layer for proper rendering order
        sorted_entities = sorted([e for e in self.entities if e.visible], 
                               key=lambda e: e.layer)
        
        for entity in sorted_entities:
            entity.render(screen, camera_x, camera_y)
    
    def clear(self) -> None:
        """Remove all entities"""
        self.entities.clear()
        self.entities_to_add.clear()
        self.entities_to_remove.clear()