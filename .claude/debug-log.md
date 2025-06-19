# デバッグログ

## 重要なデバッグ記録

### 現在のプロジェクト状況
- **最終更新**: 2024年
- **プロジェクト段階**: 基本システム構築完了
- **動作状況**: 基本的なゲームプレイが動作中

### よくある問題と解決策

#### 問題: ゲームが起動しない
**症状**: `python main.py` 実行時にエラーが発生
**考えられる原因**:
- Pygameがインストールされていない
- Python版が古い (3.6未満)
- 依存関係の問題

**解決手順**:
1. Pygame のインストール確認: `pip show pygame`
2. 必要に応じて再インストール: `pip install pygame>=2.1.0`
3. Python版確認: `python --version`

#### 問題: フレームレートが低い
**症状**: ゲームの動きがカクカク、60FPS維持できない
**考えられる原因**:
- 衝突検出の処理が重い
- 不要な描画処理
- メモリリークによる性能低下

**デバッグ手順**:
1. パフォーマンストラッカーを有効化
2. エンティティ数の確認
3. 描画回数の最適化

#### 問題: プレイヤーが壁を通り抜ける
**症状**: 衝突検出が正常に動作しない
**考えられる原因**:
- 移動速度が大きすぎる
- 衝突検出のタイミング問題
- 物理演算の更新順序

**解決方法**:
- 連続衝突検出の実装
- 移動量の分割処理
- デルタタイムの調整

## デバッグ用コード例

### エンティティ状態の可視化
```python
def render_debug_overlay(screen, entities, camera_x, camera_y):
    """デバッグ情報をオーバーレイ表示"""
    debug_font = pygame.font.Font(None, 20)
    
    # エンティティの衝突ボックス表示
    for entity in entities:
        if entity.visible:
            screen_x = int(entity.x - camera_x)
            screen_y = int(entity.y - camera_y)
            pygame.draw.rect(screen, (255, 0, 0), 
                           (screen_x, screen_y, entity.width, entity.height), 1)
    
    # FPS表示
    fps_text = debug_font.render(f"FPS: {clock.get_fps():.1f}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))
```

### コンソール出力によるデバッグ
```python
def debug_collision_info(entity1, entity2):
    """衝突情報をコンソール出力"""
    side = entity1.get_collision_side(entity2)
    print(f"衝突検出: {entity1.entity_type} vs {entity2.entity_type}, 方向: {side}")
    print(f"位置1: ({entity1.x:.1f}, {entity1.y:.1f})")
    print(f"位置2: ({entity2.x:.1f}, {entity2.y:.1f})")
```

## トラブルシューティング履歴

### 解決済み問題

#### 2024年初期 - カメラの不安定な動き
**問題**: カメラがプレイヤーを追従する時に震える
**原因**: 整数変換のタイミング問題
**解決**: 浮動小数点で計算し、描画時のみ整数変換

#### 2024年中期 - メモリ使用量の増加
**問題**: 長時間プレイでメモリ使用量が増加
**原因**: エフェクトオブジェクトの削除不備
**解決**: `EffectsManager.clear()` の適切な実装

### 未解決・継続監視中の問題

#### パフォーマンスの最適化
**問題**: 多数のエンティティがある場合のフレームレート低下
**状況**: 調査中、オブジェクトプール実装を検討

#### 音声システム
**問題**: 音声ファイルの読み込みエラーハンドリング不足
**状況**: 将来の機能として実装予定

## デバッグ用設定

### 開発モードの切り替え
```python
# constants.py に追加
DEBUG_MODE = True
SHOW_COLLISION_BOXES = True
SHOW_FPS = True
ENABLE_DEBUG_KEYS = True
```

### デバッグキーの設定
- F1: 衝突ボックス表示切り替え
- F2: FPS表示切り替え
- F3: エンティティ情報表示
- F12: デバッグモード切り替え

## パフォーマンス測定結果

### 基準環境
- CPU: 一般的なデスクトップPC
- メモリ: 8GB以上
- 解像度: 1024x768

### 目標性能
- FPS: 60fps安定維持
- メモリ使用量: 100MB以下
- 起動時間: 3秒以内