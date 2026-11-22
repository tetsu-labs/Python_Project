# Python実践開発マニュアル — ジュニアエンジニア到達版

**改訂第1版 / 2026年11月**  
対象：Pythonの文法を一度学んだ初学者。目標：小規模なPythonバックエンド／自動化案件を、仕様理解から実装・テスト・レビュー・障害調査まで自力で進める。  
前提：Windows 11 / VS Code / Python 3.12以上を例示。コマンドは主にPowerShellまたはbash。  
**重要：本書の「合格」は読了ではなく、独力で再現できること。** サンプルのコピペだけで合格にしない。

## 目次と学習設計

| 区分 | 章 | 主な成果物 |
|---|---|---|
| 必修 | 1 Python開発環境と実行 | venv、CLI |
| 必修 | 2 Python文法・データ構造 | 入出力を伴う集計器 |
| 必修 | 3 関数・OOP・型 | 責務分離した業務ロジック |
| 必修 | 4 ファイル・例外・ログ | CSV→JSON変換 |
| 必修 | 5 HTTP・外部API・セキュリティ基礎 | 再試行つきAPIクライアント |
| 必修 | 6 SQLとデータベース | テーブル・制約・トランザクション |
| 必修 | 7 FastAPIとWeb設計 | CRUD API |
| 必修 | 8 pytest・デバッグ・品質 | 自動テスト・再現手順 |
| 必修 | 9 Git・設計・レビュー | Pull RequestとREADME |
| 必修 | 10 Docker・CI/CD・運用 | コンテナ化・GitHub Actions |
| 応用 | 11 Web取得・ブラウザ自動化 | 規約配慮の取得処理 |
| 応用 | 12 pandas・可視化 | 集計レポート |
| 応用 | 13 非同期処理・ジョブ | 並列HTTP・失敗制御 |
| 応用 | 14 画像処理・OCR・ML | 再現可能な実験 |
| 実践 | 15 実務総合課題・評価 | 仕様→実装→保守→説明 |

**優先順位：** 第1〜10章を先に習得。第11〜14章は目的に応じて選択。第15章で横断的に能力を検証する。画像処理や機械学習は、Pythonジュニアバックエンド職の必須要件ではない。

### 学習の運用ルール

1. **読む（20%）**：何の問題を解決する技術かを説明する。
2. **動かす（30%）**：提示コードを実行し、入出力を観察する。
3. **変える（30%）**：要件を1つ変更し、テストを増やす。
4. **説明する（20%）**：選択理由、失敗例、改善余地をREADMEに記録する。

各章の課題は「成果物」「検証方法」「不合格の条件」をセットで評価する。学習時間は個人差が大きいため、時間よりテスト結果で進捗を管理する。

---

# 第1章 Python開発環境と実行

## 1.1 まず理解すること

Pythonプログラムの実行は `ソースコード → Pythonインタプリタ → OS`。`pip` はライブラリ導入、`venv` はプロジェクト単位の依存環境を分離する。IDEだけに依存せずターミナルから起動できることが必要。

Windows PowerShell：

```powershell
py --version
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -c "print('hello, junior')"
```

macOS/Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python --version
python -c "print('hello, junior')"
```

`python` と `pip` が別の環境を指す事故を防ぐため `python -m pip` を使う。`.venv/` はGitにコミットしない。配布に必要な依存は `requirements.txt` または `pyproject.toml` へ記載する。

## 1.2 コマンドライン引数

```python
# hello.py
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--name', required=True)
args = parser.parse_args()
print(f'こんにちは、{args.name}さん')
```

`python hello.py --name Taro` で実行。`--name` 未指定時に入力エラーを返す。`argparse` は`sys.argv`を手作業で分解するより安全で保守しやすい。

## 1.3 実務で起こる障害

- `ModuleNotFoundError`：仮想環境を有効化したか、実行中のPythonに導入したかを確認する。
- OS固有のパス：`pathlib.Path` を使い、文字列連結でパスを組み立てない。
- 「自分のPCだけ動く」：Pythonバージョンと依存をREADMEに明記し、別環境で再現する。

**演習1：** `python hello.py --name ...` に `--times` オプションを追加。1〜10以外はエラーにする。  
**合格条件：** 有効値・無効値の両方を確認し、別のターミナルから再実行できる。

---

# 第2章 Python文法・データ構造

## 2.1 変数・制御構文

```python
scores = [70, 95, 42, 88]
passed = [score for score in scores if score >= 60]
for i, score in enumerate(passed, start=1):
    print(i, score)
