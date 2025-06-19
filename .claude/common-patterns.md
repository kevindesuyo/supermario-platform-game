# 共通パターンとコマンドテンプレート

## よく使用するコマンドパターン

### プロジェクト実行
```bash
# ゲームの起動
python main.py

# 仮想環境でのテスト実行
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python main.py
```

### 開発・デバッグ用コマンド
```bash
# Python構文チェック
python -m py_compile main.py
python -m py_compile src/*.py

# コードフォーマット（将来的に追加予定）
# black src/ main.py
# flake8 src/ main.py
```

## 実装パターンテンプレート

### 新しいエンティティの作成
```python
from src.entity import Entity
from src.constants import ENTITY_[TYPE]

class NewEntity(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, width, height, ENTITY_[TYPE])
        
        # エンティティ固有のプロパティ
        self.health = 100
        self.speed = 200
        
        # 物理プロパティの設定
        self.solid = True
        self.layer = LAYER_ENTITIES
    
    def update(self, dt: float, entities: List[Entity]) -> None:
        """エンティティの更新ロジック"""
        # 物理演算
        self.velocity_y += GRAVITY * dt
        self.velocity_y = min(self.velocity_y, TERMINAL_VELOCITY)
        
        # 移動
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # 衝突検出
        platforms = [e for e in entities if e.entity_type == ENTITY_PLATFORM]
        for platform in platforms:
            if self.collides_with(platform):
                self.handle_platform_collision(platform)
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """エンティティの描画"""
        if not self.visible:
            return
        
        # カメラオフセットを適用
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # 描画範囲チェック
        if (screen_x + self.width < 0 or screen_x > SCREEN_WIDTH or
            screen_y + self.height < 0 or screen_y > SCREEN_HEIGHT):
            return
        
        # 実際の描画処理
        pygame.draw.rect(screen, COLOR, (screen_x, screen_y, self.width, self.height))
```

### 新しいゲーム状態の追加
```python
from src.game_engine import GameState

class NewGameState(GameState):
    def __init__(self, game_engine):
        super().__init__(game_engine)
        # 状態固有の初期化
    
    def enter(self) -> None:
        """状態開始時の処理"""
        pass
    
    def exit(self) -> None:
        """状態終了時のクリーンアップ"""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """入力イベントの処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_engine.change_state(STATE_MENU)
    
    def update(self, dt: float) -> None:
        """状態の更新処理"""
        pass
    
    def render(self, screen: pygame.Surface) -> None:
        """状態の描画処理"""
        screen.fill(BACKGROUND_COLOR)
```

### コンポーネントシステムの活用
```python
# ヘルスコンポーネント
class HealthComponent:
    def __init__(self, max_health: int):
        self.max_health = max_health
        self.current_health = max_health
    
    def take_damage(self, amount: int) -> bool:
        self.current_health = max(0, self.current_health - amount)
        return self.current_health <= 0

# インベントリコンポーネント
class InventoryComponent:
    def __init__(self):
        self.items = {}
        self.coins = 0
    
    def add_item(self, item: str, count: int = 1):
        self.items[item] = self.items.get(item, 0) + count

# 使用例
entity.add_component("health", HealthComponent(100))
entity.add_component("inventory", InventoryComponent())

# アクセス
health = entity.get_component("health")
if health:
    is_dead = health.take_damage(25)
```

## デバッグパターン

### エンティティ状態の確認
```python
def debug_entity_info(entity: Entity) -> str:
    return f"{entity.entity_type}: pos=({entity.x:.1f}, {entity.y:.1f}), vel=({entity.velocity_x:.1f}, {entity.velocity_y:.1f}), active={entity.active}"

# ゲーム内デバッグ表示
def render_debug_info(screen: pygame.Surface, entities: List[Entity]):
    debug_font = pygame.font.Font(None, 24)
    y_offset = 10
    
    for entity in entities[:5]:  # 最初の5つのエンティティのみ表示
        debug_text = debug_entity_info(entity)
        text_surface = debug_font.render(debug_text, True, WHITE)
        screen.blit(text_surface, (10, y_offset))
        y_offset += 25
```

### パフォーマンス測定
```python
import time

class PerformanceTracker:
    def __init__(self):
        self.frame_times = []
        self.max_samples = 60
    
    def start_frame(self):
        self.frame_start = time.time()
    
    def end_frame(self):
        frame_time = time.time() - self.frame_start
        self.frame_times.append(frame_time)
        
        if len(self.frame_times) > self.max_samples:
            self.frame_times.pop(0)
    
    def get_average_fps(self) -> float:
        if not self.frame_times:
            return 0.0
        avg_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_time if avg_time > 0 else 0.0
```

## 設定管理パターン

### 設定ファイルの読み込み
```python
import json
from typing import Dict, Any

class GameSettings:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_settings()
    
    def get_default_settings(self) -> Dict[str, Any]:
        return {
            "volume": 0.7,
            "resolution": [1024, 768],
            "fullscreen": False,
            "controls": {
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
                "jump": pygame.K_SPACE
            }
        }
    
    def save_settings(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
```

## エラーハンドリングパターン

### 安全なリソース読み込み
```python
def safe_load_image(path: str, default_size: Tuple[int, int] = (32, 32)) -> pygame.Surface:
    try:
        return pygame.image.load(path)
    except pygame.error as e:
        print(f"画像の読み込みに失敗: {path} - {e}")
        # デフォルトの矩形を作成
        surface = pygame.Surface(default_size)
        surface.fill((255, 0, 255))  # マゼンタ色で欠落を示す
        return surface

def safe_load_sound(path: str) -> Optional[pygame.mixer.Sound]:
    try:
        return pygame.mixer.Sound(path)
    except pygame.error as e:
        print(f"音声の読み込みに失敗: {path} - {e}")
        return None
```