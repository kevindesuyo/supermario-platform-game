# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Super Mario-like platform game written in Python using Pygame. The game features:
- Entity-Component-System architecture
- State-based game management
- Physics-based movement and collision detection
- Multiple game states (Menu, Playing, Paused, Game Over)
- Smooth camera system with player following

## Knowledge Management System

This project uses a structured knowledge management system in the `.claude/` directory to maintain context and technical insights:

### `.claude/context.md`
Contains project background, goals, technology stack, and current constraints.

### `.claude/project-knowledge.md`
Documents technical insights, architectural decisions, implementation patterns, and libraries used.

### `.claude/project-improvements.md`
Tracks improvement history, problem-solving approaches, and lessons learned from development.

### `.claude/common-patterns.md`
Stores frequently used command templates and implementation patterns for common tasks.

### `.claude/debug-log.md`
Important debugging records, common issues, and troubleshooting procedures.

### `.claude/debug/`
Directory for managing debugging information:
- `sessions/` - Session-specific temporary logs
- `temp-logs/` - Working temporary files
- `archive/` - Resolved issue storage

## Core Architecture

The codebase follows a modular Entity-Component-System structure:

- `main.py` - Game entry point and main loop
- `src/constants.py` - Global constants and configuration
- `src/game_engine.py` - Game state management and main engine
- `src/entity.py` - Base entity system and entity manager
- `src/player.py` - Player entity implementation
- `src/enemies.py` - Enemy entities and AI behavior
- `src/level.py` - Level design and management
- `src/effects.py` - Visual effects and particles

### Game State System
The game uses a state machine with these states:
- `STATE_MENU` (0) - Main menu
- `STATE_PLAYING` (1) - Active gameplay
- `STATE_PAUSED` (2) - Game paused
- `STATE_GAME_OVER` (3) - Game over screen

### Entity System
All game entities inherit from the `Entity` base class with:
- Component-based architecture for flexible feature addition
- Efficient collision detection using pygame.Rect
- Layer-based rendering system
- Physics integration with gravity and movement

## Running the Game

To run the game:
```bash
python main.py
```

Requirements:
- Python 3.x
- Pygame 2.1.0+

Install dependencies:
```bash
pip install -r requirements.txt
```

## Development Guidelines

### Code Style
- Follow the existing patterns in the codebase
- Use type hints for better code maintainability
- Implement proper error handling for resource loading
- Maintain the Entity-Component-System architecture

### Performance Considerations
- Use object pooling for frequently created/destroyed objects
- Implement efficient collision detection for large numbers of entities
- Optimize rendering by culling off-screen objects
- Monitor frame rate and memory usage during development

### Testing
- Test the game by running through different game modes
- Verify collision detection works correctly
- Check camera movement and boundary conditions
- Ensure proper state transitions

## Important Implementation Notes

- Game objects use Pygame's Rect system for collision detection
- Camera system provides smooth following with configurable parameters
- Entity manager handles efficient object lifecycle management
- State system ensures proper initialization and cleanup
- Physics system implements realistic gravity and movement

The game supports keyboard controls (WASD/Arrow keys for movement, Space for jump, ESC for pause) and handles various game modes with proper state management.

When making changes, ensure compatibility with the existing architecture and maintain the performance characteristics of the game.