```

`if` は条件分岐、`for` は有限データ処理、`while` は終了条件つき反復に使う。`enumerate()` は番号、`zip()` は複数系列、`any()` と `all()` は条件判定に使う。

## 2.2 データ構造の選択

| 型 | 用途 | 重要な性質 |
|---|---|---|
| list | 順序つきの可変データ | インデックスで参照 |
| tuple | 変更しない組 | ハッシュ可能な要素だけなら辞書キー可 |
| dict | キーと値 | キー検索は平均的に高速 |
| set | 重複排除・所属判定 | 順序保証を期待しない |

```python
orders = [
    {'sku': 'A', 'amount': 1200},
    {'sku': 'B', 'amount': 900},
    {'sku': 'A', 'amount': 300},
]
summary = {}
for order in orders:
    sku = order['sku']
    summary[sku] = summary.get(sku, 0) + order['amount']
assert summary == {'A': 1500, 'B': 900}
```

**注意：** `float` は二進数の近似である。金額を正確に表すときは整数の円単位や `decimal.Decimal` を使用する。

```python
from decimal import Decimal
subtotal = Decimal('1299')
tax = Decimal('0.10')
print(subtotal * (1 + tax))  # 1428.90（端数処理は業務ルールで決める）
```

## 2.3 計算量の感覚

100万件から指定IDを探す場合、毎回リスト先頭から走査する処理はO(n)。IDをキーにした辞書なら平均的な検索はO(1)。ただしメモリ使用量や順序保持などの制約も考える。

**演習2：** 注文一覧からSKU別売上・件数を集計し、売上降順で表示。空配列でも例外にしない。  
**合格条件：** 重複、ゼロ件、負数（返品）をテストする。

---

# 第3章 関数・オブジェクト指向・型ヒント

## 3.1 関数の役割

関数は「同じ処理を繰り返す」ためだけでなく、入出力と責務を分離する単位。引数・返り値を明確にし、グローバル変数への暗黙依存を避ける。

```python
from decimal import Decimal

def gross_profit(revenue: Decimal, cost: Decimal, fee: Decimal) -> Decimal:
    """売上から原価と手数料を差し引く。"""
    return revenue - cost - fee

assert gross_profit(Decimal('2000'), Decimal('1300'), Decimal('180')) == Decimal('520')
```

## 3.2 クラスを使う基準

クラスは状態と振る舞いが一体の場合に有用。どの処理でもクラスを作る必要はない。単なる集計は関数で十分な場合が多い。

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Item:
    sku: str
    purchase_price: Decimal

    def expected_profit(self, sale_price: Decimal, fee: Decimal) -> Decimal:
        return sale_price - self.purchase_price - fee

item = Item('A', Decimal('1800'))
assert item.expected_profit(Decimal('2500'), Decimal('250')) == Decimal('450')
```

`frozen=True` は通常の代入による変更を防ぐが、内部に可変オブジェクトがあれば深い不変性を保証しない。

## 3.3 設計原則

- 高凝集：関数・クラスは明確な役割を持つ。
- 低結合：HTTP層がSQLやファイル操作の詳細を直接抱えない。
- 依存性注入：DBパス、外部APIクライアントを引数で渡し、テストで差し替えられるようにする。
- 過剰設計を避ける：使われない抽象化を先回りで追加しない。

