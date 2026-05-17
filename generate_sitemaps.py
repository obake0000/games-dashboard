"""
generate_sitemaps.py — 各ゲームのリポジトリルートに sitemap.xml と robots.txt を生成する。

GitHub Pages の Project Pages 形式 (obake0000.github.io/<repo>/) では各リポジトリに
sitemap を置くのが正しい配置 (ユーザーページとは別)。

使い方:
  python generate_sitemaps.py
"""
from datetime import date
from pathlib import Path

TODAY = date.today().isoformat()

# 各リポジトリのルートと、そこからクロールさせたいURLリスト
SITES = [
    {
        "repo_root": r"c:/gm/td-deploy",
        "base_url": "https://obake0000.github.io/toilet-tower-defense/",
        "urls": [""],
    },
    {
        "repo_root": r"c:/gm/裏道再現/コピーバージョン",
        "base_url": "https://obake0000.github.io/nurse-survival-game/",
        "urls": [""],
    },
    {
        "repo_root": r"c:/gm/歌舞伎町ファイター/claude-MANI",
        "base_url": "https://obake0000.github.io/kabukicho-fighter/",
        "urls": [""],
    },
    {
        "repo_root": r"c:/py/sanpun-deploy",
        "base_url": "https://obake0000.github.io/sanpun-shinde-warau/",
        "urls": [""],
    },
    {
        "repo_root": r"c:/gm/マチアプRPG",
        "base_url": "https://obake0000.github.io/machiapu-rpg/",
        "urls": ["", "game.html"],
    },
    {
        "repo_root": r"c:/gm/シフト表テトリス",
        "base_url": "https://obake0000.github.io/shift-tetris/",
        "urls": [""],
    },
    {
        "repo_root": r"c:/gm/トイレタワーディフェンス/簡易タワーディフェンス用1ST絞り/dist",
        "base_url": "https://obake0000.github.io/gemini-at-the-stake/",
        "urls": [""],
    },
]


def build_sitemap(base_url: str, urls: list[str]) -> str:
    items = []
    for u in urls:
        loc = base_url + u
        items.append(
            f"  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{TODAY}</lastmod>\n"
            f"    <changefreq>weekly</changefreq>\n"
            f"    <priority>1.0</priority>\n"
            f"  </url>"
        )
    body = "\n".join(items)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>\n"
    )


def build_robots(base_url: str) -> str:
    return (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {base_url}sitemap.xml\n"
    )


def main():
    for site in SITES:
        root = Path(site["repo_root"])
        if not root.exists():
            print(f"SKIP  {root} (not found)")
            continue
        sitemap_path = root / "sitemap.xml"
        robots_path = root / "robots.txt"
        sitemap_path.write_text(
            build_sitemap(site["base_url"], site["urls"]),
            encoding="utf-8",
        )
        robots_path.write_text(
            build_robots(site["base_url"]),
            encoding="utf-8",
        )
        print(f"OK    {root}/sitemap.xml + robots.txt")


if __name__ == "__main__":
    main()
