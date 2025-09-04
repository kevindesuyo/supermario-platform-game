# Super Mario Adventure

A Super Mario-like platform game built with Python and Pygame, designed with extensibility and modularity in mind.

This repository now includes a more playable core loop with collectibles, power-ups, a goal flag, and basic polish to feel closer to a game (roughly a 40% milestone).

## Features

- **Modular Entity System**: Extensible architecture for game objects
- **Physics-based Movement**: Realistic platformer physics with gravity, jumping, and collision detection
- **Multiple Enemy Types**: Various AI behaviors including Goombas, Koopas, Piranha Plants, and Flying enemies
- **Level System**: Tile-based level design with platform generation
- **Collectibles & Power-ups (new)**: Coins, question/brick blocks, mushroom and fire-flower power-ups
- **Goal Flag (new)**: Reach the flag to complete the level and earn a time bonus
- **UI/States Polish (new)**: Start countdown, pause overlay, level-complete flow, restart with `R`
- **Visual Effects**: Particle systems, explosions, score popups, and trails
- **Sound System**: Integrated sound manager for music and effects (optional; assets not bundled)
- **State Management**: Clean separation between menu, gameplay, pause, and game over states
- **Camera System**: Smooth camera following with bounds

## Architecture

The game follows a modular architecture designed for easy extension:

### Core Components

- **Entity System** (`src/entity.py`): Base classes for all game objects with component support
- **Game Engine** (`src/game_engine.py`): State management and main game loop
- **Player** (`src/player.py`): Player character with advanced platformer physics
- **Level System** (`src/level.py`): Tile-based level creation and management
- **Enemies** (`src/enemies.py`): Various enemy types with different AI behaviors
- **Effects System** (`src/effects.py`): Visual effects and sound management

### Game States

- **Menu State**: Main menu with navigation
- **Playing State**: Core gameplay with entity management
- **Paused State**: Game pause overlay
- **Game Over State**: End game screen with restart option

### Entity Types

- **Player**: Advanced physics with jump buffering, coyote time, and power-ups
- **Enemies**: Multiple types with unique behaviors
  - Goomba: Simple walking enemy
  - Koopa: Shell-based enemy with kick mechanics
  - Piranha Plant: Pop-up enemy from pipes
  - Flying Enemy: Sine wave movement pattern
- **Platforms**: Generated from level tiles with collision detection
- **Effects**: Visual feedback system

## Controls

- **Movement**: A/D or Arrow Keys (Left/Right)
- **Jump**: W/Space/Up Arrow
- **Run**: Hold Shift
- **Pause**: ESC or P
- **Restart Level**: R

## Installation and Setup

1. Install Python 3.9+ (3.12 tested)
2. (Recommended) Create a virtual environment:
   - Windows (PowerShell):
     - `python -m venv .venv`
     - `.\.venv\Scripts\activate`
   - macOS/Linux:
     - `python -m venv .venv`
     - `source .venv/bin/activate`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Run the game:
   - `python main.py`

## Extending the Game

The architecture is designed for easy extension:

### Adding New Enemy Types

1. Create a new class inheriting from `Enemy` in `src/enemies.py`
2. Implement `update_ai()` method for custom behavior
3. Add to `EnemySpawner.create_enemy()` method
4. Use in level spawn data

### Creating New Levels

1. Use `LevelBuilder` class to create custom levels
2. Define tile layouts with `set_tile()`
3. Add enemy, power-up, and collectible spawn points
4. Generate platforms with `generate_platforms()`

### Adding Visual Effects

1. Create new effect classes inheriting from `Effect`
2. Implement custom `update()` and `render()` methods
3. Add factory methods to `EffectsManager`
4. Use throughout the game for feedback

### Adding Game States

1. Create new state class inheriting from `GameState`
2. Implement required methods (`enter`, `exit`, `update`, `render`, `handle_event`)
3. Add to `GameEngine.states` dictionary
4. Use `change_state()` to transition

## Technical Features

- **Component System**: Entities can have modular components attached
- **Collision Detection**: Rectangle-based collision with side detection
- **Physics Simulation**: Gravity, acceleration, friction, and terminal velocity
- **Animation Support**: Built-in animation timer and state management
- **Particle System**: Flexible particle effects for explosions and trails
- **Sound Integration**: pygame.mixer integration with volume control
- **Camera System**: Smooth following camera with bounds checking
- **Performance Optimized**: Efficient rendering with layer sorting and culling

## Future Expansion Ideas

- **Power-up System**: Star power-up, invincibility chain scoring
- **Collectibles**: Hidden blocks, bonus areas, 1-up mushrooms
- **Level Editor**: In-game level creation tools
- **Multiplayer**: Split-screen or network multiplayer
- **Boss Enemies**: Large enemies with multiple phases
- **Moving Platforms**: Elevators, conveyor belts, rotating platforms
- **Weather Effects**: Rain, snow, wind affecting gameplay
- **Save System**: Progress saving and level unlocking
- **Sprite Graphics**: Replace colored rectangles with actual sprites
- **Background Music**: Dynamic music system with level themes

The modular design makes all of these features straightforward to implement without major architectural changes.