**演習3：** `Item` に送料を加えた利益計算を追加し、Decimalで境界値をテスト。  
**合格条件：** 型ヒント、単体テスト、責務の説明がある。

---

# 第4章 ファイル・例外処理・ログ

## 4.1 pathlib・JSON・CSV

```pythonfrom pathlib import Path
import json

path = Path('data') / 'settings.json'
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps({'threshold': 500}, ensure_ascii=False), encoding='utf-8')
settings = json.loads(path.read_text(encoding='utf-8'))
assert settings['threshold'] == 500
```

CSVは `csv.DictReader` と `csv.DictWriter` を使う。日本語ファイルは一般に `encoding='utf-8-sig'` でExcelとの文字コード互換を確保できる場合がある。ただし取引先仕様に合わせる。

## 4.2 例外の扱い

```python
from pathlib import Path
import json

def load_config(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError as exc:
        raise RuntimeError(f'設定ファイルがありません: {path}') from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f'JSON形式が不正です: {path}') from exc
```

`except Exception: pass` は障害を隠すため原則避ける。例外は適切なレイヤーで処理し、ユーザーへのメッセージと開発者向けログを分ける。

## 4.3 logging と秘密情報

```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)
logger.info('job started: total=%d', 10)
```

アクセストークン、住所、個人情報、カード情報はログに出さない。ログにはリクエストIDや処理件数など調査に必要な最低限の情報を残す。

**演習4：** 不正な行を無視せずエラーログへ記録するCSV→JSON変換ツールを実装。  
**合格条件：** 正常CSV、不正CSV、空CSV、存在しないファイルの4ケースをテストする。

---

# 第5章 HTTP・外部API・セキュリティ基礎

## 5.1 HTTPで覚えること

GETは取得、POSTは新規処理、PUTは全体置換、PATCHは部分更新、DELETEは削除。HTTPステータス200、201、204、400、401、403、404、409、422、429、500、503を状況と結び付けて理解する。

認証（誰か）と認可（何を許されるか）は異なる。401は認証が必要／不正、403は権限不足などで使う。

## 5.2 requestsでAPI呼び出し

```python
import requests

with requests.Session() as session:
    try:
        response = session.get('https://httpbin.org/json', timeout=(3, 10))
        response.raise_for_status()
        payload = response.json()
        print(type(payload).__name__)
    except requests.Timeout:
        print('タイムアウト。後で再試行してください。')
    except requests.RequestException as exc:
        print(f'HTTP通信エラー: {exc}')
```

外部通信サンプルはネット接続を要する。現実の業務APIではレート制限、利用規約、個人情報の取り扱い、エンドポイントの制限を確認する。再試行は主に一時的障害に限り、重複作成につながるPOSTは冪等性キーなどの設計なしに機械的再試行しない。

## 5.3 セキュリティの最低限

- SQLは文字列連結せずプレースホルダを使う。
- 秘密情報はソースコードへハードコードしない。環境変数やシークレット管理を使う。
- 未検証のファイルパス、URL、ユーザー入力をそのまま処理しない。
- 外部から受け取ったJSONはスキーマ検証する。
- 依存パッケージを更新し、Gitに `.env` を含めない。

**演習5：** 公開APIのレスポンスを取得し、タイムアウト・429・500系に応じてログと終了コードを変える。  
**合格条件：** `unittest.mock` またはHTTPモックで通信失敗を再現できる。

---

# 第6章 SQL・データベース設計

## 6.1 DBの役割

