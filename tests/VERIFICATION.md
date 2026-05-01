# Colab 動作確認ガイド

各ノートブックを Colab で実行するときの **成功判定の目印** と **詰まったときの切り分け手順** をまとめたメモ。Claude と画面共有しながら流すと早い。

リポジトリは **フレームワーク別に 2 系統**に分かれています:
- `tutorials/pytidb/` (00〜10、11 本) — pytidb 公式 SDK 版
- `tutorials/llamaindex/` (00〜01、2 本) — LlamaIndex の `TiDBVectorStore` 版

## 全体の準備

- Colab は **CPU ランタイム** で十分 (pytidb 06/07/08 の LLM 部分以外)
- pytidb 08/09/10 は **GPU ランタイム** にしてもよいが、無くても動く (10 は CPU でも CLIP 推論可能)
- LLM を使うセル (`google.colab.ai`) は **Colab ログイン必須**
- LlamaIndex 版は **ローカル実行**もサポート (LM Studio + OpenAI 互換 API)
- TiDB Cloud Zero はサインアップ不要。1 ノートブック = 1 クラスタ作成

**pytidb 推奨順**: 00 → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10
初めての場合は 00 + 03 + 06 + 10 の 4 本だけでも全体像が掴めます。

**LlamaIndex 版**は pytidb 版 06 / 05 の知識を前提にした「同じ題材を別 SDK で組み直す」位置付け。pytidb 版を一通り回した後がおすすめ。

## 所要時間の目安

### pytidb 版 (`tutorials/pytidb/`)

| # | 時間 (累計) | 備考 |
|---|---|---|
| 00 | 2 分 | 最初にプロビジョニングで 20-30 秒 |
| 01 | 2 分 | JSON 列操作が主、軽い |
| 02 | 3 分 | フィルタ・トランザクション検証含む |
| 03 | 3 分 | ベクトル検索待ち 5-10 秒/クエリ |
| 04 | 2 分 | 全文検索 |
| 05 | 3 分 | ベクトル + 全文、RRF / weighted 比較 |
| 06 | 3 分 | LLM 応答で 5-10 秒 |
| 07 | 5 分 | LLM を抽出/応答で複数回呼ぶ |
| 08 | 3 分 | LLM で SQL 生成 + 実行 |
| 09 | 4 分 | 初回 sentence-transformers DL (~120 MB) |
| 10 | 5 分 | 初回 CLIP DL (~150 MB) + datasets DL |
| 合計 | 約 35-45 分 | キャッシュ効けば再実行は半分 |

### LlamaIndex 版 (`tutorials/llamaindex/`)

| # | 時間 | 備考 |
|---|---|---|
| 00 | 4-5 分 | e5-small (~120MB) DL + LLM 推論 2 回 |
| 01 | 5-7 分 | e5-small DL + FTS index の columnar replica 同期で~1 分待機 |

---

# pytidb 版チェックリスト

## 00_quickstart

| セル | 期待出力 | NG のサイン |
|---|---|---|
| install | エラーなく終了 | pip エラー → Colab ランタイム再起動 |
| provision | `Host : xxx` / `Expires : 2026-...` / claim URL が表示 | `HTTPError 429` → 1 分待って再実行 |
| connect | `接続OK: quickstart_demo` + `テーブル準備OK: tasks` | `OperationalError` → host/pw の取得失敗 |
| insert | `投入完了。現在の件数: 4` | 件数が 4 以外 → セルの再実行で上書き再作成されること確認 |
| query | `[ ] #1` 〜 `[ ] #4` の 4 行 | |
| update_delete | `[x] #1` 表示、#4 が消えて `合計: 3 件` | |

## 01_schema_and_types

- `投入完了。件数: 3`
- JSON 読み出しで `authors=['白井 翔', 'Mia Hoffmann']` / `topics=['raft', 'paxos']` が見える
- 評価 4.3 以上: **1 件** (id=2、分散システム入門 rating=4.6)
  - 幻想機械の設計図 (4.2) と Tea and Tectonics (4.0) は対象外
- `genre=tech` の本: 1 件

## 02_query_and_filter

- 9 件投入 (電器 3 / 食 3 / ファッション 3)
- 価格 5000 円以下: **6 件** (USB-C ケーブル 890, エスプレッソ粉 1280, 抹茶パウダー 2480, ダークチョコ 580, 帆布トートバッグ 3980, ウールソックス 1280)
- 在庫切れ: `['A-003', 'C-002']`
- grocery 10% 値上げ後、在庫 0 商品 2 件削除 → 残り 7 件
- トランザクション: electronics 合計が -5、fashion 合計が +5 動くこと

## 03_vector_search

- 20 件投入、category は tech/sports/food/science 各 5
- 「宇宙や物理学の新しい発見」→ top-5 は science が占めるはず
- food フィルタ付き: 3 件とも food のみ
- `distance_threshold(0.5)`: 0 件 〜 数件 (キャッシュなしだと 2-3 件が目安)

## 04_fulltext_search

