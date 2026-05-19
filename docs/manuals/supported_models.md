# 対象機種と対応インターフェース

## 目的

TAKAYA UTRシリーズ LAN接続 Pythonサンプルで対象とする機種と対応インターフェースを整理する。

## 参照元

- `docs/manuals/original/TDR-MNL-UTR-SUN02-4CH-102.pdf`
- `docs/manuals/original/TDR-MNL-UTR-SUN02-8CH-103.pdf`
- `docs/manuals/original/TDR-MNL-UTR-SUN02V-8CH-104.pdf`
- `docs/manuals/original/TDR-MNL-TR3IFBTOOLV201-100.pdf`

## 対象機種

| 製品種別 | 型式 | LAN対応 | 主なインターフェース | 本リポジトリでの扱い |
|---|---|---|---|---|
| UHFリーダライタ | UTR-SUN02-4CH | 対応 | USB、LAN(TCP/IP)、Bluetooth、Wi-Fi | LAN接続確認対象 |
| UHFリーダライタ | UTR-SUN02-8CH | 対応 | USB、有線LAN(Ethernet) | 取説上はLAN設定・動作確認の対象 |
| UHFリーダライタ | UTR-SUN02V-8CH | 対応 | USB、有線LAN(Ethernet) | LAN接続確認対象 |

> 根拠: UTR-SUN02-4CH取扱説明書 第2章 2.1「特徴」本文p.5
> 根拠: UTR-SUN02-8CH取扱説明書 第2章 2.1「特徴」本文p.5
> 根拠: UTR-SUN02V-8CH取扱説明書 第2章 2.1「特徴」本文p.5

## 各機種の対応インターフェース

### UTR-SUN02-4CH

- USB
- LAN(TCP/IP)
- Bluetooth
- Wi-Fi

> 根拠: UTR-SUN02-4CH取扱説明書 第2章 2.1「特徴」本文p.5

### UTR-SUN02-8CH

- USB
- 有線LAN(Ethernet)

> 根拠: UTR-SUN02-8CH取扱説明書 第2章 2.1「特徴」本文p.5

### UTR-SUN02V-8CH

- USB
- 有線LAN(Ethernet)

> 根拠: UTR-SUN02V-8CH取扱説明書 第2章 2.1「特徴」本文p.5

## LAN接続対象

- UTR-SUN02-4CH、UTR-SUN02-8CH、UTR-SUN02V-8CHはいずれもLAN接続確認の対象とする。
- 初期実機テストでは、LANサーバーモードを優先する。
- LANクライアントモードは、後続フェーズまたは別サンプル候補として扱う。

> 根拠: UTR-SUN02-4CH取扱説明書 第4章 4.2.2「LAN接続」本文p.13-p.14
> 根拠: UTR-SUN02-8CH取扱説明書 第4章 4.2.2「LAN接続」本文p.12-p.13
> 根拠: UTR-SUN02V-8CH取扱説明書 第4章 4.2.2「LAN接続」本文p.12-p.13

## UTR-SUN02-8CHとTR3IFBTool対象リストの扱い

- TR3IFBTool取扱説明書の動作対象機器リストでは、UTR-SUN02-8CHを明示確認できない。
- UTR-SUN02-8CH取扱説明書では、TR3IFBToolを参照ツールとして扱っている。
- UTR-SUN02-8CH取扱説明書には、LANクライアントモード、LANサーバーモードの動作確認手順が記載されている。
- 本リポジトリでは、UTR-SUN02-8CHを「取説上はLAN設定・動作確認の対象」として扱う。
- TR3IFBTool側の動作対象機器リストとの差分は、確認事項として残す。

> 根拠: TR3IFBTool取扱説明書 第1章 1.2「動作対象機器」本文p.3
> 根拠: UTR-SUN02-8CH取扱説明書「はじめに」本文pなし
> 根拠: UTR-SUN02-8CH取扱説明書 第5章 5.3.3「動作確認(LANクライアントモード)」本文p.26-p.34
> 根拠: UTR-SUN02-8CH取扱説明書 第5章 5.3.4「動作確認(LANサーバーモード)」本文p.35-p.42

## サンプルコードで優先する対象

- 優先する接続構成: PC側からリーダライタへ接続するLANサーバーモード。
- 優先理由: PythonサンプルがリーダライタのIPアドレス・ポートへTCP接続する構成に合うため。
- 後続候補: リーダライタ側からPCへ接続するLANクライアントモード。

> 根拠: TR3IFBTool取扱説明書 第3章 3.10「LANインターフェース設定（クライアントモード）」本文p.29-p.31
> 根拠: TR3IFBTool取扱説明書 第3章 3.11「LANインターフェース設定（サーバモード）」本文p.32-p.34

## 注意事項

- 通信コマンド仕様は `docs/protocol/` を正とする。
- 機器ごとの接続方法、電源、設置、安全注意は取扱説明書を確認する。
- LAN非対応機種をLANサンプルの対象として扱わない。
- ブザー制御は初期実機テストでは実行しない。
- ブザー制御は、ROMバージョン確認、RAM指定のコマンドモード設定、Inventory 1回の確認後、ユーザーが明示的に許可した場合のみ後続テストとして扱う。

## 確認事項

- TODO: TR3IFBTool取扱説明書の動作対象機器リストとUTR-SUN02-8CH取扱説明書の記載差分を確認する。
- TODO: 実機で使用する機種、ファームウェア、現在のLANモード、IPアドレス、ポートを確認する。
- TODO: LANクライアントモードをサンプル対象に含める場合は、Python側の待受サーバー実装方針を別途整理する。