ファイルは単純な保存に便利だが、条件検索、整合性、同時更新が必要になるとDBが有利。SQLiteは小規模なローカルアプリに便利。複数ワーカーや強い同時書き込み要件ではPostgreSQL等も検討する。

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    price_yen INTEGER NOT NULL CHECK(price_yen >= 0)
);
INSERT INTO products(sku,name,price_yen) VALUES('A01','Camera',12000);
SELECT sku, price_yen FROM products WHERE price_yen >= 10000;
```

## 6.2 JOIN・インデックス・トランザクション

```sql
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    qty INTEGER NOT NULL CHECK(qty > 0)
);
SELECT p.sku, SUM(s.qty) AS sold_qty
FROM sales AS s JOIN products AS p ON s.product_id = p.id
GROUP BY p.sku;
CREATE INDEX idx_sales_product_id ON sales(product_id);
```

JOINは関連データの統合。インデックスは検索を速くするが更新・容量のコストもある。トランザクションは一連の変更をまとめ、失敗時にROLLBACKできる単位。

```python
import sqlite3
with sqlite3.connect('shop.sqlite3') as conn:
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('UPDATE products SET price_yen=? WHERE sku=?', (10500, 'A01'))
```

上の例は事前のテーブル作成が必要。SQLiteでは外部キー制約が接続ごとに無効なことがあるため、必要なら接続時に有効化する。

## 6.3 進階で学ぶこと

正規化、N+1クエリ、EXPLAIN、楽観ロック、マイグレーション（Alembic）、バックアップと復旧。ORM（SQLAlchemy）を使う場合もSQL理解を省略しない。

**演習6：** 商品・売上の2表を設計しSKU別販売数量をJOINで集計。  
**合格条件：** UNIQUE、NOT NULL、CHECK、外部キー、インデックス、トランザクションを説明できる。

---

# 第7章 FastAPIとWeb API設計

## 7.1 層の分離

```text
HTTPリクエスト → FastAPIルーター → 入力検証 → リポジトリ → SQLite
HTTPレスポンス ← Pydantic応答モデル ←──────────────┘
```

同梱の `app/main.py` と `app/repository.py` を参照。HTTP層がDB操作の実装詳細を抱えない。`create_app(db_path)` で接続先を差し替え、テスト用DBを本番DBから分離する。

## 7.2 CRUD API

| エンドポイント | 処理 | 成功 |
|---|---|---|
| GET /health | ヘルスチェック | 200 |
| GET /tasks | 全件一覧 | 200 |
| POST /tasks | 新規作成 | 201 |
| GET /tasks/{id} | 個別取得 | 200 / 404 |
| PATCH /tasks/{id} | 完了フラグ更新 | 200 / 404 |
| DELETE /tasks/{id} | 削除 | 204 / 404 |

ローカル起動：

```bash
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

`http://127.0.0.1:8000/docs` でSwagger UIのAPI仕様と試行を確認する。入力はPydanticで制約を付ける。HTTP 422はスキーマ不適合を示す（FastAPIの標準挙動）。

## 7.3 APIを公開する前に

このサンプルは**認証・認可がない教材用アプリ**であり、外部公開は不可。実務ならログイン方式、リソース単位の認可、HTTPS、レート制限、CORSポリシー、監査ログ、データ保護、DBバックアップが必要。UIでボタンを隠すことは認可ではない。

**演習7：** `priority`（low/medium/high）を追加し、CRUD・DB制約・テストを一貫して改修。  
**合格条件：** 変更前のテストが維持され、新しい制約をテストしている。

---

# 第8章 pytest・デバッグ・品質

## 8.1 テストの3分類

- 単体テスト：関数、ルール、境界値を検証する。
- 結合テスト：APIとDBなど複数構成要素を合わせる。
- E2Eテスト：利用者の一連操作を通して確認する。

```python
# tests/test_profit.py（追加演習例）
from decimal import Decimal

def profit(revenue: Decimal, cost: Decimal) -> Decimal:
    return revenue - cost

def test_profit():
    assert profit(Decimal('1000'), Decimal('400')) == Decimal('600')
```

```bash
python -m pytest -q
```

本プロジェクトには入力検証、SQLインジェクションに見える文字列の保存、存在しないID、DB永続化などを確認するテストがある。**テスト件数より、故障モードを再現できるかが重要。**
## 8.2 デバッグの順序