- 9 件投入 (ja 6 / en 3)
- 「分散 トランザクション」→ top は「分散トランザクションの基礎」(match_score 1.5 前後)
  - 検索対象は `body` 列なので、本文に「分散」と「トランザクション」の両方を含む記事が上位に来る
- 「ベクトル」フィルタ ja: 「ベクトル検索を始めよう」が top
- title で「search」: 「Hybrid search explained」が top

## 05_hybrid_search

- 12 件投入
- 同じクエリでベクトル検索と全文検索で結果が異なること
- hybrid (RRF) の score は `0〜1` の小さい値 (RRF の性質)
- hybrid (weighted, vs=0.7): 「撥水ライトシェルジャケット」系が上位
- hybrid (weighted, vs=0.3): 「雨」「通勤」を名前に含む商品が上位 (FTS 寄り)

## 06_rag

- 10 件のレシピ投入
- 「さっぱり食べられる和風の温かい料理」→ 霧氷豆腐の白湯がけ が top 3 に入る
- LLM 回答が料理名 + 説明の形で日本語で返る
- 「火を使わずに作れる料理」→ 月光麻婆冷奴 / 海風ガスパチョ / 雪見みたらし系が出る

## 07_memory

- `テーブル準備OK: memories`
- alice の発言 3 本 → それぞれ 1-3 facts 抽出
- bob の発言 3 本 → 同様
- 最終的に `合計メモリ: 10-20 件` 程度
- `answer("alice", "...飲み物...")` → コーヒー (エスプレッソ) 推奨の回答
- `answer("bob", "...飲み物...")` → 日本茶 (緑茶) 推奨の回答
- **異なるユーザーで異なる回答**になることが最大の確認ポイント

## 08_text2sql

- 3 テーブル (stores / products / sales) が作られる
- `get_schema_snippet()` 出力で 3 つの `CREATE TABLE ...` 文が見える
- 「関東地方の3月の売上金額合計」→ SQL: `SELECT SUM(s.quantity * p.unit_price) ... WHERE region='関東' AND sold_on BETWEEN ...` 系
- **期待結果**: 新宿店の 3 月売上 = (12800 * 3) + (4980 * 2) + (1280 * 6) = 55,960 円
- 「カテゴリ別」→ GROUP BY 付き SQL、`ORDER BY ... DESC`
- **危険判定**: 万一 DML が生成されたら `[!] ... 中止します` が出ること
- SQL 生成が失敗するケース: プロンプト改善を `追加実験` として試す

## 09_custom_embedding

- 初回のみ `intfloat/multilingual-e5-small` が DL (~120 MB)
- `Embedding dim = 384` / `sample = 384 次元ベクトル`
- `テーブル準備OK: faqs`
- 15 件投入
- 5 個のクエリで それぞれ上位 3 件の FAQ が表示される
  - 「キャンセルしたい」→ 注文キャンセルの FAQ が top
  - 「paypayで払えますか?」→ 支払い方法の FAQ が top
  - 「どれくらいで届きますか?」→ 商品が届かないときは の FAQ が top
- 日本語だけで検索ができている = 多言語モデルが機能している

## 10_image_search (auto-embedding 版)

- 初回 DL: CLIP (~150 MB) + ImageNet tiny データセット (~20 MB)
- `CLIP ready  dim = 512`
- `/content/img_pool/` に 20 枚の `.jpg` が保存され、`example URI: file:///content/img_pool/000.jpg` のような出力
- 20 枚の画像がグリッド表示される
- **`投入完了: 20 件`** — ここで `table.bulk_insert(rows)` のみ実行。pytidb が内部で `embed_fn.get_source_embeddings([uri, ...], source_type="image")` を呼び、CLIP で 512 次元化して自動的に `image_vec` 列に書き込む (手動 embedding 不要)
- **テキスト → 画像** `table.search("a photo of a dog").limit(5)` を直接呼ぶ:
  - `"a photo of a dog"` → 犬系の画像が上位
  - `"sushi on a plate"` → 食べ物系 (厳密に寿司じゃなくても OK、データセット次第)
  - `"a classic sports car"` → 車 or 乗り物系
  - wrapper 側で `_is_image_like("a photo of a dog") == False` と判定されテキストエンコーダが走る
- **画像 → 画像** `table.search(pil_image).limit(5)` を直接呼ぶ:
  - クエリ画像 (データセット先頭) の類似が上位 5 枚、先頭は自分自身で sim ≈ 1.0
  - wrapper 側で `PIL.Image` を検出して画像エンコーダが走る
- **同じ VectorField で両方向の検索ができる**ことが最大の確認ポイント

---

# LlamaIndex 版チェックリスト

## llamaindex/00_rag

- 初回 DL: `intfloat/multilingual-e5-small` (~120MB)
- `embed_model: intfloat/multilingual-e5-small`
- LLM 行: `LLM: google.colab.ai` (Colab) または `LLM: LM Studio (google/gemma-4-e2b)` (ローカル)
- `Document 件数: 10`
- `インデックス作成完了`
- ベクトル検索ヒット top-1 が **霧氷豆腐の白湯がけ** (sim=0.85 前後)
- `=== LLM 回答 ===` セクションで日本語の回答テキストが返る (例: 霧氷豆腐 / 白湯 / 和風 のいずれかが含まれる)
- チャレンジ (火を使わない料理): 月光麻婆冷奴 / 海風ガスパチョ / 雪見みたらしクレープ のいずれかを提案

