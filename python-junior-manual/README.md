# Pythonジュニア実務マニュアル（改訂版）

15章の教材 `MANUAL.md` と、独立した演習2本を収録しています。

## 目標

仕様を読み、Pythonで小規模な業務機能を実装し、テスト・デバッグ・GitHubレビューまで説明できるジュニアエンジニアを目指します。15章の読了だけでは合格としません。

## 実装状況

| 段階 | 成果物 | 状態 |
| --- | --- | --- |
| 1（第1〜4章） | CSV集計CLI（標準ライブラリ） | 実装・単体テスト済み |
| 2（第6〜8章） | FastAPI + SQLite CRUD API | 実装・単体テスト済み |
| 3（第5・9〜10章） | HTTPクライアント・品質・CI | CI設定追加、実行結果の確認待ち |
| 4（第11〜14章） | 収集・分析・非同期・OCR/ML | 未実装 |
| 5（第15章） | 総合プロジェクト | 未実装 |

ローカルの `python -m pytest -q` は **17 passed**（2026-11-23）。GitHub Actionsの実行結果は別途確認が必要です。

## セットアップ

```powershell
cd python-junior-manual
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

macOS/Linuxでは `python3 -m venv .venv && source .venv/bin/activate` を利用します。

## 演習1：CSV集計

列 `category,amount` を持つUTF-8 CSVを用意します。金額は円の整数値で、負の値は返金として扱います。

```csv
category,amount
書籍,1200
ゲーム,500
書籍,-200
```

```bash
python -m exercises.sales_summary sales.csv
```

期待出力：`{"ゲーム": 500, "書籍": 1000}`（JSON形式）。

## 演習2：FastAPI + SQLite

```bash
python -m uvicorn app.main:app --reload
```

`http://127.0.0.1:8000/docs` でPOST /tasks、GET /tasks、PATCH /tasks/{id}、DELETE /tasks/{id}を操作できます。

Docker環境を使う場合は、演習2のみ `docker compose up --build` で起動できます。Dockerの起動検証は未実施です。

## セキュリティ

このAPIには認証・認可・レート制限がありません。**インターネットへ直接公開しないでください。** SQLiteへのアクセスはパラメータ化クエリを利用しますが、本番利用には追加の設計が必要です。