1. 最小限の操作で不具合を再現する。
2. 期待結果／実結果を明文化する。
3. 入力、ログ、例外スタックトレース、DB状態を確認する。
4. 原因仮説を立て、1箇所ずつ変更する。
5. 再現テストを追加して修正する（回帰防止）。

調査では `print` に加え、VS Codeのブレークポイント、`pdb`、構造化ログも使う。

## 8.3 品質ゲート

```bash
python -m compileall -q app tests
python -m pytest -q
python -m ruff check app tests
```

**演習8：** 存在しないタスクの更新が404になるテストを先に書き、エラーを直す。  
**合格条件：** バグ再現テスト、修正、すべての回帰テスト通過をGitで示せる。

---

# 第9章 Git・設計・コードレビュー

## 9.1 一連の変更を管理する

```bash
git init
git switch -c feature/priority
git add app tests README.md
git commit -m "feat: add task priority"
```

リモート作成はGitHubの画面またはCLIで行う。リポジトリURLを設定して `git push -u origin feature/priority`。コミット前に `git diff --staged` で秘密情報や不要ファイルを確認する。

## 9.2 Pull Requestの記述

```text
目的: タスクを優先度別に管理する
変更: DB列、APIスキーマ、一覧ソート、テスト
確認: pytest、curl、手動操作
懸念: 既存DBのマイグレーションが必要
```

レビュー視点は「要件を満たすか」「変更を局所化できているか」「負のケースをテストしたか」「セキュリティと後方互換性に問題はないか」。

## 9.3 READMEと運用文書

READMEに概要、前提、セットアップ、起動、テスト、API利用例、既知の制約を書く。障害対応手順（Runbook）は「症状→確認→復旧→再発防止」を記述する。成果物の証拠はスクリーンショットより、再現可能なコマンドとテストログを優先する。

**演習9：** 要件変更→featureブランチ→コミット→PR説明文まで作成。  
**合格条件：** 第三者がREADMEだけで環境構築・テストを再現できる。

---

# 第10章 Docker・CI/CD・運用

## 10.1 Dockerの役割

Dockerイメージはアプリと依存環境をまとめた配布単位。コンテナはホストのカーネルを共有する分離実行環境であり、VMそのものではない。開発・テスト・本番の差を減らすが、DB永続化やセキュリティ設定は別に必要。

```bash
docker compose up --build
```

同梱 `Dockerfile` は非rootユーザー、`compose.yaml` は127.0.0.1バインド、名前付きボリュームを用いている。Dockerが利用できない環境では実行可否は未検証として扱う。

## 10.2 CIとCD

CI（継続的インテグレーション）はpush／PR時のビルド・静的解析・テストの自動化。CDは成果物を配布・デプロイする工程を自動化する考え方。本書の `.github/workflows/ci.yml` は**CIまで**で、公開デプロイはしない。

```yaml
name: Python CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python -m pip install -r requirements-dev.txt
      - run: python -m ruff check app tests
      - run: python -m pytest -q
```

GitHub Actionsのアクションは実務では安定版とSHA固定、最小権限設定などのサプライチェーン対策も検討する。

## 10.3 運用は何を測るか

- 可用性：ヘルスチェック、成功率、エラー率。
- 性能：レイテンシp50/p95、DB応答時間、スループット。
- 信頼性：バックアップ、復旧テスト、変更時の切り戻し。
- コスト：リソース使用量、不要な常駐処理、ログ保存期間。

**演習10：** Dockerで起動してAPIを確認し、GitHub ActionsがPR時にテストを実行する状態を作る。  
**合格条件：** CI実行の証拠、失敗テストを意図的に作った時の検出、ロールバック手順がある。

---

# 第11章 Web取得・ブラウザ自動化（選択）

## 11.1 requestsとBeautifulSoup

APIが提供される場合はAPIを優先する。HTML解析が許される場合は、HTTP取得・DOM解析・保存を別の関数に分割する。

