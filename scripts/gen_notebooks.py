#!/usr/bin/env python3
"""
pytidb Colab チュートリアルの .ipynb を一括生成する。

使い方:
    python3 scripts/gen_notebooks.py

各トピックに対して tutorials/NN_*.ipynb を書き出す。
既存の 06_rag.ipynb はこの生成の対象外 (別途 git mv 済み)。
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

REPO = "tadapin/tidb-colab-tutorials"
OUT_DIR = Path(__file__).resolve().parent.parent / "tutorials"


# ----------------------------------------------------------------------------
# 共通ヘルパ
# ----------------------------------------------------------------------------

def _cell(kind: str, text: str, cell_id: str) -> dict:
    """ipynb の 1 セルを辞書として返す。kind は 'md' か 'code'。"""
    base = {
        "cell_type": "markdown" if kind == "md" else "code",
        "id": cell_id,
        "metadata": {},
        "source": text,
    }
    if kind == "code":
        base["execution_count"] = None
        base["outputs"] = []
    return base


def md(cell_id: str, text: str) -> dict:
    return _cell("md", textwrap.dedent(text).lstrip("\n").rstrip() + "\n", cell_id)


def code(cell_id: str, text: str) -> dict:
    return _cell("code", textwrap.dedent(text).lstrip("\n").rstrip() + "\n", cell_id)


def build_notebook(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "colab": {
                "provenance": [],
                "private_outputs": True,
                "include_colab_link": True,
            },
            "kernelspec": {"display_name": "Python 3", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def colab_badge(notebook_name: str) -> str:
    url = f"https://colab.research.google.com/github/{REPO}/blob/main/tutorials/{notebook_name}"
    return (
        f'<a href="{url}" target="_parent">'
        '<img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>'
        "</a>"
    )


# ----------------------------------------------------------------------------
# 共通コードブロック (各ノートブックに埋め込む)
# ----------------------------------------------------------------------------

INSTALL_BASIC = "!pip install -q pytidb"

PROVISION_CODE = '''\
from pathlib import Path
import requests

# TiDB Cloud Zero のAPIエンドポイント (サインアップ不要、30日有効)
ZERO_API = "https://zero.tidbapi.com/v1beta1/instances"


def request_zero_instance(tag: str = "pytidb-tutorial") -> dict:
    """TiDB Cloud Zero のインスタンスを作成して接続情報を返す"""
    resp = requests.post(ZERO_API, json={"tag": tag}, timeout=30)
    resp.raise_for_status()
    return resp.json()["instance"]


instance = request_zero_instance(tag="__TAG__")
conn = instance["connection"]
claim_url = instance.get("claimInfo", {}).get("claimUrl", "(取得失敗)")
expires_at = instance.get("expiresAt", "(取得失敗)")

print("=== プロビジョニング完了 ===")
print(f"Host     : {conn['host']}")
print(f"User     : {conn['username']}")
print(f"Expires  : {expires_at}")
print()
print("インスタンスは 30 日後に自動削除されます。")
print("保持したい場合は claim URL を開いてください:")
print(claim_url)
'''


def provision_code(tag: str) -> str:
    return PROVISION_CODE.replace("__TAG__", tag)


# ----------------------------------------------------------------------------
# 00_quickstart.ipynb
# ----------------------------------------------------------------------------

def build_00_quickstart() -> dict:
    name = "00_quickstart.ipynb"
    cells = [
        md("badge", f"{colab_badge(name)}"),
        md("title", """
            # pytidb クイックスタート (TODO タスク管理)

            このノートブックは **pytidb シリーズの第 0 回** です。pytidb で TiDB に接続し、テーブル作成から CRUD までの一連を 15 分で体験します。

            ## 学習目標
            - `TiDBClient.connect()` で TiDB Cloud Zero に接続する
            - `TableModel` でテーブルを Python のクラスとして定義する
            - `insert` / `query` / `update` / `delete` で基本操作を行う
        """),
        md("step1", "## 1. 依存パッケージのインストール"),
        code("install", INSTALL_BASIC),
        md("step2", """
            ## 2. TiDB Cloud Zero でクラスタを作成する

            [TiDB Cloud Zero](https://zero.tidbapi.com/) は、サインアップ不要で使い捨てクラスタを作れるサービスです。
            作成後 30 日間有効で、必要なら claim URL から TiDB Cloud Starter に移行できます。
        """),
        code("provision", provision_code(tag="pytidb-quickstart")),
        md("step3", """
            ## 3. TiDB に接続してテーブルを作成する

            `TableModel` を継承すると Python のクラスがそのまま TiDB のテーブル定義になります。
            今回は 3 列だけのシンプルな `tasks` テーブルを作ります。
        """),
        code("connect", """
            from pytidb import TiDBClient
            from pytidb.schema import Field, TableModel

            DATABASE = "quickstart_demo"

            db = TiDBClient.connect(
                host=conn["host"],
                port=4000,
                username=conn["username"],
                password=conn["password"],
                database=DATABASE,
                ensure_db=True,  # DB が無ければ作る
            )
            print("接続OK:", DATABASE)


            class Task(TableModel):
                __tablename__ = "tasks"
                __table_args__ = {"extend_existing": True}

                id: int = Field(primary_key=True)
                title: str = Field()
                done: bool = Field(default=False)


            table = db.create_table(schema=Task, if_exists="overwrite")
            print("テーブル準備OK:", table.table_name)
        """),
        md("step4", """
            ## 4. データを投入する (Create)

            単発の `insert` と、一括の `bulk_insert` の両方を試します。
            テーブルは `if_exists="overwrite"` で毎回作り直しているので、常にまっさらな状態から入ります。
        """),
        code("insert", """
            table.insert(Task(id=1, title="pytidb の README を読む"))
            table.bulk_insert([
                Task(id=2, title="クイックスタートを試す"),
                Task(id=3, title="ベクトル検索を動かす"),
                Task(id=4, title="ハイブリッド検索を動かす"),
            ])
            print(f"投入完了。現在の件数: {table.rows()}")
        """),
        md("step5", """
            ## 5. 取得する (Read)

            `table.query()` は条件指定・件数制限・並び替えに対応します。
            `.to_pydantic()` で `Task` クラスのインスタンスのリストが返ります。
        """),
        code("query", """
            tasks = table.query(limit=10).to_pydantic()
            for t in tasks:
                mark = "[x]" if t.done else "[ ]"
                print(f"{mark} #{t.id} {t.title}")
        """),
        md("step6", """
            ## 6. 更新と削除 (Update / Delete)

            `update` は条件に一致する行を書き換え、`delete` は行を消します。
        """),
        code("update_delete", """
            # id=1 を完了扱いにする
            table.update(values={"done": True}, filters={"id": 1})
            # id=4 は削除する
            table.delete(filters={"id": 4})

            # 確認
            for t in table.query(limit=10).to_pydantic():
                mark = "[x]" if t.done else "[ ]"
                print(f"{mark} #{t.id} {t.title}")
            print(f"合計: {table.rows()} 件")
        """),
        md("next", """
            ## 次のステップ

            - `01_schema_and_types.ipynb` : TEXT / JSON / VECTOR などのデータ型の使い分け
            - `02_query_and_filter.ipynb` : 複雑なフィルタ・並び替え・トランザクション
            - `03_vector_search.ipynb` : 意味類似検索 (セマンティック検索)

            ## 追加実験

            - `Task` に `due_date`(日付)列を追加してみる (`datetime.date` 型)
            - `table.query(filters={"done": False})` で未完了だけ取り出す
            - `db.drop_table("tasks")` でテーブルを削除し、再実行する
        """),
    ]
    return build_notebook(cells)


# ----------------------------------------------------------------------------
# 01_schema_and_types.ipynb
# ----------------------------------------------------------------------------

def build_01_schema() -> dict:
    name = "01_schema_and_types.ipynb"
    cells = [
        md("badge", f"{colab_badge(name)}"),
        md("title", """
            # pytidb のスキーマとデータ型 (書籍ライブラリ)

            このノートブックは **pytidb シリーズの第 1 回** です。 `TableModel` に TiDB 固有の型をどう表現するかを学びます。

            ## 学習目標
            - `str` / `int` / `bool` / `datetime` などの基本型をマップする
            - `TEXT`・`JSON`・`VECTOR` を明示的に指定する書き方を知る
            - JSON 列にリストやネスト構造を入れて読み書きする

            前提: `00_quickstart.ipynb` を実行済み。
        """),
        md("step1", "## 1. 依存パッケージのインストール"),
        code("install", INSTALL_BASIC),
        md("step2", "## 2. TiDB Cloud Zero でクラスタを作成する"),
        code("provision", provision_code(tag="pytidb-schema")),
        md("step3", """
            ## 3. 書籍テーブルを定義する

            TiDB のデータ型は pytidb の `datatype` モジュールから `TEXT` / `JSON` / `VECTOR` が取れます。
            Python の型ヒントと一緒に `Field(sa_type=...)` または `Field(sa_column=Column(...))` で指定します。
        """),
        code("schema", """
            from datetime import date
            from pytidb import TiDBClient
            from pytidb.schema import Field, TableModel, VectorField
            from pytidb.datatype import JSON, TEXT

            DATABASE = "books_demo"

            db = TiDBClient.connect(
                host=conn["host"],
                port=4000,
                username=conn["username"],
                password=conn["password"],
                database=DATABASE,
                ensure_db=True,
            )


            class Book(TableModel):
                __tablename__ = "books"
                __table_args__ = {"extend_existing": True}

                id: int = Field(primary_key=True)
                title: str = Field()                             # VARCHAR (<=255)
                summary: str = Field(sa_type=TEXT)               # 長文 → TEXT
                authors: list = Field(sa_type=JSON, default_factory=list)   # JSON 配列
                tags: dict = Field(sa_type=JSON, default_factory=dict)      # JSON オブジェクト
                published_on: date = Field()                     # DATE
                rating: float = Field(default=0.0)               # DOUBLE
                embedding: list[float] = VectorField(dimensions=8)   # VECTOR(8) (デモ用に 8 次元のダミー)


            table = db.create_table(schema=Book, if_exists="overwrite")
            print("テーブル準備OK:", table.table_name)
        """),
        md("step4", """
            ## 4. データを投入する

            JSON 列には Python の `list` や `dict` をそのまま渡せます。
            `VECTOR(8)` のダミーには手書きの 8 次元リストを入れます (本物の embedding は `03_vector_search.ipynb` で扱います)。
        """),
        code("insert", """
            samples = [
                Book(
                    id=1,
                    title="幻想機械の設計図",
                    summary="19 世紀末のヨーロッパを舞台に、発明家と彼の幻想機械をめぐる冒険を描く長編小説。",
                    authors=["白井 翔", "Mia Hoffmann"],
                    tags={"genre": "fantasy", "language": "ja", "pages": 412},
                    published_on=date(2021, 6, 15),
                    rating=4.2,
                    embedding=[0.1] * 8,
                ),
                Book(
                    id=2,
                    title="分散システム入門",
                    summary="コンセンサスアルゴリズムとレプリケーションをゼロから解説する技術書。",
                    authors=["中村 健二"],
                    tags={"genre": "tech", "language": "ja", "pages": 268, "topics": ["raft", "paxos"]},
                    published_on=date(2019, 11, 1),
                    rating=4.6,
                    embedding=[0.2] * 8,
                ),
                Book(
                    id=3,
                    title="Tea and Tectonics",
                    summary="A memoir that weaves the history of Darjeeling tea with personal reflections on travel.",
                    authors=["Priya Venkatesh"],
                    tags={"genre": "memoir", "language": "en", "pages": 320},
                    published_on=date(2023, 3, 28),
                    rating=4.0,
                    embedding=[0.3] * 8,
                ),
            ]
            table.bulk_insert(samples)
            print(f"投入完了。件数: {table.rows()}")
        """),
        md("step5", """
            ## 5. JSON 列を読み書きする

            取得時は Python のオブジェクトとして戻ります。条件指定にはフィルタ辞書または SQL 的な式を使えます。
        """),
        code("json_read", """
            books = table.query().to_pydantic()
            for b in books:
                topics = b.tags.get("topics", [])
                print(f"#{b.id} {b.title}  著者={b.authors}  pages={b.tags.get('pages')}  topics={topics}")
        """),
        md("step6", """
            ## 6. JSON 列に対して条件を指定する

            pytidb の `filter` は MongoDB 風の演算子 (`$eq`, `$gt`, `$lt`, `$in` など) を使えます。
            JSON 列のキーへ降りるときは生 SQL を使うと分かりやすいです。
        """),
        code("json_filter", """
            # 単純なフィルタ: rating が 4.3 以上の本を取得
            high_rated = table.query(filters={"rating": {"$gte": 4.3}}).to_pydantic()
            print("評価 4.3 以上:")
            for b in high_rated:
                print(f"  #{b.id} {b.title} ({b.rating})")

            # JSON のネストキーで絞る場合は client.query (生 SQL) を使う
            rows = db.query(\"\"\"
                SELECT id, title, tags
                FROM books
                WHERE JSON_EXTRACT(tags, '$.genre') = 'tech'
            \"\"\").to_rows()
            print("\\ngenre=tech の本:")
            for r in rows:
                print(f"  {r}")
        """),
        md("next", """
            ## 次のステップ

            - `02_query_and_filter.ipynb` : クエリ・フィルタ・トランザクション
            - `03_vector_search.ipynb` : VECTOR を実際の埋め込みで使う

            ## 追加実験

            - `tags` に `"price": 1980` を加えて、価格帯で絞ってみる
            - `published_on` で年ごとに絞り込み (`$gte` / `$lte`)
            - `table.update(values={"rating": 4.8}, filters={"id": 2})` で更新
        """),
    ]
    return build_notebook(cells)


# ----------------------------------------------------------------------------
# 02_query_and_filter.ipynb
# ----------------------------------------------------------------------------

def build_02_query() -> dict:
    name = "02_query_and_filter.ipynb"
    cells = [
        md("badge", f"{colab_badge(name)}"),
        md("title", """
            # クエリ・フィルタ・トランザクション (在庫管理)

            このノートブックは **pytidb シリーズの第 2 回** です。在庫管理を題材に、条件付き検索・並び替え・ページング・更新・トランザクションを扱います。

            ## 学習目標
            - `filter` に MongoDB 風の演算子 (`$gt`, `$lt`, `$in` …) を渡す
            - `order_by` / `limit` / `offset` でページングする
            - `table.update` / `table.delete` で一括更新
            - `client.session()` でトランザクション (全件コミット or ロールバック)

            前提: `00_quickstart.ipynb` を実行済み。
        """),
        md("step1", "## 1. 依存と接続"),
        code("install", INSTALL_BASIC),
        code("provision", provision_code(tag="pytidb-query")),
        md("step2", """
            ## 2. 在庫テーブルを作成

            `sku`(SKU), `name`(商品名), `category`(カテゴリ), `stock`(在庫数), `price`(価格) の 5 列。
        """),
        code("schema", """
            from pytidb import TiDBClient
            from pytidb.schema import Field, TableModel

            db = TiDBClient.connect(
                host=conn["host"],
                port=4000,
                username=conn["username"],
                password=conn["password"],
                database="inventory_demo",
                ensure_db=True,
            )


            class Item(TableModel):
                __tablename__ = "inventory"
                __table_args__ = {"extend_existing": True}

                sku: str = Field(primary_key=True)
                name: str = Field()
                category: str = Field()
                stock: int = Field(default=0)
                price: float = Field(default=0.0)


            table = db.create_table(schema=Item, if_exists="overwrite")
            print("テーブル準備OK:", table.table_name)
        """),
        md("step3", "## 3. データ投入"),
        code("insert", """
            SAMPLES = [
                Item(sku="A-001", name="ワイヤレスイヤホン",  category="electronics", stock=42, price=8980),
                Item(sku="A-002", name="スマートウォッチ",    category="electronics", stock=15, price=18900),
                Item(sku="A-003", name="USB-C ケーブル 1m",   category="electronics", stock=0,  price=890),
                Item(sku="B-001", name="エスプレッソ粉 200g", category="grocery",     stock=30, price=1280),
                Item(sku="B-002", name="抹茶パウダー 100g",   category="grocery",     stock=8,  price=2480),
                Item(sku="B-003", name="ダークチョコ 70%",    category="grocery",     stock=120, price=580),
                Item(sku="C-001", name="帆布トートバッグ",    category="fashion",     stock=22, price=3980),
                Item(sku="C-002", name="リネンシャツ",        category="fashion",     stock=0,  price=6900),
                Item(sku="C-003", name="ウールソックス",      category="fashion",     stock=65, price=1280),
            ]

            table.bulk_insert(SAMPLES)
            print(f"投入完了。{table.rows()} 件")
        """),
        md("step4", """
            ## 4. フィルタ式のバリエーション

            `filters` は dict で、値に `{"$gt": X}` のような演算子を書けます。
            利用できる演算子: `$eq`, `$ne`, `$lt`, `$lte`, `$gt`, `$gte`, `$in`, `$nin`。
        """),
        code("filters", """
            # 価格 5000 円以下のもの
            cheap = table.query(filters={"price": {"$lte": 5000}}).to_pydantic()
            print(f"[価格 5000 円以下] {len(cheap)} 件")

            # electronics または fashion のどちらか
            mixed = table.query(filters={"category": {"$in": ["electronics", "fashion"]}}).to_pydantic()
            print(f"[electronics or fashion] {len(mixed)} 件")

            # 在庫切れ
            oos = table.query(filters={"stock": 0}).to_pydantic()
            print(f"[在庫切れ] {[i.sku for i in oos]}")
        """),
        md("step5", """
            ## 5. 並び替えとページング

            `order_by` に `{"カラム": "asc" | "desc"}` を渡します。`limit` / `offset` でページング。
        """),
        code("order_page", """
            # 在庫が少ない順に 3 件
            tight = table.query(order_by={"stock": "asc"}, limit=3).to_pydantic()
            print("[在庫少ない順 TOP3]")
            for i in tight:
                print(f"  {i.sku} stock={i.stock} name={i.name}")

            # 価格が高い順に 2 件ずつページング
            print("\\n[価格降順・2 件ずつ]")
            for page in range(3):
                items = table.query(order_by={"price": "desc"}, limit=2, offset=page * 2).to_pydantic()
                print(f"  page {page}: {[i.name for i in items]}")
        """),
        md("step6", """
            ## 6. 一括更新と削除

            条件付きで `update` / `delete` を行います。
        """),
        code("update_delete", """
            # grocery カテゴリだけ 10% 値上げ (生 SQL を使うと一括計算しやすい)
            db.execute("UPDATE inventory SET price = price * 1.10 WHERE category = 'grocery'")

            # 在庫ゼロの商品を削除
            before = table.rows()
            table.delete(filters={"stock": 0})
            after = table.rows()
            print(f"削除件数: {before - after}  (残り {after} 件)")
        """),
        md("step7", """
            ## 7. トランザクション (`client.session()`)

            `with db.session()` のブロック内で例外が出れば自動ロールバック、無事抜ければコミットします。
            次の例では、在庫の移動 (倉庫 A → 倉庫 B) を 2 つの UPDATE でアトミックに行います。
        """),
        code("transaction", """
            # 例のため、カテゴリごとに在庫合計を出す関数を用意
            def category_stock(cat):
                rows = db.query(
                    "SELECT COALESCE(SUM(stock), 0) FROM inventory WHERE category = :cat",
                    {"cat": cat},
                ).to_rows()
                return rows[0][0]

            before_e = category_stock("electronics")
            before_f = category_stock("fashion")
            print(f"before: electronics={before_e}, fashion={before_f}")

            MOVE_QTY = 5
            with db.session():
                db.execute(
                    "UPDATE inventory SET stock = stock - :q WHERE sku = 'A-002'",
                    {"q": MOVE_QTY},
                )
                db.execute(
                    "UPDATE inventory SET stock = stock + :q WHERE sku = 'C-003'",
                    {"q": MOVE_QTY},
                )

            after_e = category_stock("electronics")
            after_f = category_stock("fashion")
            print(f"after : electronics={after_e}, fashion={after_f}")
            print("(electronics から fashion へ 5 個ぶん移動、合計は保存される)")
        """),
        md("next", """
            ## 次のステップ

            - `03_vector_search.ipynb` : 自然言語での意味類似検索
            - `05_hybrid_search.ipynb` : ベクトル + 全文のハイブリッド

            ## 追加実験

            - `{"$and": [...], "$or": [...]}` の組み合わせを試す
            - `db.query(sql, params)` で group by / having を書いてみる
            - session 内で `raise Exception("abort")` したらロールバックされることを確認
        """),
    ]
    return build_notebook(cells)


# ----------------------------------------------------------------------------
# 03_vector_search.ipynb
# ----------------------------------------------------------------------------

def build_03_vector() -> dict:
    name = "03_vector_search.ipynb"
    cells = [
        md("badge", f"{colab_badge(name)}"),
        md("title", """
            # ベクトル検索 / セマンティック検索 (ニュース見出し)

            このノートブックは **pytidb シリーズの第 3 回** です。ニュース記事の見出しを題材に、自然言語で意味的に近い記事を引き出す手順を学びます。

            ## 学習目標
            - `EmbeddingFunction(model_name="tidbcloud_free/...")` で TiDB 組み込みの埋め込みを使う
            - `VectorField(source_field="...")` で自動埋め込み (auto-embedding) 列を作る
            - `table.search(QUERY)` で類似検索、`distance` / `similarity_score` を読み取る
            - `distance_threshold` / `filter` と併用して絞り込みを行う

            前提: `00_quickstart.ipynb` / `01_schema_and_types.ipynb` を実行済み。
            API キーは不要 (TiDB Cloud Zero + Titan 組み込み埋め込みで完結)。
        """),
        md("step1", "## 1. 依存と接続"),
        code("install", INSTALL_BASIC),
        code("provision", provision_code(tag="pytidb-vector")),
        md("step2", """
            ## 2. 見出しテーブルを作成

            `headline` 列に対して自動で埋め込み (`headline_vec`) を生成する構成にします。
            `EmbeddingFunction("tidbcloud_free/amazon/titan-embed-text-v2")` はサーバサイド実行なので、pytidb の追加依存 (litellm 等) は不要です。
        """),
        code("schema", """
            from pytidb import TiDBClient
            from pytidb.datatype import TEXT
            from pytidb.embeddings import EmbeddingFunction
            from pytidb.schema import Field, TableModel

            db = TiDBClient.connect(
                host=conn["host"],
                port=4000,
                username=conn["username"],
                password=conn["password"],
                database="news_demo",
                ensure_db=True,
            )

            _embed = EmbeddingFunction(
                model_name="tidbcloud_free/amazon/titan-embed-text-v2",
            )


            class Headline(TableModel):
                __tablename__ = "headlines"
                __table_args__ = {"extend_existing": True}

                id: int = Field(primary_key=True)
                category: str = Field()
                headline: str = Field(sa_type=TEXT)
                headline_vec: list[float] = _embed.VectorField(source_field="headline")


            table = db.create_table(schema=Headline, if_exists="overwrite")
            print("テーブル準備OK:", table.table_name)
        """),
        md("step3", """
            ## 3. サンプル見出しを投入

            20 件のフィクションの見出し。カテゴリは `tech` / `sports` / `food` / `science` の 4 つ。
        """),
        code("insert", """
            HEADLINES = [
                ("tech",    "スタートアップが量子暗号を使った新メッセンジャーを発表"),
                ("tech",    "大手クラウドが東京にAI専用データセンターを新設"),
                ("tech",    "オープンソースの日本語LLMがGitHubで急上昇"),
                ("tech",    "自動運転トラックが都市間配送で商用試験を開始"),
                ("tech",    "スマホ向けARアプリが教育市場で利用を拡大"),
                ("sports",  "マラソン大会で国内新記録が誕生"),
                ("sports",  "プロ野球セ・リーグ、延長12回の末にサヨナラ勝ち"),
                ("sports",  "ワールドカップ予選、日本代表が欧州遠征で勝利"),
                ("sports",  "卓球の国際大会で高校生選手が初優勝"),
                ("sports",  "女子バスケットボール、東京チームが逆転で連勝"),
                ("food",    "地方発のクラフトビール醸造所が全国展開を開始"),
                ("food",    "新しい培養肉のバーガーが東京のレストランで試験提供"),
                ("food",    "家庭向けの自動調理家電、新モデルが30分で8品作る"),
                ("food",    "北海道のワイナリー、リースリングが国際コンクールで金賞"),
                ("food",    "冷凍技術が進化し、寿司ネタが自宅で解凍1分で食べ頃に"),
                ("science", "国内天文台が近傍銀河の暗黒物質分布を新たに解明"),
                ("science", "深海探査ロボットが新種の甲殻類を発見"),
                ("science", "mRNAを使った新しいワクチンの臨床試験が第3相に進む"),
                ("science", "ペロブスカイト太陽電池の屋外耐久性が大幅に向上"),
                ("science", "量子コンピュータで物質相転移のシミュレーションに成功"),
            ]

            table.bulk_insert([
                Headline(id=i + 1, category=c, headline=h)
                for i, (c, h) in enumerate(HEADLINES)
            ])
            print(f"投入完了: {table.rows()} 件")
        """),
        md("step4", """
            ## 4. ベクトル検索を実行

            `table.search(QUERY)` にテキストを渡すだけで、自動的に埋め込みへ変換されて類似検索が走ります。
            結果は `distance` (小さいほど近い) と `similarity_score = 1 - distance` を持ちます。
        """),
        code("search", """
            QUERY = "宇宙や物理学の新しい発見について知りたい"

            results = table.search(QUERY).limit(5).to_pydantic()

            print(f"Query: {QUERY}\\n")
            for i, r in enumerate(results, 1):
                print(f"{i}. [{r.hit.category}] {r.hit.headline}")
                print(f"    distance={r.distance:.4f}  similarity={r.similarity_score:.4f}")
        """),
        md("step5", """
            ## 5. フィルタと閾値を組み合わせる

            カテゴリの絞り込みや、ある程度似ているものだけに限定するときに便利です。
        """),
        code("filter", """
            # food カテゴリの中から意味的に近い上位 3 件
            results = (
                table.search("自宅で簡単に新しい食体験ができる話題")
                .filter({"category": "food"})
                .limit(3)
                .to_pydantic()
            )
            print("[food カテゴリ内で意味検索]")
            for r in results:
                print(f"  sim={r.similarity_score:.3f}  {r.hit.headline}")

            # 閾値以下 (= 十分近い) のものだけ
            print("\\n[distance <= 0.5 に限定]")
            results = (
                table.search("AIやデータセンターの動向")
                .distance_threshold(0.5)
                .limit(10)
                .to_pydantic()
            )
            for r in results:
                print(f"  d={r.distance:.3f}  [{r.hit.category}] {r.hit.headline}")
        """),
        md("step6", """
            ## 6. 裏で何が起きているか

            - サーバサイド埋め込み: `INSERT` 時に TiDB が `EMBED_TEXT()` 関数で `headline` を `headline_vec` に変換して保存
            - 検索時も同じモデルで質問文が埋め込まれ、`VEC_COSINE_DISTANCE` でスコアを計算
            - デフォルトの距離メトリクスは COSINE、HNSW インデックスが自動で貼られる

            API キーが要らないのは、TiDB Cloud の無料プロバイダ (Titan) を内部で呼び出しているためです。
        """),
        md("next", """
            ## 次のステップ

            - `04_fulltext_search.ipynb` : キーワード一致ベースの全文検索
            - `05_hybrid_search.ipynb` : ベクトル + 全文のハイブリッド

            ## 追加実験

            - クエリを `"おいしい料理の最新ニュース"` に変えて結果がどう変わるか
            - `distance_threshold(0.3)` にして、ヒットが 0 件になる境界を探す
            - 独自の見出しを追加 (`table.insert(...)`) し、再検索で上位に来るか確認
        """),
    ]
    return build_notebook(cells)


# ----------------------------------------------------------------------------
# 04_fulltext_search.ipynb
# ----------------------------------------------------------------------------

def build_04_fts() -> dict:
    name = "04_fulltext_search.ipynb"
    cells = [
        md("badge", f"{colab_badge(name)}"),
        md("title", """
            # 全文検索 / 日本語トークナイズ (ブログ記事)

            このノートブックは **pytidb シリーズの第 4 回** です。ブログ記事を題材に、キーワード一致ベースの全文検索 (FTS) を扱います。

            ## 学習目標
            - `FullTextField(fts_parser="MULTILINGUAL")` で FTS インデックス付き列を作る
            - `table.search(QUERY, search_type="fulltext")` で検索
            - `match_score` の見方、ベクトル検索との違い
            - 言語の異なる記事に対する `MULTILINGUAL` パーサの挙動

            前提: `00_quickstart.ipynb` を実行済み。
        """),
        md("step1", "## 1. 依存と接続"),
        code("install", INSTALL_BASIC),
        code("provision", provision_code(tag="pytidb-fts")),
        md("step2", """
            ## 2. ブログ記事テーブル

            `title` と `body` を全文検索可能にします。`FullTextField(fts_parser="MULTILINGUAL")` は
            日本語・中国語・英語などを自動的にトークナイズできるパーサです。
        """),
        code("schema", """
            from pytidb import TiDBClient
            from pytidb.schema import Field, FullTextField, TableModel

            db = TiDBClient.connect(
                host=conn["host"],
                port=4000,
                username=conn["username"],
                password=conn["password"],
                database="blog_demo",
                ensure_db=True,
            )


            class Post(TableModel):
                __tablename__ = "posts"
                __table_args__ = {"extend_existing": True}

                id: int = Field(primary_key=True)
                language: str = Field(max_length=8)
                title: str = FullTextField(fts_parser="MULTILINGUAL")
                body: str = FullTextField(fts_parser="MULTILINGUAL")


            table = db.create_table(schema=Post, if_exists="overwrite")
            print("テーブル準備OK:", table.table_name)
        """),
        md("step3", """
            ## 3. サンプル記事の投入

            日本語 6 本 + 英語 3 本の小さなデータセット。
        """),
        code("insert", """
            POSTS = [
                ("ja", "分散トランザクションの基礎",        "TiDB の分散トランザクションは ACID で動作します。コミット時に TSO から一意のタイムスタンプを取得し、Percolator を参考にした 2 フェーズコミットで複数ノードにまたがる整合性を実現します。"),
                ("ja", "ベクトル検索を始めよう",            "ベクトル検索は意味的な近さでドキュメントを取り出す技術です。TiDB は VECTOR 型と HNSW インデックスを提供します。"),
                ("ja", "全文検索の使いどころ",              "キーワードが一致する文書を素早く取り出したい時は全文検索が向きます。商品カタログや FAQ のような用途で特に有効です。"),
                ("ja", "PyTiDB でレシピ RAG を作る",        "レシピデータをベクトル化し、ユーザーの質問に近いレシピを引っ張り出して LLM に渡すと、簡単に RAG アプリが作れます。"),
                ("ja", "HTAP で分析と運用を同じデータで",   "TiDB は行指向の TiKV と列指向の TiFlash を併用し、トランザクションと分析クエリを同じクラスタで実行できます。"),
                ("ja", "日本語トークナイザの違いを比べる",  "MULTILINGUAL パーサは漢字・ひらがな・カタカナを自動で区切ってくれます。英数字混じりでも自然に働きます。"),
                ("en", "Hybrid search explained",          "Hybrid search combines keyword based full-text matching with vector similarity to capture both exact and semantic relevance."),
                ("en", "Why use HTAP databases",           "HTAP systems let you run transactional and analytical workloads on the same cluster without ETL, making real-time dashboards easier."),
                ("en", "Intro to RAG for developers",      "Retrieval Augmented Generation improves LLM answers by grounding them on retrieved context from a knowledge base."),
            ]

            table.bulk_insert([
                Post(id=i + 1, language=lang, title=t, body=b)
                for i, (lang, t, b) in enumerate(POSTS)
            ])
            print(f"投入完了: {table.rows()} 件")
        """),
        md("step4", """
            ## 4. 全文検索を実行

            `search_type="fulltext"` を指定し、検索対象のテキスト列を `.text_column()` で指定します。
            スコアは `match_score`: 大きいほど一致度が高い。
        """),
        code("search", """
            QUERY = "分散 トランザクション"
            results = (
                table.search(QUERY, search_type="fulltext")
                .text_column("body")
                .limit(5)
                .to_pydantic()
            )

            print(f"Query: {QUERY}\\n")
            for i, r in enumerate(results, 1):
                print(f"{i}. [{r.hit.language}] {r.hit.title}")
                print(f"    match_score={r.match_score:.4f}")
        """),
        md("step5", """
            ## 5. フィルタと組み合わせる

            言語別に絞る、タイトル列で検索するなど。
        """),
        code("filter", """
            # 日本語の記事から "ベクトル" を検索
            results = (
                table.search("ベクトル", search_type="fulltext")
                .text_column("body")
                .filter({"language": "ja"})
                .limit(3)
                .to_pydantic()
            )
            print("[日本語, body に 'ベクトル']")
            for r in results:
                print(f"  {r.match_score:.3f}  {r.hit.title}")

            # title 列で検索
            print("\\n[title 列で 'search' を検索]")
            results = (
                table.search("search", search_type="fulltext")
                .text_column("title")
                .limit(5)
                .to_pydantic()
            )
            for r in results:
                print(f"  {r.match_score:.3f}  [{r.hit.language}] {r.hit.title}")
        """),
        md("step6", """
            ## 6. 全文検索 vs ベクトル検索

            全文検索はキーワードの正確な一致に強く、ベクトル検索は意味の近さに強い、という違いがあります。
            両方の良いとこ取りをするのが次回 (`05_hybrid_search.ipynb`) のハイブリッド検索です。
        """),
        md("next", """
            ## 次のステップ
            - `05_hybrid_search.ipynb` : ベクトル + 全文 + 結果フュージョン

            ## 追加実験
            - 英語のクエリ (`"retrieval"`) で日本語記事がどう扱われるか試す
            - 表記ゆれ (`"トランザクション" vs "トランザクシヨン"`) が match_score にどう影響するか見る
            - `fts_parser="STANDARD"` に変えて挙動の違いを確認 (再作成が必要)
        """),
    ]
    return build_notebook(cells)


# ----------------------------------------------------------------------------
# 05_hybrid_search.ipynb
# ----------------------------------------------------------------------------

def build_05_hybrid() -> dict:
    name = "05_hybrid_search.ipynb"
    cells = [
        md("badge", f"{colab_badge(name)}"),
        md("title", """
            # ハイブリッド検索 (EC 商品カタログ)

            このノートブックは **pytidb シリーズの第 5 回** です。ベクトル検索と全文検索の結果を融合 (fusion) する「ハイブリッド検索」を扱います。

            ## 学習目標
            - 1 つのテーブルに `VectorField` と `FullTextField` を共存させる
            - `search_type="hybrid"` でハイブリッド検索を行う
            - `fusion` のアルゴリズム (`rrf` / `weighted`) を切り替える
            - ベクトル単独・全文単独・ハイブリッドの結果を見比べる

            前提: `03_vector_search.ipynb` と `04_fulltext_search.ipynb` を実行済み。
        """),
        md("step1", "## 1. 依存と接続"),
        code("install", INSTALL_BASIC),
        code("provision", provision_code(tag="pytidb-hybrid")),
        md("step2", """
            ## 2. 商品カタログテーブル

            `name` は全文検索用、`description` はベクトル検索用 (自動埋め込み) にします。
        """),
        code("schema", """
            from pytidb import TiDBClient
            from pytidb.datatype import TEXT
            from pytidb.embeddings import EmbeddingFunction
            from pytidb.schema import Field, FullTextField, TableModel

            db = TiDBClient.connect(
                host=conn["host"],
                port=4000,
                username=conn["username"],
                password=conn["password"],
                database="shop_demo",
                ensure_db=True,
            )

            _embed = EmbeddingFunction(model_name="tidbcloud_free/amazon/titan-embed-text-v2")


            class Product(TableModel):
                __tablename__ = "products"
                __table_args__ = {"extend_existing": True}

                id: int = Field(primary_key=True)
                category: str = Field()
                price: int = Field()
                name: str = FullTextField(fts_parser="MULTILINGUAL")
                description: str = Field(sa_type=TEXT)
                description_vec: list[float] = _embed.VectorField(source_field="description")


            table = db.create_table(schema=Product, if_exists="overwrite")
            print("テーブル準備OK:", table.table_name)
        """),
        md("step3", "## 3. サンプル商品を投入"),
        code("insert", """
            PRODUCTS = [
                ("electronics", 12800, "ワイヤレスノイズキャンセリングイヤホン",
                 "周囲の騒音を打ち消しながら音楽や通話を楽しめる完全ワイヤレス型のイヤホン。通勤や旅行で集中したい人向け。"),
                ("electronics", 28900, "コンパクトドローン 4K カメラ付き",
                 "折りたたんでカバンに入る小型ドローン。屋外で空撮を楽しみたい初心者から中級者に。"),
                ("electronics", 9800,  "スマートポータブル加湿器",
                 "USB 給電の小型加湿器。オフィスや枕元で乾燥を防ぎ、静音設計で在宅勤務に最適。"),
                ("kitchen",     4980,  "圧力調理マルチポット",
                 "圧力・蒸し・炒めができる一台多役の調理器。忙しい平日の夕食づくりを 30 分で終わらせたい人向け。"),
                ("kitchen",     1980,  "ステンレスコーヒードリッパー",
                 "紙フィルター不要の金属メッシュドリッパー。豆の油分まで抽出できて、コーヒーを毎日淹れる人におすすめ。"),
                ("kitchen",     3480,  "電動ミル付きペッパーグラインダー",
                 "ボタン一つでスパイスを挽ける電動式グラインダー。料理の仕上げに挽きたての香りを楽しめる。"),
                ("outdoor",     15800, "軽量登山テント 2 人用",
                 "総重量 1.9kg の軽量テント。2 人が快適に泊まれるサイズで、縦走やキャンプツーリングに最適。"),
                ("outdoor",     6980,  "防水リュック 30L",
                 "完全防水素材を使った 30L のリュック。雨天の通勤や川沿いのアウトドアで中身を守る。"),
                ("outdoor",     2980,  "折りたたみチタンマグカップ",
                 "薄くて軽いチタン製のマグカップ。キャンプや登山で温かい飲み物をすぐに楽しめる。"),
                ("fashion",     4280,  "メリノウール ベースレイヤー",
                 "冬のアウトドアにも普段着にも使えるメリノウール製の長袖インナー。臭いを抑える天然素材。"),
                ("fashion",     8900,  "撥水ライトシェルジャケット",
                 "急な雨や風を防ぐ軽量シェル。自転車通勤やハイキングで羽織るのに便利なアウター。"),
                ("fashion",     1280,  "シンプルコットンTシャツ",
                 "肉厚のコットンを使ったユニセックスのTシャツ。普段使いのローテに入れやすいベーシック。"),
            ]

            table.bulk_insert([
                Product(id=i + 1, category=c, price=p, name=n, description=d)
                for i, (c, p, n, d) in enumerate(PRODUCTS)
            ])
            print(f"投入完了: {table.rows()} 件")
        """),
        md("step4", """
            ## 4. ベクトル単独 vs 全文単独 を先に見る

            同じクエリ「雨の日の通勤が快適になるもの」で比較します。
            ベクトル検索は意味の近いものを、全文検索は「雨」「通勤」など単語一致を重視します。
        """),
        code("compare", """
            QUERY = "雨の日の通勤が快適になるもの"

            print("[ベクトル検索]")
            for r in table.search(QUERY, search_type="vector").text_column("description").limit(5).to_pydantic():
                print(f"  sim={r.similarity_score:.3f}  {r.hit.name}")

            print("\\n[全文検索]")
            for r in table.search(QUERY, search_type="fulltext").text_column("name").limit(5).to_pydantic():
                print(f"  ms={r.match_score:.3f}  {r.hit.name}")
        """),
        md("step5", """
            ## 5. ハイブリッド検索 (既定: RRF)

            `search_type="hybrid"` を指定すると、ベクトル結果と全文結果を **Reciprocal Rank Fusion (RRF)** で結合します。
            どちらのランクでも上位に登場するドキュメントが優先されます。
        """),
        code("hybrid_rrf", """
            results = (
                table.search(QUERY, search_type="hybrid")
                .text_column("name")
                .vector_column("description_vec")
                .limit(5)
                .to_pydantic()
            )
            print(f"[hybrid (RRF)] Query: {QUERY}")
            for r in results:
                print(f"  score={r.score:.4f}  [{r.hit.category}] {r.hit.name}")
        """),
        md("step6", """
            ## 6. ハイブリッド検索 (weighted)

            `.fusion(method="weighted", vs_weight=..., fts_weight=...)` で重み付き結合に切り替えます。
            ベクトル寄りにしたい場合は `vs_weight` を大きく、キーワード寄りにしたい場合は `fts_weight` を大きくします。
        """),
        code("hybrid_weighted", """
            results = (
                table.search(QUERY, search_type="hybrid")
                .text_column("name")
                .vector_column("description_vec")
                .fusion(method="weighted", vs_weight=0.7, fts_weight=0.3)
                .limit(5)
                .to_pydantic()
            )
            print(f"[hybrid (weighted, vs=0.7/fts=0.3)] Query: {QUERY}")
            for r in results:
                print(f"  score={r.score:.4f}  [{r.hit.category}] {r.hit.name}")
        """),
        md("step7", """
            ## 7. カテゴリフィルタと組み合わせる

            ハイブリッド検索も `.filter()` と併用できます。
        """),
        code("filter", """
            results = (
                table.search("山でも普段でも使える", search_type="hybrid")
                .text_column("name")
                .vector_column("description_vec")
                .filter({"category": {"$in": ["outdoor", "fashion"]}})
                .limit(5)
                .to_pydantic()
            )
            for r in results:
                print(f"  score={r.score:.4f}  [{r.hit.category}] {r.hit.name}")
        """),
        md("next", """
            ## 追加実験

            - `vs_weight=0.3, fts_weight=0.7` に変えて、結果がキーワード寄りになることを確認
            - クエリを英語 (`"cheap coffee gear"`) にして、ベクトルと全文の差を感じる
            - RRF の `k` 係数 (`.fusion(method="rrf", k=40)`) で並びがどう変わるかテスト
        """),
    ]
    return build_notebook(cells)


# ----------------------------------------------------------------------------
# 07_memory.ipynb
# ----------------------------------------------------------------------------

def build_07_memory() -> dict:
    name = "07_memory.ipynb"
    cells = [
        md("badge", f"{colab_badge(name)}"),
        md("title", """
            # AI エージェントの永続メモリ (ユーザー × 発言ログ)

            このノートブックは **pytidb シリーズの第 7 回** です。ベクトル検索を使って AI エージェントに「過去の文脈を思い出す」能力を付与します。

            ## 学習目標
            - `user_id` でマルチユーザー対応した `memories` テーブルを作る
            - 新しい発言から事実を抽出 (`google.colab.ai.generate_text`) し、ベクトル化して保存
            - 質問に応じて過去メモリをベクトル検索で呼び戻し、LLM プロンプトに差し込む
            - RAG (外部ドキュメント) と memory (対話履歴) の違いを理解する

            前提: `03_vector_search.ipynb`、`06_rag.ipynb` を実行済み。
            本ノートブックは **Google Colab 前提** です (`google.colab.ai` を利用)。
        """),
        md("step1", "## 1. 依存と接続"),
        code("install", INSTALL_BASIC),
        code("provision", provision_code(tag="pytidb-memory")),
        md("step2", """
            ## 2. メモリテーブル

            1 行 = 1 つの「覚えておきたい事実」。`user_id` でマルチユーザーに対応します。
            `content` は TEXT、自動埋め込みで `content_vec` が生成されます。
        """),
        code("schema", """
            import datetime
            from pytidb import TiDBClient
            from pytidb.datatype import TEXT
            from pytidb.embeddings import EmbeddingFunction
            from pytidb.schema import Field, TableModel

            db = TiDBClient.connect(
                host=conn["host"],
                port=4000,
                username=conn["username"],
                password=conn["password"],
                database="memory_demo",
                ensure_db=True,
            )

            _embed = EmbeddingFunction(model_name="tidbcloud_free/amazon/titan-embed-text-v2")


            class Memory(TableModel):
                __tablename__ = "memories"
                __table_args__ = {"extend_existing": True}

                id: int = Field(default=None, primary_key=True)
                user_id: str = Field(max_length=32)
                content: str = Field(sa_type=TEXT)
                content_vec: list[float] = _embed.VectorField(source_field="content")
                created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


            table = db.create_table(schema=Memory, if_exists="overwrite")
            print("テーブル準備OK:", table.table_name)
        """),
        md("step3", """
            ## 3. 事実抽出 + 保存のヘルパー関数

            会話スニペットから「覚えておくべき事実」を抽出し、ユーザーごとに保存します。
            抽出には `google.colab.ai.generate_text()` を使います。
        """),
        code("helpers", """
            from google.colab import ai

            EXTRACT_PROMPT = \"\"\"以下のユーザー発言から、今後の会話で思い出すと有益な「事実」を 1 行 1 件、箇条書きにしてください。
            事実以外の説明や記号は入れないでください。該当がなければ空行のみを返してください。

            ユーザー発言:
            {utterance}
            \"\"\"


            def extract_and_store(user_id: str, utterance: str) -> list[str]:
                \"\"\"ユーザーの発言から事実を抽出してメモリに保存する\"\"\"
                raw = ai.generate_text(EXTRACT_PROMPT.format(utterance=utterance))
                facts = [line.lstrip("-・ ").strip() for line in raw.splitlines() if line.strip()]
                for f in facts:
                    table.insert(Memory(user_id=user_id, content=f))
                return facts


            def recall(user_id: str, query: str, limit: int = 3) -> list[str]:
                \"\"\"ユーザーごとに関連メモリをベクトル検索で思い出す\"\"\"
                results = (
                    table.search(query)
                    .filter({"user_id": user_id})
                    .limit(limit)
                    .to_pydantic()
                )
                return [r.hit.content for r in results]
        """),
        md("step4", """
            ## 4. 2 人分の会話履歴を投入する

            Alice と Bob の過去発言を入れて、それぞれの事実を抽出・保存します。
        """),
        code("seed", """
            alice_utterances = [
                "私は Python を 5 年くらい書いています。仕事ではデータ分析が中心です。",
                "コーヒーはブラック派で、朝はエスプレッソを 1 杯飲みます。",
                "最近は Tokyo で開催される PyCon JP に毎年参加しています。",
            ]
            bob_utterances = [
                "I am working on a Go backend for an e-commerce startup in Berlin.",
                "I prefer tea over coffee, especially Japanese green tea.",
                "I attended KubeCon in Europe last year and gave a short talk.",
            ]
            for u in alice_utterances:
                facts = extract_and_store("alice", u)
                print(f"[alice] {len(facts)} fact(s) stored")
            for u in bob_utterances:
                facts = extract_and_store("bob", u)
                print(f"[bob]   {len(facts)} fact(s) stored")
            print(f"合計メモリ: {table.rows()} 件")
        """),
        md("step5", """
            ## 5. 呼び戻し + LLM 応答

            ユーザーごとに、質問に関連するメモリを取り出してプロンプトに埋め込みます。
            同じ質問でも、ユーザーによって使えるメモリが異なるので回答も変わります。
        """),
        code("chat", """
            ANSWER_PROMPT = \"\"\"あなたはユーザーの好みを知っているアシスタントです。
            以下の「メモリ」だけを根拠に、ユーザーの質問へ日本語で丁寧に答えてください。

            --- メモリ ---
            {memories}
            --- ここまで ---

            質問: {question}
            \"\"\"


            def answer(user_id: str, question: str) -> str:
                memories = recall(user_id, question, limit=4)
                mem_text = "\\n".join(f"- {m}" for m in memories) or "(該当メモリなし)"
                prompt = ANSWER_PROMPT.format(memories=mem_text, question=question)
                return ai.generate_text(prompt).strip()


            question = "このユーザーにおすすめの飲み物は何ですか?"
            for uid in ("alice", "bob"):
                print(f"=== {uid} ===")
                print(answer(uid, question))
                print()
        """),
        md("next", """
            ## 追加実験
            - 新しい発言 (`extract_and_store`) を追加したあとに再度質問してみる
            - `recall(..., limit=1)` で 1 件だけ呼び戻して、回答の具体性がどう変わるか見る
            - `created_at` で期間フィルタ (`filter={"created_at": {"$gte": ...}}`) をかけ、最近の記憶だけを使う
        """),
    ]
    return build_notebook(cells)


# ----------------------------------------------------------------------------
# 08_text2sql.ipynb
# ----------------------------------------------------------------------------

def build_08_text2sql() -> dict:
    name = "08_text2sql.ipynb"
    cells = [
        md("badge", f"{colab_badge(name)}"),
        md("title", """
            # Text2SQL (自然言語 → SQL、売上トランザクション)

            このノートブックは **pytidb シリーズの第 8 回** です。自然言語の質問を SQL に変換し、TiDB で実行して結果を返すミニ text2sql を組み立てます。

            ## 学習目標
            - テーブル定義 (`SHOW CREATE TABLE`) をプロンプトに埋め込む
            - `google.colab.ai.generate_text` で SQL を生成する
            - `db.query(sql)` で生成された SQL を実行する
            - 生成された SQL の危険性 (書き込み系など) をチェックする
            - 結果を LLM でマークダウン整形する

            前提: `00_quickstart.ipynb` / `02_query_and_filter.ipynb` を実行済み。
            本ノートブックは **Google Colab 前提** です。
        """),
        md("step1", "## 1. 依存と接続"),
        code("install", INSTALL_BASIC),
        code("provision", provision_code(tag="pytidb-text2sql")),
        md("step2", """
            ## 2. 売上トランザクションのサンプルデータを用意

            売上 (sales)、商品 (products)、店舗 (stores) の 3 テーブル構成にします。
        """),
        code("schema", """
            from datetime import date
            from pytidb import TiDBClient
            from pytidb.schema import Field, TableModel

            db = TiDBClient.connect(
                host=conn["host"],
                port=4000,
                username=conn["username"],
                password=conn["password"],
                database="sales_demo",
                ensure_db=True,
            )


            class Store(TableModel):
                __tablename__ = "stores"
                __table_args__ = {"extend_existing": True}
                id: int = Field(primary_key=True)
                name: str = Field()
                region: str = Field()


            class Product(TableModel):
                __tablename__ = "products"
                __table_args__ = {"extend_existing": True}
                id: int = Field(primary_key=True)
                name: str = Field()
                category: str = Field()
                unit_price: int = Field()


            class Sale(TableModel):
                __tablename__ = "sales"
                __table_args__ = {"extend_existing": True}
                id: int = Field(primary_key=True)
                store_id: int = Field()
                product_id: int = Field()
                sold_on: date = Field()
                quantity: int = Field()


            stores_tbl   = db.create_table(schema=Store,   if_exists="overwrite")
            products_tbl = db.create_table(schema=Product, if_exists="overwrite")
            sales_tbl    = db.create_table(schema=Sale,    if_exists="overwrite")
            print("3 テーブル準備OK")
        """),
        code("seed", """
            stores_tbl.bulk_insert([
                Store(id=1, name="新宿店", region="関東"),
                Store(id=2, name="梅田店", region="関西"),
                Store(id=3, name="博多店", region="九州"),
            ])
            products_tbl.bulk_insert([
                Product(id=1, name="ワイヤレスイヤホン", category="electronics", unit_price=12800),
                Product(id=2, name="圧力調理マルチポット", category="kitchen",   unit_price=4980),
                Product(id=3, name="登山テント 2 人用",    category="outdoor",   unit_price=15800),
                Product(id=4, name="コットンTシャツ",      category="fashion",   unit_price=1280),
            ])
            sales_tbl.bulk_insert([
                Sale(id=1, store_id=1, product_id=1, sold_on=date(2026, 3, 1),  quantity=3),
                Sale(id=2, store_id=1, product_id=2, sold_on=date(2026, 3, 2),  quantity=2),
                Sale(id=3, store_id=2, product_id=1, sold_on=date(2026, 3, 5),  quantity=4),
                Sale(id=4, store_id=2, product_id=3, sold_on=date(2026, 3, 8),  quantity=1),
                Sale(id=5, store_id=3, product_id=4, sold_on=date(2026, 3, 10), quantity=10),
                Sale(id=6, store_id=1, product_id=4, sold_on=date(2026, 3, 15), quantity=6),
                Sale(id=7, store_id=3, product_id=2, sold_on=date(2026, 3, 20), quantity=3),
                Sale(id=8, store_id=2, product_id=4, sold_on=date(2026, 3, 25), quantity=5),
                Sale(id=9, store_id=1, product_id=3, sold_on=date(2026, 4, 1),  quantity=2),
                Sale(id=10, store_id=3, product_id=1, sold_on=date(2026, 4, 3), quantity=2),
            ])
            print(f"投入完了: stores={stores_tbl.rows()} / products={products_tbl.rows()} / sales={sales_tbl.rows()}")
        """),
        md("step3", """
            ## 3. スキーマをプロンプトに埋め込むヘルパー

            LLM が正しい SQL を書けるよう、各テーブルの `CREATE TABLE` 文をそのまま渡します。
        """),
        code("schema_helper", """
            def get_schema_snippet() -> str:
                parts = []
                for t in db.list_tables():
                    row = db.query(f"SHOW CREATE TABLE `{t}`").to_rows()[0]
                    # 行は (table_name, create_sql)
                    parts.append(row[1])
                return "\\n\\n".join(parts)

            print(get_schema_snippet()[:1200], "...")
        """),
        md("step4", """
            ## 4. 質問を SQL に変換する

            プロンプトにルール (SELECT のみ、未定義列を作らない等) を明記します。
            生成結果は SQL テキストだけを期待します。
        """),
        code("generate_sql", """
            from google.colab import ai
            import re

            SQL_PROMPT = \"\"\"あなたは TiDB / MySQL の熟練 DBA です。与えられたスキーマだけを使って、ユーザーの質問に答える **SELECT 文** を 1 つだけ出力してください。

            ルール:
            - SELECT 文以外 (INSERT / UPDATE / DELETE / DROP など) は絶対に使わない
            - 未定義のテーブルやカラムは作らない
            - バッククォートでテーブル・カラム名を囲む
            - SQL 以外の説明文、記号、コードフェンスは一切つけず、SQL そのものだけを返す

            --- スキーマ ---
            {schema}
            --- ここまで ---

            質問: {question}
            SQL:
            \"\"\"


            def nl_to_sql(question: str) -> str:
                raw = ai.generate_text(SQL_PROMPT.format(schema=get_schema_snippet(), question=question))
                # コードフェンスが混じっていたら剥がす
                m = re.search(r"```(?:sql)?(.*?)```", raw, re.S)
                sql = (m.group(1) if m else raw).strip().rstrip(";")
                return sql


            question = "関東地方の3月の売上金額の合計は?"
            sql = nl_to_sql(question)
            print("生成された SQL:\\n", sql)
        """),
        md("step5", """
            ## 5. 安全チェックして実行する

            生成された SQL がほんとうに読み取り専用か軽く検査してから、`db.query` で実行します。
        """),
        code("execute", """
            WRITE_KEYWORDS = ("insert ", "update ", "delete ", "drop ", "truncate ", "alter ")


            def is_read_only(sql: str) -> bool:
                lower = sql.lower()
                if not lower.lstrip().startswith("select"):
                    return False
                return not any(k in lower for k in WRITE_KEYWORDS)


            def run_nl_query(question: str):
                sql = nl_to_sql(question)
                print("SQL:", sql)
                if not is_read_only(sql):
                    print("[!] 読み取り専用ではない SQL が生成されました。実行を中止します。")
                    return
                rows = db.query(sql).to_rows()
                print(f"結果 ({len(rows)} 行):")
                for r in rows:
                    print(" ", r)


            run_nl_query("関東地方の3月の売上金額の合計は?")
            print()
            run_nl_query("カテゴリ別に売上金額を集計して金額の大きい順に並べて")
            print()
            run_nl_query("店舗ごとに最もよく売れた商品を1つずつ教えて")
        """),
        md("next", """
            ## 追加実験

            - 質問を変えてみる: 「日別の売上トレンド」「商品別の販売数量ランキング」
            - SQL 生成に失敗するケースを探し、`SQL_PROMPT` にルールを追加して改善する
            - 結果を LLM で表形式のマークダウンに整形するセルを追加する
        """),
    ]
    return build_notebook(cells)


# ----------------------------------------------------------------------------
# 09_custom_embedding.ipynb
# ----------------------------------------------------------------------------

def build_09_custom_embedding() -> dict:
    name = "09_custom_embedding.ipynb"
    cells = [
        md("badge", f"{colab_badge(name)}"),
        md("title", """
            # 独自埋め込み関数 (FAQ × sentence-transformers)

            このノートブックは **pytidb シリーズの第 9 回** です。組み込みの TiDB Cloud 埋め込みではなく、ローカルで動く `sentence-transformers` を使った **独自 `BaseEmbeddingFunction`** を実装します。

            ## 学習目標
            - `BaseEmbeddingFunction` を継承してクラスを書く
            - 必須 3 メソッド (`get_query_embedding` / `get_source_embedding` / `get_source_embeddings`) を実装
            - クライアントサイド埋め込み (`use_server=False`) を VectorField に渡す
            - 小型の多言語モデル `intfloat/multilingual-e5-small` (約 120MB) で FAQ 検索を動かす

            前提: `03_vector_search.ipynb` を実行済み。
            API キーは不要。ただし初回のみモデルダウンロードに数十秒かかります。
        """),
        md("step1", """
            ## 1. 依存パッケージのインストール

            今回は `sentence-transformers` を追加インストールします (PyTorch は Colab 既定で入っています)。
        """),
        code("install", "!pip install -q pytidb sentence-transformers"),
        md("step2", "## 2. TiDB Cloud Zero の払い出し"),
        code("provision", provision_code(tag="pytidb-custom-embed")),
        md("step3", """
            ## 3. 独自の BaseEmbeddingFunction を作る

            `sentence-transformers` の多言語小型モデルをラップします。
            モデル: `intfloat/multilingual-e5-small` (384 次元)。日本語を含む 100 以上の言語に対応。
        """),
        code("custom_fn", """
            from typing import Any, List, Optional
            from pytidb.embeddings.base import BaseEmbeddingFunction
            from sentence_transformers import SentenceTransformer


            class E5SmallEmbedding(BaseEmbeddingFunction):
                # pydantic v2 ベースなので内部で持つ HF モデルは PrivateAttr 相当にしないと serialize されない
                # ここでは単純化のため object 型としてアトリビュートに付ける
                model_config = {"arbitrary_types_allowed": True}

                def __init__(self, model_name: str = "intfloat/multilingual-e5-small", **kwargs):
                    # e5 系のモデルは 384 次元。provider は分類用の任意文字列で OK
                    super().__init__(
                        provider="sentence-transformers",
                        model_name=model_name,
                        dimensions=384,
                        use_server=False,   # クライアント側で埋め込む
                        **kwargs,
                    )
                    self.__dict__["_model"] = SentenceTransformer(model_name)

                def _encode(self, texts: List[str]) -> List[List[float]]:
                    # e5 系モデルでは "query:"/"passage:" プリフィクスを付けると検索精度が上がる
                    # ここでは利用者から見て透過的に扱いたいので、シンプルに encode のみを行う
                    arr = self.__dict__["_model"].encode(texts, normalize_embeddings=True)
                    return [row.tolist() for row in arr]

                def get_query_embedding(self, query: Any, source_type: Optional[str] = "text", **kwargs) -> List[float]:
                    return self._encode([f"query: {query}"])[0]

                def get_source_embedding(self, source: Any, source_type: Optional[str] = "text", **kwargs) -> List[float]:
                    return self._encode([f"passage: {source}"])[0]

                def get_source_embeddings(self, sources: List[Any], source_type: Optional[str] = "text", **kwargs) -> List[List[float]]:
                    return self._encode([f"passage: {s}" for s in sources])


            embed_fn = E5SmallEmbedding()
            print("Embedding dim =", embed_fn.dimensions)
            print("sample =", len(embed_fn.get_query_embedding("こんにちは、世界")), "次元ベクトル")
        """),
        md("step4", """
            ## 4. FAQ テーブルを作成 + データ投入

            `question` 列を埋め込み対象にします。`embed_fn.VectorField(source_field="question")` を使うと、自動で投入時に埋め込みが作られます。
        """),
        code("schema", """
            from pytidb import TiDBClient
            from pytidb.datatype import TEXT
            from pytidb.schema import Field, TableModel

            db = TiDBClient.connect(
                host=conn["host"],
                port=4000,
                username=conn["username"],
                password=conn["password"],
                database="faq_demo",
                ensure_db=True,
            )


            class FAQ(TableModel):
                __tablename__ = "faqs"
                __table_args__ = {"extend_existing": True}

                id: int = Field(primary_key=True)
                question: str = Field(sa_type=TEXT)
                answer: str = Field(sa_type=TEXT)
                question_vec: list[float] = embed_fn.VectorField(source_field="question")


            table = db.create_table(schema=FAQ, if_exists="overwrite")
            print("テーブル準備OK:", table.table_name)
        """),
        code("seed", """
            FAQS = [
                ("注文のキャンセルはいつまでできますか?",
                 "発送準備前であればマイページの注文履歴からキャンセルできます。"),
                ("送料はいくらですか?",
                 "通常便は全国一律 550 円、5,000 円以上のお買い上げで送料無料です。"),
                ("海外発送はしていますか?",
                 "現在は日本国内のみの発送となっております。"),
                ("領収書はもらえますか?",
                 "マイページの注文詳細から PDF でダウンロードいただけます。"),
                ("商品が届かないときは?",
                 "発送後 5 営業日を過ぎても届かない場合はカスタマーサポートまでお問い合わせください。"),
                ("返品はできますか?",
                 "未使用・未開封の商品に限り、到着後 7 日以内であれば返品を受け付けます。"),
                ("支払い方法は何が使えますか?",
                 "クレジットカード、コンビニ決済、銀行振込、後払い (Paidy) に対応しています。"),
                ("ポイントの有効期限は?",
                 "最後にポイントを取得または利用した日から 1 年間有効です。"),
                ("会員登録は無料ですか?",
                 "はい。無料で登録でき、登録時に 500 ポイントをプレゼントしています。"),
                ("パスワードを忘れた場合は?",
                 "ログイン画面の「パスワードを忘れた方」から再設定用のメールをお送りします。"),
                ("メルマガを解除したい",
                 "メール下部の購読解除リンク、またはマイページの通知設定から停止できます。"),
                ("プレゼント用にラッピングできますか?",
                 "一部商品を除き、200 円でギフトラッピングを承ります。注文時に選択してください。"),
                ("届いた商品が壊れていた場合は?",
                 "到着後 3 日以内にカスタマーサポートへご連絡ください。無償で交換いたします。"),
                ("注文後に住所を変更したい",
                 "発送準備前であればマイページから変更できます。発送後は配送業者までご連絡ください。"),
                ("店舗でも購入できますか?",
                 "オンライン限定商品は店舗では扱っておりません。その他の商品は各店舗でお買い求めいただけます。"),
            ]

            table.bulk_insert([FAQ(id=i + 1, question=q, answer=a) for i, (q, a) in enumerate(FAQS)])
            print(f"投入完了: {table.rows()} 件")
        """),
        md("step5", """
            ## 5. 独自埋め込みで検索する

            `table.search(QUERY)` の中では、`embed_fn.get_query_embedding(QUERY)` が呼ばれて
            生成された 384 次元のベクトルで検索が行われます。
        """),
        code("search", """
            queries = [
                "キャンセルしたい",
                "送料のことが知りたい",
                "paypayで払えますか?",
                "商品が動かなくて困っています",
                "どれくらいで届きますか?",
            ]
            for q in queries:
                print(f"\\n--- Q: {q}")
                for r in table.search(q).limit(3).to_pydantic():
                    print(f"  sim={r.similarity_score:.3f}  Q:{r.hit.question}")
                    print(f"    A:{r.hit.answer}")
        """),
        md("next", """
            ## 追加実験

            - `intfloat/multilingual-e5-base` (768 次元) に差し替えて精度と速度を比べる
            - `normalize_embeddings=False` にしてスコア挙動がどう変わるか観察
            - `sparse_vecs` を追加するなど独自のマルチベクトル戦略を実装する
        """),
    ]
    return build_notebook(cells)


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# 10_image_search.ipynb
# ----------------------------------------------------------------------------

def build_10_image_search() -> dict:
    name = "10_image_search.ipynb"
    cells = [
        md("badge", f"{colab_badge(name)}"),
        md("title", """
            # 画像検索 / CLIP + pytidb (auto-embedding 版)

            このノートブックは **pytidb シリーズの第 10 回** です。OpenAI の CLIP (ViT-B/32) を pytidb の **auto-embedding API** に接続し、TiDB で画像検索を行います。

            参考: [pytidb `examples/image_search/app.py`](https://github.com/pingcap/pytidb/blob/main/examples/image_search/app.py) の構成を、Colab 無料枠で動くよう CLIP 置き換えで再構築したものです。

            ## 学習目標
            - `BaseEmbeddingFunction` を継承し、`source_type="text"` / `"image"` の両方に対応したマルチモーダル埋め込みクラスを書く
            - `VectorField(source_field="image_uri", source_type="image")` で **画像の auto-embedding 列**を宣言する
            - 画像は **`file://` URI** として TiDB に保存し、pytidb に embed を任せる (`table.bulk_insert` のみで OK)
            - 同じ VectorField に対して **テキスト→画像 検索**と **画像→画像 検索** を両方実行する
              - pytidb は `source_type="image"` を常に `get_query_embedding` に渡すが、我々の wrapper 側で入力型から auto-dispatch する

            ## 注意
            - CLIP ViT-B/32 は **英語**のテキストに最適化されたモデルです。クエリ文は英語で書いてください
            - 初回のみ CLIP DL が走ります (約 150 MB)、Colab の無料枠 (CPU ランタイム) で数十秒〜1 分程度
            - API キーは不要 (CLIP はローカル推論)

            前提: `09_custom_embedding.ipynb` を実行済みだと構造が分かりやすいです。
        """),
        md("step1", """
            ## 1. 依存パッケージのインストール

            追加で `transformers`・`datasets`・`pillow` を入れます (`torch` は Colab に同梱)。
        """),
        code("install", "!pip install -q pytidb transformers datasets pillow"),
        md("step2", "## 2. TiDB Cloud Zero の払い出し"),
        code("provision", provision_code(tag="pytidb-image-search")),
        md("step3", """
            ## 3. URI / PIL 両対応のマルチモーダル CLIP クラス

            `BaseEmbeddingFunction` を継承し、**auto-embedding の流儀**に合わせます:

            - `get_source_embedding(s)`: insert 時に `image_uri` 列の文字列が渡ってくる → `source_type="image"` で画像として読み込む
            - `get_query_embedding`: 検索時、`source_type` は VectorField の宣言値 (`"image"`) が固定で渡るので、**実入力の型から auto-dispatch** (PIL.Image / URI 文字列 → 画像エンコーダ、普通の文字列 → テキストエンコーダ)

            `_load_image()` は `file://` / `http(s)://` / ローカルパス / PIL.Image のどれでも受けて PIL に正規化します。
        """),
        code("clip_class", """
            import io
            import urllib.request
            from pathlib import Path
            from typing import Any, List, Optional

            import requests
            import torch
            from PIL import Image
            from PIL.Image import Image as PILImage
            from transformers import CLIPModel, CLIPProcessor
            from pytidb.embeddings.base import BaseEmbeddingFunction

            CLIP_MODEL = "openai/clip-vit-base-patch32"
            CLIP_DIM = 512
            IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif")


            def _load_image(src: Any) -> PILImage:
                \"\"\"PIL.Image / Path / str (file:// / http(s):// / plain path) を RGB PIL に正規化\"\"\"
                if isinstance(src, PILImage):
                    return src.convert("RGB")
                if isinstance(src, Path):
                    return Image.open(src).convert("RGB")
                if isinstance(src, str):
                    if src.startswith("file://"):
                        path = urllib.request.url2pathname(src[len("file://"):])
                        return Image.open(path).convert("RGB")
                    if src.startswith(("http://", "https://")):
                        data = requests.get(src, timeout=10).content
                        return Image.open(io.BytesIO(data)).convert("RGB")
                    return Image.open(src).convert("RGB")
                raise TypeError(f"unsupported image source: {type(src).__name__}")


            def _is_image_like(x: Any) -> bool:
                \"\"\"入力が画像と判断できるか\"\"\"
                if isinstance(x, (PILImage, Path)):
                    return True
                if isinstance(x, str):
                    if x.startswith(("file://", "http://", "https://")):
                        return True
                    if any(x.lower().endswith(ext) for ext in IMAGE_EXTS):
                        return True
                return False


            class CLIPEmbedding(BaseEmbeddingFunction):
                model_config = {"arbitrary_types_allowed": True}

                def __init__(self, model_name: str = CLIP_MODEL, **kwargs):
                    super().__init__(
                        provider="clip",
                        model_name=model_name,
                        dimensions=CLIP_DIM,
                        use_server=False,
                        **kwargs,
                    )
                    self.__dict__["_model"] = CLIPModel.from_pretrained(model_name)
                    self.__dict__["_processor"] = CLIPProcessor.from_pretrained(model_name)

                @staticmethod
                def _to_tensor(out):
                    # transformers のバージョン差を吸収 (tensor / BaseModelOutputWithPooling 両対応)
                    if hasattr(out, "cpu"):
                        return out
                    for attr in ("text_embeds", "image_embeds", "pooler_output", "last_hidden_state"):
                        v = getattr(out, attr, None)
                        if v is not None and hasattr(v, "cpu"):
                            return v
                    raise TypeError(f"Cannot extract tensor from CLIP output: {type(out).__name__}")

                def _encode_text(self, texts: List[str]) -> List[List[float]]:
                    proc = self.__dict__["_processor"]
                    model = self.__dict__["_model"]
                    with torch.no_grad():
                        inputs = proc(text=texts, return_tensors="pt", padding=True, truncation=True)
                        features = self._to_tensor(model.get_text_features(**inputs))
                    return [row.tolist() for row in features.cpu().numpy()]

                def _encode_images(self, images) -> List[List[float]]:
                    proc = self.__dict__["_processor"]
                    model = self.__dict__["_model"]
                    pil_images = [_load_image(im) for im in images]
                    with torch.no_grad():
                        inputs = proc(images=pil_images, return_tensors="pt")
                        features = self._to_tensor(model.get_image_features(**inputs))
                    return [row.tolist() for row in features.cpu().numpy()]

                # pytidb が呼ぶ 3 つのエントリポイント

                def get_source_embedding(self, source: Any, source_type: Optional[str] = "text", **kwargs) -> List[float]:
                    # insert 時: source は image_uri 列の文字列 (VectorField.source_type="image" で固定)
                    if source_type == "image":
                        return self._encode_images([source])[0]
                    return self._encode_text([str(source)])[0]

                def get_source_embeddings(self, sources: List[Any], source_type: Optional[str] = "text", **kwargs) -> List[List[float]]:
                    if source_type == "image":
                        return self._encode_images(sources)
                    return self._encode_text([str(s) for s in sources])

                def get_query_embedding(self, query: Any, source_type: Optional[str] = "text", **kwargs) -> List[float]:
                    # 検索時: source_type は "image" で常に固定なので実入力から auto-dispatch する
                    if _is_image_like(query):
                        return self._encode_images([query])[0]
                    return self._encode_text([str(query)])[0]


            embed_fn = CLIPEmbedding()
            print("CLIP ready  dim =", embed_fn.dimensions)
        """),
        md("step4", """
            ## 4. テーブル定義 (auto-embedding 列)

            `image_uri` 列に `file://` URI 文字列を入れ、`image_vec` は **`source_field="image_uri"`** + **`source_type="image"`** で自動生成させます。
            この瞬間、insert のときに pytidb が `embed_fn.get_source_embeddings(uris, source_type="image")` を呼び出す経路が出来上がります。
        """),
        code("schema", """
            from pytidb import TiDBClient
            from pytidb.datatype import TEXT
            from pytidb.schema import Field, TableModel

            db = TiDBClient.connect(
                host=conn["host"],
                port=4000,
                username=conn["username"],
                password=conn["password"],
                database="image_search_demo",
                ensure_db=True,
            )


            class ImageRecord(TableModel):
                __tablename__ = "image_records"
                __table_args__ = {"extend_existing": True}

                id: int = Field(primary_key=True)
                label: str = Field()
                image_uri: str = Field(sa_type=TEXT)                    # file:// URI を格納
                image_vec: list[float] = embed_fn.VectorField(
                    source_field="image_uri",
                    source_type="image",
                )


            table = db.create_table(schema=ImageRecord, if_exists="overwrite")
            print("テーブル準備OK:", table.table_name)
        """),
        md("step5", """
            ## 5. サンプル画像をロード + 画像をローカル保存

            `datasets` から ImageNet tiny を 20 枚取得し、Colab のローカルに `.jpg` として保存して `file://` URI を作ります。
            (pytidb の組み込み multimodal example と同じ方式です)
        """),
        code("dataset", """
            import os
            import datasets

            IMG_DIR = "/content/img_pool"
            os.makedirs(IMG_DIR, exist_ok=True)

            ds = datasets.load_dataset("theodor1289/imagenet-1k_tiny", split="train")

            records = []     # [(id, label, image_uri, PIL.Image)] for preview/reference
            for i, row in enumerate(ds):
                if i >= 20:
                    break
                img = row["image"].convert("RGB")
                label = str(row.get("label", row.get("fine_label", "unknown")))
                path = os.path.abspath(os.path.join(IMG_DIR, f"{i:03d}.jpg"))
                img.save(path, "JPEG")
                uri = f"file://{path}"
                records.append((i + 1, label, uri, img))

            print(f"saved {len(records)} images to {IMG_DIR}")
            print("example URI:", records[0][2])
        """),
        md("step5b", "### 画像をインラインで確認する"),
        code("preview", """
            import matplotlib.pyplot as plt

            def show_grid(images, titles=None, cols=5, width=2):
                n = len(images)
                rows = (n + cols - 1) // cols
                fig, axes = plt.subplots(rows, cols, figsize=(cols * width, rows * width))
                axes = axes.flatten() if n > 1 else [axes]
                for ax in axes:
                    ax.axis("off")
                for i, img in enumerate(images):
                    axes[i].imshow(img)
                    if titles:
                        axes[i].set_title(titles[i], fontsize=9)
                plt.tight_layout()
                plt.show()


            show_grid(
                [r[3] for r in records],
                titles=[f"#{r[0]} {r[1]}" for r in records],
            )
        """),
        md("step6", """
            ## 6. bulk_insert だけで自動埋め込み

            `ImageRecord(id, label, image_uri)` を 20 件まとめて `table.bulk_insert(...)` に渡すと、pytidb が内部で
            `embed_fn.get_source_embeddings([uri, uri, ...], source_type="image")` を呼び、画像を CLIP で 512 次元にしてから `image_vec` 列に書き込みます。
            **手動で `get_source_embeddings` を呼ぶ必要はありません。**
        """),
        code("ingest", """
            rows = [
                ImageRecord(id=rid, label=label, image_uri=uri)
                for (rid, label, uri, _) in records
            ]
            table.bulk_insert(rows)
            print(f"投入完了: {table.rows()} 件")
        """),
        md("step7", """
            ## 7. テキスト → 画像 検索

            `table.search("a photo of a dog")` をそのまま呼ぶだけ。pytidb は自動で `get_query_embedding` を呼び、我々の wrapper が **テキスト入力** を検出してテキストエンコーダを使います。
        """),
        code("text_search", """
            QUERIES = ["a photo of a dog", "sushi on a plate", "a classic sports car"]

            for q in QUERIES:
                hits = table.search(q).limit(5).to_pydantic()
                print(f"\\n=== query: {q!r} ===")
                imgs = [_load_image(h.hit.image_uri) for h in hits]
                titles = [f"sim={h.similarity_score:.3f}\\n[{h.hit.label}]" for h in hits]
                show_grid(imgs, titles=titles, cols=5)
        """),
        md("step8", """
            ## 8. 画像 → 画像 検索

            検索対象にも `table.search(pil_image)` と PIL Image を直接渡せます。wrapper が `PIL.Image` を検出して画像エンコーダを使います。
            top-1 は必ずクエリ自身 (sim≈1.0) になります。
        """),
        code("image_search", """
            # データセット先頭の 1 枚をクエリにする
            query_image = records[0][3]
            print("Query image:")
            show_grid([query_image], titles=["query"], cols=1)

            hits = table.search(query_image).limit(5).to_pydantic()

            print("\\n=== top-5 similar images ===")
            imgs = [_load_image(h.hit.image_uri) for h in hits]
            titles = [f"sim={h.similarity_score:.3f}\\n[{h.hit.label}]" for h in hits]
            show_grid(imgs, titles=titles, cols=5)
        """),
        md("next", """
            ## 追加実験

            - `table.search("...")` / `table.search(pil_image)` のどちらでも **同じ image_vec 列**が使われていることを確認
            - `QUERIES` に英語フレーズを追加 / 外部画像 URL (`https://...`) を直接 `table.search(url)` に渡す (wrapper 側で自動ロード)
            - `table.search(...).distance_threshold(0.5).limit(10)` で閾値による足切り
            - CLIP を **`openai/clip-vit-large-patch14`** (約 900 MB、768 次元) に差し替え → `CLIP_DIM = 768` に注意
            - **真の multimodal auto-embedding** として pytidb 組み込みの `EmbeddingFunction("jina_ai/jina-embeddings-v4", multimodal=True)` を試す場合は `JINA_AI_API_KEY` を `os.environ` にセット (有料)
        """),
    ]
    return build_notebook(cells)


BUILDERS = {
    "00_quickstart.ipynb":         build_00_quickstart,
    "01_schema_and_types.ipynb":   build_01_schema,
    "02_query_and_filter.ipynb":   build_02_query,
    "03_vector_search.ipynb":      build_03_vector,
    "04_fulltext_search.ipynb":    build_04_fts,
    "05_hybrid_search.ipynb":      build_05_hybrid,
    "07_memory.ipynb":             build_07_memory,
    "08_text2sql.ipynb":           build_08_text2sql,
    "09_custom_embedding.ipynb":   build_09_custom_embedding,
    "10_image_search.ipynb":       build_10_image_search,
}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename, build_fn in BUILDERS.items():
        nb = build_fn()
        path = OUT_DIR / filename
        with path.open("w", encoding="utf-8") as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print(f"wrote {path.relative_to(OUT_DIR.parent)}")


if __name__ == "__main__":
    main()
