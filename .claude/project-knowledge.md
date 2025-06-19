# プロジェクト技術知識

## アーキテクチャの設計決定

### エンティティ・コンポーネント・システム (ECS)
- **決定理由**: ゲームオブジェクトの柔軟な拡張と管理を可能にするため
- **実装パターン**: 抽象基底クラス `Entity` を中心とした継承ベースのシステム
- **コンポーネント管理**: 動的コンポーネント追加による機能拡張

### ステートマシンベースのゲーム管理
- **ゲーム状態**: `STATE_MENU`, `STATE_PLAYING`, `STATE_PAUSED`, `STATE_GAME_OVER`
- **状態遷移**: `GameEngine.change_state()` による安全な状態切り替え
- **各状態の責任分離**: 個別の `GameState` サブクラスで管理

### カメラシステム
- **スムーズな追従**: プレイヤーを中心とした動的カメラ移動
- **境界制御**: レベル範囲内でのカメラ制限
- **補間アルゴリズム**: `smooth_factor` による自然な動き

## 物理演算の実装

### 基本物理定数
```python
GRAVITY = 1200          # 重力加速度 (pixels/s²)
TERMINAL_VELOCITY = 800 # 最大落下速度
JUMP_SPEED = -600       # ジャンプ初速度
```

### 衝突検出システム
- **矩形ベース**: `pygame.Rect` を使用した効率的な衝突判定
- **衝突面判定**: `get_collision_side()` による衝突方向の特定
- **重複計算**: 最小重複量による衝突面の決定

### 動き制御
- **加速度ベース**: 加速度→速度→位置の物理的な動きシミュレーション
- **摩擦システム**: 地面との接触時の速度減衰
- **地面判定**: `on_ground` フラグによる状態管理

## レンダリングシステム

### 層別描画 (Layered Rendering)
```python
LAYER_BACKGROUND = 0    # 背景
LAYER_PLATFORMS = 1     # プラットフォーム
LAYER_ENTITIES = 2      # エンティティ
LAYER_PLAYER = 3        # プレイヤー
LAYER_EFFECTS = 4       # 視覚効果
LAYER_UI = 5           # UI要素
```

### カメラオフセット
- **画面座標変換**: ワールド座標からスクリーン座標への変換
- **視界範囲外カリング**: 画面外オブジェクトの描画スキップ

## 使用ライブラリとツール

### Pygame 2.1.0+
- **選択理由**: Pythonでの2Dゲーム開発に最適化
- **主要機能**: 
  - イベント処理 (`pygame.event`)
  - 描画システム (`pygame.Surface`)
  - 衝突検出 (`pygame.Rect`)
  - フォント描画 (`pygame.font`)

### 標準ライブラリ活用
- **typing**: 型ヒントによるコード品質向上
- **abc**: 抽象基底クラスによる設計の強制
- **sys**: システム終了の安全な処理

## 実装パターンと慣例

### エンティティの作成パターン
```python
class CustomEntity(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, width, height, "custom")
        # 固有プロパティの初期化
    
    def update(self, dt, entities):
        # 物理演算とロジック更新
        
    def render(self, screen, camera_x, camera_y):
        # 描画処理
```

### コンポーネント追加パターン
```python
entity.add_component("health", HealthComponent(100))
entity.add_component("inventory", InventoryComponent())
```

### 状態管理パターン
- **enter()**: 状態開始時の初期化
- **exit()**: 状態終了時のクリーンアップ
- **update()**: フレーム毎の更新処理
- **render()**: 描画処理

## 避けるべきパターン

### パフォーマンス関連
- **毎フレームでのオブジェクト生成**: メモリ断片化の原因
- **不要な衝突検出**: 画面外や非アクティブエンティティとの判定
- **重複する描画命令**: 同一オブジェクトの複数回描画

### 設計関連
- **直接的な状態変更**: `GameEngine.change_state()` を経由しない状態変更
- **循環参照**: エンティティ間の相互参照による メモリリーク
- **ハードコーディング**: 定数ファイル以外での数値の直接記述