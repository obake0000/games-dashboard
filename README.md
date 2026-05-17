# obake0000 games — アクセス解析ダッシュボード

9ゲームのアクセス解析（GA4）と SEO 対策を一元管理するハブ。

## 構成

| ファイル | 役割 |
|---|---|
| [index.html](index.html) | ダッシュボード本体（ブラウザで開く） |
| [keywords.md](keywords.md) | 9ゲームのキーワード戦略マトリクス |
| [inject_seo.py](inject_seo.py) | 各ゲームの index.html に SEO+GA4 タグを一括注入 |
| [generate_sitemaps.py](generate_sitemaps.py) | 各リポジトリに sitemap.xml + robots.txt を生成 |

## 9ゲーム

### GitHub Pages（ローカル特定済み・7ゲーム）

| ゲーム | URL | ローカルパス |
|---|---|---|
| トイレ防衛隊 | obake0000.github.io/toilet-tower-defense/ | `c:/gm/td-deploy/` |
| 看護師もーむり | obake0000.github.io/nurse-survival-game/ | `c:/gm/裏道再現/コピーバージョン/` |
| 歌舞伎町ローソン | obake0000.github.io/kabukicho-fighter/ | `c:/gm/歌舞伎町ファイター/claude-MANI/` |
| 3分の人生 | obake0000.github.io/sanpun-shinde-warau/ | `c:/py/sanpun-deploy/` |
| マチアプRPG | obake0000.github.io/machiapu-rpg/ | `c:/gm/マチアプRPG/` |
| シフト表テトリス | obake0000.github.io/shift-tetris/ | `c:/gm/シフト表テトリス/` |
| ジェミニ防衛戦 | obake0000.github.io/gemini-at-the-stake/ | `c:/gm/トイレタワーディフェンス/簡易タワーディフェンス用1ST絞り/dist/` |

### Vercel（要・ローカルパス確認・2ゲーム）

| ゲーム | URL | ローカルパス |
|---|---|---|
| ハニーファイト | honey-fight-codex.vercel.app | **未確認** |
| せどりサバイバー | sedori-survivors.vercel.app | **未確認** |

---

## 運用フロー

### 1. GA4 セットアップ（ユーザー初回作業）

1. https://analytics.google.com/ にログイン → 管理 → プロパティを作成
   - プロパティ名: `obake0000 games`
   - タイムゾーン: 日本、通貨: 円
2. データストリームを「Web」で1個作成（URL は代表ゲームでOK、後で他ゲームも同じIDで送る）
3. Measurement ID `G-XXXXXXXXXX` を控える
4. Claude に「GA4 ID は G-XXXXXXXXXX」と伝える

### 2. GA4 タグ注入（Claude作業）

```bash
# inject_seo.py の GA4_ID = "G-XXXXXXXXXX" を差し替え
python inject_seo.py        # 全ゲーム一括（GA4込み）
python inject_seo.py shift-tetris  # 個別
```

### 3. sitemap 再生成（必要時のみ）

```bash
python generate_sitemaps.py
```

### 4. 各リポジトリで commit + push

GitHub Pages は git push で即反映。Claude が一気にやる予定（ユーザー承認後）。

### 5. Looker Studio ダッシュボード

1. https://lookerstudio.google.com/ → 新規レポート
2. データソース「Google Analytics」→ 上記GA4プロパティを選択
3. 推奨ページ構成:
   - **概要**: 期間別PV/UU、デバイス、国
   - **ゲーム別**: Dimension「page_path」「page_location.hostname」で各ゲーム比較
   - **流入元**: Dimension「session_source」「session_medium」
4. 「共有」→「埋め込み」→「埋め込みURL有効化」→ iframe URL コピー
5. `index.html` の Looker iframe コメントを解除して src 差し替え

---

## SEO 注入の仕組み

`inject_seo.py` は各 index.html の `<head>` 内に以下を挿入する：

```html
<!-- SEO_BLOCK_START -->
<title>...</title>
<meta name="description" content="...">
<meta name="keywords" content="...">
<meta name="author" content="obake0000">
<link rel="canonical" href="...">

<!-- OGP -->
<meta property="og:type" content="website">
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:url" content="...">
<meta property="og:image" content="...">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
...

<!-- JSON-LD VideoGame -->
<script type="application/ld+json">{...}</script>

<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-..."></script>
<script>...</script>
<!-- SEO_BLOCK_END -->
```

マーカーで囲んでいるので**再実行で安全に上書き**される。
元の `<title>` は最初の1回だけ削除される（重複防止）。

---

## OGP 画像（後で）

各ゲームの `og.png` (1200×630) を以下に配置：
- `<repo_root>/og.png`

暫定はゲーム内スクショ、後で各ゲームのキービジュアルを作成して差し替え。

---

## キーワード戦略の要点

- **検索意図3層**: ジャンル語 + テーマ語 + 修飾語
- **タイトルは「テーマ語 — 修飾フレーズ」の二段構え**
- **description は140字以内、最初の80字に重要語**
- **JSON-LD VideoGame** で Google が「ゲーム」と認識

詳細は [keywords.md](keywords.md)。