```python
from bs4 import BeautifulSoup
html = '<ul><li class="item">A</li><li class="item">B</li></ul>'
soup = BeautifulSoup(html, 'html.parser')
items = [li.get_text(strip=True) for li in soup.select('li.item')]
assert items == ['A', 'B']
```

サイトの利用規約・robots.txt・アクセス頻度・著作権・個人情報・認証の扱いを確認する。403を回避するためのアクセス制御突破は行わず、公式APIや許可されたデータ取得方法へ切り替える。

## 11.2 Selenium/Playwright

JavaScriptによってDOMが更新される場合にブラウザ自動化を使う。固定sleepではなく「要素が見える／クリック可能になる」など状態を待つ。ヘッドレスでも動作、ダウンロード先、権限、ブラウザバージョンに注意する。

**演習11：** 自作の静的HTMLから名称・価格を取り出し、CSV保存する。ページ構造変更時には明示的なエラーにする。  
**合格条件：** 保存件数、欠損値、重複排除、取得頻度に対するテストがある。

---

# 第12章 pandas・集計・可視化（選択）

## 12.1 数値・日付・欠損値

```python
import pandas as pd

df = pd.DataFrame([
    {'day': '2026-10-01', 'sku': 'A', 'revenue': 2000, 'cost': 1400},
    {'day': '2026-10-02', 'sku': 'A', 'revenue': 2500, 'cost': 1500},
    {'day': '2026-10-03', 'sku': 'B', 'revenue': 1200, 'cost': 1000},
])
df['day'] = pd.to_datetime(df['day'], errors='raise')
df['profit'] = df['revenue'] - df['cost']
summary = df.groupby('sku', as_index=False)['profit'].sum()
print(summary)
```

CSVの金額列に文字列が混在すると集計に失敗する。`pd.to_numeric(..., errors='coerce')` を使った場合、変換失敗がNaNになるので勝手にゼロ補完せず件数を調査する。

## 12.2 可視化

```python
import matplotlib.pyplot as plt
summary.plot.bar(x='sku', y='profit', legend=False)
plt.ylabel('Profit (JPY)')
plt.tight_layout()
plt.savefig('profit_by_sku.png', dpi=160)
plt.close()
```

グラフは「何を判断するか」を先に決めて選ぶ。時間変化には折れ線、項目比較には棒、分布にはヒストグラム。母数や期間を隠した比較は誤解を招く。

**演習12：** 月次利益と粗利益率をCSVから算出し、欠損値レポートも出力。  
**合格条件：** 元CSV、変換コード、集計CSV、画像、欠損の扱いを記録。

---

# 第13章 asyncio・非同期ジョブ（選択）

## 13.1 非同期は万能ではない

`asyncio` は主にI/O待ちが多い処理に効果がある。CPU集約処理は通常マルチプロセス等を検討する。大量のHTTPを無制限に並列化すると相手サイトを圧迫し、レート制限を受ける。

```python
import asyncio

async def work(name: str) -> str:
    await asyncio.sleep(0.1)  # 待機を模擬
    return name

async def main() -> None:
    semaphore = asyncio.Semaphore(3)
    async def limited(name: str) -> str:
        async with semaphore:
            return await work(name)
    print(await asyncio.gather(*(limited(str(i)) for i in range(6))))

asyncio.run(main())
```

## 13.2 失敗設計

並列化する前に次を決める：同時実行上限、全体タイムアウト、個別の再試行間隔、キャンセル時の後処理、途中まで完了したデータの扱い、重複実行時の冪等性。`gather()` は1件失敗した際の振る舞いに注意する。

**演習13：** 10個の模擬ジョブを並列3件まで処理。1件だけ例外を出し、成功／失敗件数を最終表示。  
**合格条件：** 同時実行数が3を超えないことをテストで確認する。

---

# 第14章 画像処理・OCR・機械学習（選択）
## 14.1 Pillow/OpenCV/OCR

