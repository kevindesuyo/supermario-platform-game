#!/usr/bin/env python3
"""
Super Mario-like Platform Game
Main game entry point
"""

import pygame
import sys
from src.game_engine import GameEngine
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE

def main():
    """Initialize and run the game"""
    pygame.init()
    
    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    
    # Initialize game engine
    game = GameEngine(screen)
    
    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)
        
        # Update and render
        game.update(dt)
        game.render()
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()