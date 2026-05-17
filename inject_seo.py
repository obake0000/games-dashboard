"""
inject_seo.py — 9ゲームの index.html に SEO メタタグ + GA4 タグを一括注入する。

挿入方式:
  <!-- SEO_BLOCK_START -->
  ...タグ群...
  <!-- SEO_BLOCK_END -->
  既存ブロックがあれば置換、無ければ <meta viewport> の直後 (or <title> の直後) に挿入。

  既存の <title> は SEO_BLOCK 内のものに置き換える (重複させない)。

使い方:
  python inject_seo.py                 # 全ゲーム一括
  python inject_seo.py shift-tetris    # 個別実行
  python inject_seo.py --no-ga4        # GA4タグを抜く (ID未受領時)

GA4_ID を差し替えて再実行すれば全ゲームに反映。
"""
import re
import sys
import json
from pathlib import Path

# === ここを編集 ===
GA4_ID = "G-XXXXXXXXXX"  # ユーザーから受領したら差し替え

GAMES = [
    {
        "slug": "toilet-tower-defense",
        "url": "https://obake0000.github.io/toilet-tower-defense/",
        "local": [r"c:/gm/td-deploy/index.html"],
        "title": "トイレ防衛隊：清潔圏崩壊 — 無料ブラウザタワーディフェンス",
        "desc": "90秒で保健所査察が来る！清掃員になってトイレを汚染から守るブラウザタワーディフェンス。インストール不要・無料。",
        "keywords": "タワーディフェンス,防衛ゲーム,トイレ,清掃,ブラウザゲーム,無料,スマホ,短時間,カジュアル",
        "genre": "TowerDefense",
        "image": "https://obake0000.github.io/toilet-tower-defense/og.png",
    },
    {
        "slug": "nurse-survival-game",
        "url": "https://obake0000.github.io/nurse-survival-game/",
        "local": [r"c:/gm/裏道再現/コピーバージョン/index.html"],
        "title": "看護師もーむり退職ゲーム — 夜勤を生き延びろ",
        "desc": "もう無理。夜勤・人間関係・残業を耐え抜いて退職届を出す看護師サバイバルゲーム。実体験ベースのリアル系。",
        "keywords": "看護師,夜勤,サバイバル,退職,医療,シミュレーション,ブラウザゲーム,無料,リアル",
        "genre": "Simulation",
        "image": "https://obake0000.github.io/nurse-survival-game/og.png",
    },
    {
        "slug": "kabukicho-fighter",
        "url": "https://obake0000.github.io/kabukicho-fighter/",
        "local": [r"c:/gm/歌舞伎町ファイター/claude-MANI/index.html"],
        "title": "歌舞伎町ローソンファイト — 殴らずにコンビニを守れ",
        "desc": "深夜の歌舞伎町ローソン店員になって、撮影＆通報で迷惑客を退去させる「殴らないサバイバル」。無料ブラウザゲーム。",
        "keywords": "コンビニ,歌舞伎町,ローソン,アクション,深夜,店員,サバイバル,ブラウザゲーム,無料,カジュアル",
        "genre": "Action",
        "image": "https://obake0000.github.io/kabukicho-fighter/og.png",
    },
    {
        "slug": "sanpun-shinde-warau",
        "url": "https://obake0000.github.io/sanpun-shinde-warau/",
        "local": [r"c:/py/sanpun-deploy/index.html"],
        "title": "死ぬ前に3分だけ神になれる — 4分で全エンディング",
        "desc": "寿命3分。神の力で人生をやり直す。タップで進むブラックエンド確定ナラティブ短編ゲーム。約4分。",
        "keywords": "ナラティブ,短編,選択肢,人生,神,死,ブラックエンド,ブラウザゲーム,無料,4分",
        "genre": "Adventure",
        "image": "https://obake0000.github.io/sanpun-shinde-warau/og.png",
    },
    {
        "slug": "machiapu-rpg",
        "url": "https://obake0000.github.io/machiapu-rpg/game.html",
        "local": [
            r"c:/gm/マチアプRPG/index.html",
            r"c:/gm/マチアプRPG/game.html",
        ],
        "title": "マチアプRPG — マッチングアプリ運用RPG",
        "desc": "マチアプを攻略してマッチングを稼ぐ運用RPG。プロフ強化・メッセージ戦略でレベルアップ。ブラウザで無料プレイ。",
        "keywords": "マッチングアプリ,マチアプ,恋愛,RPG,シミュレーション,プロフィール,ブラウザゲーム,無料",
        "genre": "RPG",
        "image": "https://obake0000.github.io/machiapu-rpg/og.png",
    },
    {
        "slug": "shift-tetris",
        "url": "https://obake0000.github.io/shift-tetris/",
        "local": [r"c:/gm/シフト表テトリス/index.html"],
        "title": "シフト表テトリス — 深夜のコンビニ店長日記",
        "desc": "テトリスのようにシフトを埋めるコンビニ店長シミュレーター。穴埋め・希望休・労基規制を捌け。無料ブラウザパズル。",
        "keywords": "シフト,テトリス,コンビニ,店長,シミュレーション,パズル,労務,ブラウザゲーム,無料",
        "genre": "Puzzle",
        "image": "https://obake0000.github.io/shift-tetris/og.png",
    },
    {
        "slug": "gemini-at-the-stake",
        "url": "https://obake0000.github.io/gemini-at-the-stake/",
        "local": [r"c:/gm/トイレタワーディフェンス/簡易タワーディフェンス用1ST絞り/dist/index.html"],
        "title": "ジェミニ防衛戦 — 著作権圏は崩壊する",
        "desc": "AIに迫る著作権の波を撃退するタワーディフェンス。パロディ系ブラウザゲーム、インストール不要・無料。",
        "keywords": "タワーディフェンス,AI,著作権,Gemini,パロディ,ブラウザゲーム,無料,カジュアル",
        "genre": "TowerDefense",
        "image": "https://obake0000.github.io/gemini-at-the-stake/og.png",
    },
]