Pillowは画像の読込・回転・リサイズ・書出し、OpenCVは画像解析・幾何変換・テンプレート照合、OCRは画像の文字認識に使う。画像パス・形式の検証が必要で、OCRは画像品質や言語データにより精度が大きく変わる。

```python
from PIL import Image, ImageOps
with Image.open('input.jpg') as src:
    im = ImageOps.exif_transpose(src)
    im.thumbnail((1200, 1200))
    im.convert('RGB').save('output.jpg', quality=85)
```

Tesseract OCRを使う場合、`pip install pytesseract` に加えてOS側のTesseract本体が必要。日本語認識には `jpn.traineddata` が必要。二値化は常に精度を上げるわけではなく、画像ごとに評価する。

## 14.2 機械学習の基本設計

重要なのは複雑なモデルより、明確な目的変数、正しいデータ分割、リーク防止、ベースラインとの比較。

```python
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error

X, y = load_diabetes(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
for model in [DummyRegressor(strategy='mean'), Ridge(alpha=1.0)]:
    model.fit(X_train, y_train)
    print(type(model).__name__, mean_absolute_error(y_test, model.predict(X_test)))
```

時系列データ（中古商品の価格推移など）は原則として時間順に分割し、未来のデータを学習へ混入させない。実際の利益や顧客行動を予測するには、外れ値、欠損、手数料、サンプリングバイアス、情報の取得時点を精査する。

**演習14：** ベースラインと線形回帰を同条件で比較し、MAEを記録。  
**合格条件：** データの分割方法、リーク点検、評価結果、使えないケースを報告する。

---

# 第15章 総合開発課題：ジュニア到達判定

## 15.1 必修プロジェクトA：タスク管理API

同梱 `app/` は以下の最小要件を満たす教材用実装である。

- Pydanticによる入力検証
- SQLiteで永続化・SQLのプレースホルダ使用
- CRUD、404、201、204の区別
- DB処理とWeb層の分割
- `pytest` による自動テスト
- Dockerfile、compose.yaml、GitHub Actions

**未実装の実務拡張：** ログイン、ユーザーごとの認可、PostgreSQL、DBマイグレーション、監査ログ、バックアップ、監視。これらは「存在する」と誤認しないこと。

