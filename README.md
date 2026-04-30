# tidb-colab-tutorials

TiDB を Google Colab で体験するチュートリアル集です。
**フレームワーク別**にディレクトリを分けて配置しています。

- [`tutorials/pytidb/`](tutorials/pytidb/) — pytidb (TiDB 公式の Python SDK) で学ぶ 11 本のシリーズ
- [`tutorials/llamaindex/`](tutorials/llamaindex/) — LlamaIndex から TiDB を使う RAG / ハイブリッド検索の 2 本

## 共通前提

- **Google Colab で動作** します (LLM を使うノートブックは `google.colab.ai` を利用)
- **TiDB Cloud Zero**: サインアップ不要、API 経由で 30 日有効のクラスタを払い出し。claim URL から TiDB Cloud Starter に移行すれば保持できます

---

## pytidb 版 (基礎〜応用 11 本)

API キー不要 (TiDB Cloud Zero + 組み込み埋め込み Titan + Colab AI で完結)。
原則 `!pip install -q pytidb` だけで動きます (09/10 のみ埋め込みモデルの追加インストール)。

| # | ノートブック | トピック | Open |
|---|---|---|---|
| 00 | [`tutorials/pytidb/00_quickstart.ipynb`](tutorials/pytidb/00_quickstart.ipynb) | pytidb の全体像 (TODO タスクで CRUD) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/pytidb/00_quickstart.ipynb) |
| 01 | [`tutorials/pytidb/01_schema_and_types.ipynb`](tutorials/pytidb/01_schema_and_types.ipynb) | TEXT / JSON / VECTOR 型 (書籍ライブラリ) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/pytidb/01_schema_and_types.ipynb) |
| 02 | [`tutorials/pytidb/02_query_and_filter.ipynb`](tutorials/pytidb/02_query_and_filter.ipynb) | クエリ・フィルタ・トランザクション (在庫管理) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/pytidb/02_query_and_filter.ipynb) |
| 03 | [`tutorials/pytidb/03_vector_search.ipynb`](tutorials/pytidb/03_vector_search.ipynb) | ベクトル検索 / auto-embedding (ニュース見出し) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/pytidb/03_vector_search.ipynb) |
| 04 | [`tutorials/pytidb/04_fulltext_search.ipynb`](tutorials/pytidb/04_fulltext_search.ipynb) | 全文検索・日本語トークナイズ (ブログ記事) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/pytidb/04_fulltext_search.ipynb) |
| 05 | [`tutorials/pytidb/05_hybrid_search.ipynb`](tutorials/pytidb/05_hybrid_search.ipynb) | ハイブリッド検索 (EC 商品カタログ) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/pytidb/05_hybrid_search.ipynb) |
| 06 | [`tutorials/pytidb/06_rag.ipynb`](tutorials/pytidb/06_rag.ipynb) | シンプルな RAG (レシピ) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/pytidb/06_rag.ipynb) |
| 07 | [`tutorials/pytidb/07_memory.ipynb`](tutorials/pytidb/07_memory.ipynb) | AI エージェントの永続メモリ (発言ログ) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/pytidb/07_memory.ipynb) |
| 08 | [`tutorials/pytidb/08_text2sql.ipynb`](tutorials/pytidb/08_text2sql.ipynb) | Text2SQL (売上トランザクション) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/pytidb/08_text2sql.ipynb) |
| 09 | [`tutorials/pytidb/09_custom_embedding.ipynb`](tutorials/pytidb/09_custom_embedding.ipynb) | 独自 Embedding 関数 (FAQ × sentence-transformers) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/pytidb/09_custom_embedding.ipynb) |
| 10 | [`tutorials/pytidb/10_image_search.ipynb`](tutorials/pytidb/10_image_search.ipynb) | 画像検索 (CLIP ViT-B/32) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/pytidb/10_image_search.ipynb) |

### おすすめの順番

1. **基礎編** (00 → 01 → 02): pytidb の基本 API と TiDB のデータ型を一通り触る
2. **検索編** (03 → 04 → 05): ベクトル・全文・ハイブリッドの 3 種の検索を比較
3. **応用編** (06 → 07 → 08): RAG・メモリ・Text2SQL に応用する
4. **拡張** (09 → 10): 独自埋め込みでモデルを差し替える / CLIP で画像検索

---

## LlamaIndex 版 (RAG + ハイブリッド検索 2 本)

LlamaIndex の `TiDBVectorStore` を使って RAG とハイブリッド検索を組み立てるシリーズ。
TiDB の使い方そのものは pytidb 版で先にやっている前提です (基礎部分は省略)。

LLM は **環境を自動判定**して以下のどちらかを使います:
- Colab 上では `google.colab.ai.generate_text` を `llama_index.core.llms.CustomLLM` でラップ
- ローカルでは LM Studio (OpenAI 互換 API、例: `google/gemma-4-e2b`)

Embedding は `intfloat/multilingual-e5-small` (HuggingFace、約 120MB、API キー不要) を LlamaIndex の `HuggingFaceEmbedding` で使います。

| # | ノートブック | トピック | Open |
|---|---|---|---|
| 00 | [`tutorials/llamaindex/00_rag.ipynb`](tutorials/llamaindex/00_rag.ipynb) | LlamaIndex で RAG (レシピ) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/llamaindex/00_rag.ipynb) |
| 01 | [`tutorials/llamaindex/01_hybrid_search.ipynb`](tutorials/llamaindex/01_hybrid_search.ipynb) | ハイブリッド検索 (`QueryFusionRetriever` + 自作 FTS Retriever) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/llamaindex/01_hybrid_search.ipynb) |

---

## 開発メモ

- `tutorials/` 配下の `.ipynb` を直接編集してメンテナンスします。Colab で開くか、JupyterLab / VS Code でセルを編集してください。
- 検証手順は [`tests/VERIFICATION.md`](tests/VERIFICATION.md) にまとめています。
- 参考資料: [`ref/pytidb`](ref/pytidb) に pytidb 本体のサブモジュールが含まれています (gitignore 対象)。