MARKER_START = "<!-- SEO_BLOCK_START -->"
MARKER_END = "<!-- SEO_BLOCK_END -->"


def build_seo_block(game: dict, use_ga4: bool) -> str:
    ld = {
        "@context": "https://schema.org",
        "@type": "VideoGame",
        "name": game["title"].split(" — ")[0],
        "description": game["desc"],
        "url": game["url"],
        "image": game["image"],
        "author": {"@type": "Person", "name": "obake0000"},
        "inLanguage": "ja",
        "genre": game["genre"],
        "applicationCategory": "GameApplication",
        "operatingSystem": "Web Browser",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "JPY",
            "availability": "https://schema.org/InStock",
        },
    }
    ld_json = json.dumps(ld, ensure_ascii=False, indent=2)

    ga4_block = ""
    if use_ga4 and GA4_ID and not GA4_ID.endswith("XXXXX"):
        ga4_block = f"""<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA4_ID}', {{
    'send_page_view': true,
    'game_slug': '{game["slug"]}'
  }});
</script>
"""

    return f"""{MARKER_START}
<title>{game["title"]}</title>
<meta name="description" content="{game["desc"]}">
<meta name="keywords" content="{game["keywords"]}">
<meta name="author" content="obake0000">
<link rel="canonical" href="{game["url"]}">

<!-- OGP -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="obake0000 games">
<meta property="og:locale" content="ja_JP">
<meta property="og:title" content="{game["title"]}">
<meta property="og:description" content="{game["desc"]}">
<meta property="og:url" content="{game["url"]}">
<meta property="og:image" content="{game["image"]}">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{game["title"]}">
<meta name="twitter:description" content="{game["desc"]}">
<meta name="twitter:image" content="{game["image"]}">

<!-- JSON-LD VideoGame -->
<script type="application/ld+json">
{ld_json}
</script>

{ga4_block}{MARKER_END}"""


def inject(html: str, block: str) -> str:
    # 既存ブロックを置換
    pat = re.compile(re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END), re.DOTALL)
    if pat.search(html):
        return pat.sub(block, html)

    # 既存 <title>...</title> を削除 (block 内に新しい title あり)
    html = re.sub(r"\s*<title>.*?</title>\s*", "\n", html, count=1, flags=re.DOTALL)

    # <meta viewport> の直後に挿入 (なければ <head> 直後)
    viewport_pat = re.compile(r'(<meta\s+name=["\']viewport["\'][^>]*>)', re.IGNORECASE)
    m = viewport_pat.search(html)
    if m:
        return html[: m.end()] + "\n" + block + html[m.end() :]
    head_pat = re.compile(r"(<head[^>]*>)", re.IGNORECASE)
    m = head_pat.search(html)
    if m:
        return html[: m.end()] + "\n" + block + html[m.end() :]
    raise RuntimeError("No <head> or <meta viewport> found")


def process_game(game: dict, use_ga4: bool) -> list[str]:
    results = []
    block = build_seo_block(game, use_ga4)
    for path_str in game["local"]:
        p = Path(path_str)
        if not p.exists():
            results.append(f"  SKIP  {path_str} (not found)")
            continue
        original = p.read_text(encoding="utf-8")
        new = inject(original, block)
        if new == original:
            results.append(f"  NOOP  {path_str}")
        else:
            p.write_text(new, encoding="utf-8")
            results.append(f"  OK    {path_str}")
    return results


def main():
    use_ga4 = "--no-ga4" not in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    target_slugs = set(args) if args else None

    print(f"GA4_ID: {GA4_ID}  (use_ga4={use_ga4})")
    print()

    for game in GAMES:
        if target_slugs and game["slug"] not in target_slugs:
            continue
        print(f"[{game['slug']}]")
        for r in process_game(game, use_ga4):
            print(r)
        print()


if __name__ == "__main__":
    main()
