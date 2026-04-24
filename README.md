# tidb-colab-tutorials

TiDB + pytidb を Google Colab で体験するチュートリアル集です。
トピックごとに短いノートブックを用意しています。

## 共通前提

- **Google Colab で動作** します (一部ノートブックは `google.colab.ai` を利用)
- **API キー不要**: TiDB Cloud Zero + 組み込み埋め込み (Titan) + Colab AI で完結
- **依存**: 原則 `!pip install -q pytidb` だけ (09 のみ `sentence-transformers` を追加)
- **使い捨てクラスタ**: TiDB Cloud Zero はサインアップ不要・30 日で自動削除。claim URL から TiDB Cloud Starter に移行すれば保持できます

## チュートリアル一覧

| # | ノートブック | トピック | Open |
|---|---|---|---|
| 00 | [`tutorials/00_quickstart.ipynb`](tutorials/00_quickstart.ipynb) | pytidb の全体像 (TODO タスクで CRUD) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/00_quickstart.ipynb) |
| 01 | [`tutorials/01_schema_and_types.ipynb`](tutorials/01_schema_and_types.ipynb) | TEXT / JSON / VECTOR 型 (書籍ライブラリ) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/01_schema_and_types.ipynb) |
| 02 | [`tutorials/02_query_and_filter.ipynb`](tutorials/02_query_and_filter.ipynb) | クエリ・フィルタ・トランザクション (在庫管理) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/02_query_and_filter.ipynb) |
| 03 | [`tutorials/03_vector_search.ipynb`](tutorials/03_vector_search.ipynb) | ベクトル検索 / auto-embedding (ニュース見出し) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/03_vector_search.ipynb) |
| 04 | [`tutorials/04_fulltext_search.ipynb`](tutorials/04_fulltext_search.ipynb) | 全文検索・日本語トークナイズ (ブログ記事) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/04_fulltext_search.ipynb) |
| 05 | [`tutorials/05_hybrid_search.ipynb`](tutorials/05_hybrid_search.ipynb) | ハイブリッド検索 (EC 商品カタログ) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/05_hybrid_search.ipynb) |
| 06 | [`tutorials/06_rag.ipynb`](tutorials/06_rag.ipynb) | シンプルな RAG (レシピ) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/06_rag.ipynb) |
| 07 | [`tutorials/07_memory.ipynb`](tutorials/07_memory.ipynb) | AI エージェントの永続メモリ (発言ログ) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/07_memory.ipynb) |
| 08 | [`tutorials/08_text2sql.ipynb`](tutorials/08_text2sql.ipynb) | Text2SQL (売上トランザクション) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/08_text2sql.ipynb) |
| 09 | [`tutorials/09_custom_embedding.ipynb`](tutorials/09_custom_embedding.ipynb) | 独自 Embedding 関数 (FAQ × sentence-transformers) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/09_custom_embedding.ipynb) |
| 10 | [`tutorials/10_image_search.ipynb`](tutorials/10_image_search.ipynb) | 画像検索 (CLIP ViT-B/32) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tadapin/tidb-colab-tutorials/blob/main/tutorials/10_image_search.ipynb) |

## おすすめの順番

1. **基礎編** (00 → 01 → 02): pytidb の基本 API と TiDB のデータ型を一通り触る
2. **検索編** (03 → 04 → 05): ベクトル・全文・ハイブリッドの 3 種の検索を比較
3. **応用編** (06 → 07 → 08): RAG・メモリ・Text2SQL に応用する
4. **拡張** (09 → 10): 独自埋め込みでモデルを差し替える / CLIP で画像検索

## 開発メモ

- ノートブックの実体は `scripts/gen_notebooks.py` から生成しています。共通のプロビジョニング/ヘッダを含め、章ごとのソースはすべてこのスクリプト内にあります。
  ```
  python3 scripts/gen_notebooks.py
  ```
  これで `tutorials/` 配下の `.ipynb` がすべて再生成されます (`06_rag.ipynb` は手書きなので対象外)。
- 参考資料: [`ref/pytidb`](ref/pytidb) に pytidb 本体のサブモジュールが含まれています。
