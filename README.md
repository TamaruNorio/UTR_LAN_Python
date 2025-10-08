## TAKAYA RFID リーダライタ サンプルプログラム ドキュメント

> **ドキュメントの全体像や他のサンプルプログラムについては、[こちらのランディングページ](https://TamaruNorio.github.io/TAKAYA-RFID-Sample-Docs/python/index.md)をご覧ください。**

# UTR-S201 シリーズ（LAN接続）Python サンプル

タカヤ製 UTR-S201 シリーズ（UHF帯）リーダライタを **LAN(TCP)** 経由で制御するためのサンプルです。USB版サンプル（`UTR_USB_sample_1.1.5.py`）の構造を踏襲し、**通信層のみ TCP に置き換え**ています。本サンプルは無保証です。検証・学習目的でご利用ください。

## 概要

このサンプルプログラムは、ROMバージョン確認、コマンドモード切替、送信出力値／周波数チャンネルの取得、インベントリ（タグ読み取り）の実行、RSSIとPC+UIIの抽出・表示、ブザー制御、集計結果の表示／ログ保存、受信フレームのSTX / ETX / SUM / CR 検証といった主要な機能を提供します。

## 動作環境

-   OS: Windows 10 / 11
-   Python: 3.10+
-   ネットワーク到達可能な UTR-S201（LANモデル）
    -   既定ポート例：**9004**（装置設定に依存します）

> **注意**: 装置の通信設定（IP、ポートなど）は **UTR-RWManager** を用いて事前にご確認ください。

## セットアップと実行方法

1.  **Python を用意**: Python 3.10 以上がインストールされていることを確認してください。
2.  **リポジトリのクローン**:
    ```bash
    git clone https://github.com/TamaruNorio/UTR_LAN_Python.git
    cd UTR_LAN_Python
    ```
3.  **実行**:
    ```bash
    python src/UTR_LAN_sample_1.0.0.py
    ```
    実行時プロンプトに従い、**IP アドレス** と **TCP ポート** を入力します。ポート未入力時は **9004** を使用します。指定回数のインベントリを実行し、結果とログを出力します。

### VS Code でのワンクリック実行（推奨設定）

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

## プロジェクト構成

```
UTR_LAN_PYTHON/
├─ src/
│  └─ UTR_LAN_sample_1.0.0.py   # 本サンプル（LAN版）
├─ .gitignore
└─ README.md                     # このファイル
```

## 実装メモ

### 実行フロー

1.  TCP 接続確立（クライアント）
2.  ROMバージョン確認（ACK/NACK判定）
3.  コマンドモード切替
4.  送信出力値・周波数チャンネルの取得
5.  インベントリ（指定回数）
6.  ブザー制御（応答あり）
7.  集計表示／ログ保存 → 切断

> 受信処理は **1バイトずつ読み取り**、ヘッダ/フッタおよび **SUM を検証**してフレーム確定します。ACK/NACK を受信した時点で `communicate()` は戻ります。

### 主な設定ポイント

-   **装置 IP / ポート**：実機の設定に合わせて入力（デフォルト 9004）
-   **タイムアウト**：`TcpSession(timeout=1.0)`、`communicate(..., timeout=...)` で変更可。タグ枚数が多い環境では **インベントリのみ 3秒** など長めを推奨。
-   **繰り返し回数**：1〜100 の範囲で指定。

## ライセンス

本サンプルは **無保証** です。ご利用は自己責任でお願いします。ライセンスは任意です。MIT 等で公開する場合は `LICENSE` を追加してください。

## 変更履歴

-   0.1.0 (2024-06-06): 初版。LAN受信のフレーム復元とInventory2最小動作を実装。

