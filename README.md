# UTR-S201 シリーズ（LAN接続）Python サンプル

タカヤ製 UTR-S201 シリーズ（UHF帯）リーダライタを **LAN(TCP)** 経由で制御するためのサンプルです。  
USB版サンプル（`UTR_USB_sample_1.1.5.py`）の構造を踏襲し、**通信層のみ TCP に置き換え**ています。  
本サンプルは無保証です。検証・学習目的でご利用ください。

---

## 主な機能

- ROMバージョン確認（通信確認）
- コマンドモード切替
- **送信出力値**／**周波数チャンネル**の取得
- **インベントリ（タグ読み取り）**の実行（指定回数）
- **RSSI** と **PC+UII** の抽出・表示
- **ブザー制御**（タグ有り: ピー／タグ無し: ピッピッピ）
- 集計結果の表示／ログ保存（`Inventory_result_LAN.log`）
- 受信フレームの **STX / ETX / SUM / CR 検証**（USB版と同等）

---

## 動作確認環境

- Windows 10 / 11
- Python 3.10+
- ネットワーク到達可能な UTR-S201（LANモデル）  
  - 既定ポート例：**9004**（装置設定に依存します）

> 装置の通信設定（IP、ポート、ID など）は **UTR-RWManager** を用いて事前にご確認ください。

---

## フォルダ構成

```
UTR_LAN_PYTHON/
├─ src/
│  └─ UTR_LAN_sample_1.0.0.py   # 本サンプル（LAN版）
├─ .gitignore
└─ readme.md                     # このファイル
```

---

## 使い方（Quick Start）

1. Python を用意（3.10 以上）  
2. VS Code で本フォルダを開く（またはターミナルでフォルダに移動）  
3. 実行
   ```bash
   # リポジトリのルートで
   python src/UTR_LAN_sample_1.0.0.py
   ```
4. 実行時プロンプトに従い、**IP アドレス** と **TCP ポート** を入力  
   - ポート未入力時は **9004** を使用
5. 指定回数のインベントリを実行し、結果とログを出力

> **（任意）仮想環境**
> ```bash
> python -m venv .venv
> .venv\Scripts\activate
> python -m pip install --upgrade pip
> # 依存モジュールは標準ライブラリのみ（socket 等）
> ```

---

## 実行フロー

1. TCP 接続確立（クライアント）  
2. ROMバージョン確認（ACK/NACK判定）  
3. コマンドモード切替  
4. 送信出力値・周波数チャンネルの取得  
5. インベントリ（指定回数）  
6. ブザー制御（応答あり）  
7. 集計表示／ログ保存 → 切断  

> 受信処理は **1バイトずつ読み取り**、ヘッダ/フッタおよび **SUM を検証**してフレーム確定します。  
> ACK/NACK を受信した時点で `communicate()` は戻ります。

---

## VS Code でワンクリック実行（推奨設定）

`.vscode/launch.json` に以下を保存してください（**debugpy**使用）。

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run: UTR LAN sample",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/src/UTR_LAN_sample_1.0.0.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "justMyCode": true,
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  ]
}
```

---

## 主な設定ポイント

- **装置 IP / ポート**：実機の設定に合わせて入力（デフォルト 9004）  
- **タイムアウト**：`TcpSession(timeout=1.0)`、`communicate(..., timeout=...)` で変更可  
  - タグ枚数が多い環境では **インベントリのみ 3秒** など長めを推奨  
- **繰り返し回数**：1〜100 の範囲で指定

---

## トラブルシューティング

- **接続できない**：  
  - IP/ポート/配線/スイッチ設定を再確認  
  - 装置が TCP サーバーモードになっているか  
  - セキュリティソフト／FW でブロックされていないか
- **タイムアウトが多い**：  
  - `communicate()` の `timeout` を長めに（例: インベントリ 3.0）  
  - ネットワーク混雑時は HUB/ルータ経路も確認
- **タグが読めない**：  
  - 出力/周波数/アンテナ設定、タグ位置/向き/距離を確認  
  - 近傍の金属・干渉源の影響を確認

---

## .gitignore（例：Python）

```gitignore
__pycache__/
src/__pycache__/
*.pyc
.venv/
venv/
.env
*.log
.vscode/
```

`Inventory_result_LAN.log` はログのため、コミット不要であれば ignore 推奨です。

---

## 免責事項 / ライセンス

- 本サンプルは **無保証** です。ご利用は自己責任でお願いします。  
- ライセンスは任意です。MIT 等で公開する場合は `LICENSE` を追加してください（雛形の用意も可能です）。

---

## 参考情報

- タカヤ RFID 製品情報・ユーティリティ、各種「通信プロトコル説明書」  
  - UHF（UTR シリーズ）：https://www.takaya.co.jp/product/rfid/uhf/uhf_list/  
  - UTR ユーティリティ： https://www.takaya.co.jp/product/rfid/uhf/uhf_utility/  

> 実運用では **UTR-RWManager** の送受信ログと本サンプルの動作を突き合わせるとデバッグがスムーズです。