## llamaindex/01_hybrid_search

- `投入完了: 12 件`
- `FTS index DDL 実行` 後 **`FTS インデックス利用可能まで待機中… 利用可能`** が出る (最大 180 秒待機、TiDB Cloud Zero では 60〜180 秒程度かかる)
- ベクトル単独 vs 全文単独で順位が異なることを確認
  - ベクトル top: `防水リュック 30L` / `撥水ライトシェルジャケット` のどちらかが top
  - 全文 top: `撥水ライトシェルジャケット` (「雨」「通勤」が一致)
- ハイブリッド (RRF): 上位 5 件で **重複なし** ★重要
  - `撥水ライトシェルジャケット` が 1 回だけ登場 (vec/fts 両方でヒットするため最上位付近)
- 重みを変えると並び順が動く (vec=0.7 でベクトル寄り、vec=0.3 でキーワード寄り)
- メタデータフィルタ (outdoor/fashion): 5 件すべて outdoor または fashion
- 確認のキモ: **同じテーブルに ALTER TABLE で FTS index を後付けし、自作 retriever で `fts_match_word` を呼べる**こと

---

# よくある失敗と切り分け

### ① TiDB Cloud Zero の払い出しで 429 / 503
- 同 IP から短時間に大量のリクエスト → 60 秒待って再実行
- 複数ノートブックを並列実行していないか確認

### ② `OperationalError (1045, Access denied)`
- `conn` が古い (別セッションで取ったもの) → provision セルを再実行

### ③ `テーブルが既に存在します` / PK 重複
- 生成時点で `if_exists="overwrite"` にしてあるので通常は発生しない
- **手動で bulk_insert セルだけ複数回回した** 場合のみ発生 → provision からやり直し

### ④ ベクトル検索で 0 件
- `table.rows()` で 0 なら insert が走っていない → 直前のセルを再実行
- embedding 生成がまだ完了していない可能性 (サーバサイド embedding は非同期) → 10 秒待って再度検索

### ⑤ `google.colab.ai` が使えない
- Colab 以外 (VS Code の Jupyter 等) で開いていないか確認
- Colab でも未ログインだと動かない
- レート制限: 分あたりの呼び出し回数制限あり → 間隔を空ける

### ⑥ 09 で sentence-transformers のインストール失敗
- `!pip install -q sentence-transformers` を単独セルで実行
- それでもダメなら `torch` 事前インストール: `!pip install -q torch --index-url https://download.pytorch.org/whl/cpu`

### ⑦ 10 で CLIP の DL が止まる
- HuggingFace のネットワーク不調 → 数分待って再実行
- Colab のディスク残容量 (無料枠 80GB) を確認

### ⑧ 10 の画像が表示されない
- matplotlib が inline バックエンドか確認 (`%matplotlib inline` を先頭セルに追加)
- ランタイム再起動で直ることが多い

### ⑨ LlamaIndex 版で `Connections using insecure transport are prohibited`
- 接続文字列に `?ssl_verify_cert=true&ssl_verify_identity=true` が付いているか確認
- 各ノートブックの `make_conn_str()` ヘルパが SSL 句を付ける実装

### ⑩ LlamaIndex 版で FTS index 待機が timeout する (`継続するが検索が空になる可能性あり`)
- TiDB Cloud Zero 側の columnar replica が遅れているだけ。timeout 後でも 1〜2 分待ってから再実行すれば取れることが多い
- それでも空なら `ALTER TABLE products SET TIFLASH REPLICA 1;` を別途実行 → `INFORMATION_SCHEMA.TIFLASH_REPLICA` でレプリカが完成するまで待つ

### ⑪ LlamaIndex のハイブリッド検索で同じ商品が 2 回出てくる
- `TiDBFullTextRetriever` の `TextNode(id_=str(r.id), ...)` 指定が抜けている可能性
- `id_` を vec_retriever 側 (TiDBVectorStore が割り当てた UUID) と一致させると `QueryFusionRetriever` が dedup する

### ⑫ LM Studio に繋がらない (`ConnectionError`)
- LM Studio で **OpenAI 互換サーバを Start** + `google/gemma-4-e2b` をロードしているか
- `curl http://localhost:1234/v1/models` で `id: google/gemma-4-e2b` が返るか確認
- ポート違い: 環境変数 `LMSTUDIO_BASE=http://localhost:NNNN/v1` で上書き

---

# 終わったら

- TiDB Cloud Zero のクラスタは 30 日で自動削除される
- 保持したい場合は各ノートブックの provision セル出力の `claim URL` を開く
- Colab 側で `ランタイム → すべてのランタイムを終了` で GPU/メモリ解放

検証の結果やエラーメッセージを貼り付けて共有すれば、修正が必要かこちらで判断します。