### ステップA1: 実行

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m uvicorn app.main:app --reload
```

### ステップA2: API検証

`/docs` でPOST `/tasks` に `{"title": "OSPF検証"}` を送信し201を得る。GETで保存確認、PATCHで完了、DELETE後にGETで404を確認。

### ステップA3: 仕様変更

優先度（low/medium/high）、締切、一覧フィルター（`?done=true`）のうち**2つ**を自力で実装し、正常・異常・境界値のテストを追加する。必ずDB変更時の既存データ対策を検討する。

### ステップA4: 品質

README、コード整形、lint、pytest、PR説明文、運用制約、障害再現手順を記録。

## 15.2 必修プロジェクトB：CSV売上集計CLI

**要件：** CSV（販売日時、SKU、売上円、仕入円、手数料円）を読み、SKU別件数・売上合計・利益合計をCSVへ書く。

**設計上の条件：**

- 正常時と異常時で終了コードを分ける。
- 不正な金額や欠損列を検知し、元行番号を示す。
- 原価と売上の合計は整数円で計算する。
- 入力ファイルを上書きしない。
- 同じ入力から同じ出力を再現できる。

**テスト：** 空CSV、列欠落、1件、複数件、返品（負数を許す仕様か明示）、文字コード、出力先の権限不足。

## 15.3 必修プロジェクトC：外部API連携・障害対応

**要件：** 許可された公開APIまたは自作のモックサーバーからデータを取得し、JSONで保存する。接続タイムアウト、HTTP 429、HTTP 500、壊れたJSONを区別する。

**設計上の条件：**

- タイムアウトを指定する。
- 一時的な失敗だけを上限回数つきで再試行する。
- トークンは環境変数で受け取る。
- ログにトークンを出さない。
- 実HTTPを発生させないテストを1件以上持つ。

## 15.4 障害対応演習（必修）

次の5件から**少なくとも4件を再現・修正・テスト化**する。

1. `POST /tasks` が空白タイトルを受け付けてしまう。
2. `PATCH /tasks/9999` が更新成功と誤報する。
3. DBのパスが異なり、テストデータと本番データを混ぜる。
4. ログにAPIキーが表示される。
5. CSVの数値列に文字列が混入して集計が壊れる。

それぞれ「症状・再現・原因・修正・確認・切り戻し」をチケット形式で残す。

## 15.5 到達判定（客観的なゲート）

| 能力 | 合格条件 | 重要度 |
|---|---|---|
| Python基礎 | 不明点を調べながら要件どおり実装 | 必須 |
| SQL | JOIN・制約・トランザクションを使える | 必須 |
| API | CRUD・入力検証・適切なステータス | 必須 |
| テスト | 新機能と故障モードの回帰テスト | 必須 |
| Git | featureブランチ、差分、PR説明 | 必須 |
| デバッグ | 再現→原因→修正を証拠付きで説明 | 必須 |
| Docker/CI | 自動テスト、開発環境再現 | 強く推奨 |
| セキュリティ | 認可と秘密情報の基本対策を説明 | 必須 |
| 説明能力 | READMEだけで他者が再現可能 | 必須 |

**重要：** この表は「学習用のジュニア到達基準」。採用や職務遂行を保証する資格ではない。既存コードの読解、他者レビュー、コミュニケーション、実際のチーム運用経験は別途必要。

## 15.6 合格後の成長経路

- **ジュニア初期：** 要件が明確な小規模実装とバグ修正をレビュー付きで遂行。
- **ジュニア上位：** 機能の分割・テスト戦略・ログ調査・DB変更を自律して実施。
- **ミドルへ：** 非機能要件、設計判断、障害対応、技術的負債、他者レビュー、運用品質に責任を持つ。

肩書きや習得期間ではなく、再現可能な成果物とレビュー品質で進捗を測る。

---

# 付録A：4週間の実装サイクル例

| 週 | 作業 | 残す証拠 |
|---|---|---|
| 1 | 1〜4章の基礎とCLI集計 | ソース、単体テスト |
| 2 | 5〜7章のHTTP、SQL、API | CRUD、リクエスト結果 |
| 3 | 8〜10章のテスト、Git、Docker | pytest結果、PR、CI |
| 4 | 第15章の機能拡張と障害演習 | 修正履歴、Runbook、README |

これはフルタイム学習の保証ではなく1回の短い学習サイクルの例。必要に応じて週を繰り返し、合格基準を満たすまで次へ進まない。

# 付録B：GitHubポートフォリオの最低構成

```text
python_junior_revised/
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── repository.py
│   └── main.py
├── tests/
│   ├── test_api.py
│   └── test_repository.py
├── .github/workflows/ci.yml
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── MANUAL.md
└── README.md
```

採用担当への説明は「何を作ったか」よりも「なぜその設計にしたか」「何をテストしたか」「どんな障害を想定したか」を中心にする。

# 付録C：学習進捗記録テンプレート

```text
日付:
章/課題:
仕様（完了条件）:
自力で実装した範囲:
参照した資料:
実行したコマンド:
テスト結果:
再現した失敗:
原因と修正:
次に改善する1点:
Gitコミット/PR URL:
```

# 付録D：改訂方針と制約

この改訂版は従来15章の話題を整理し、**必修10章＋選択4章＋総合実践1章**に再構成した。従来の説明だけの「完成プロジェクト」は完成実装として数えず、同梱のCRUD APIのみ検証対象とする。データ分析・OCR・機械学習のコードは各環境の依存導入後に実行する例で、同梱CIでは検証していない。GitHubへのアップロードやクラウドデプロイも行っていない。

本書は自己学習用の改訂初版であり、業務システムの本番投入には個別の設計・セキュリティレビュー・負荷テスト・運用手順が必要。