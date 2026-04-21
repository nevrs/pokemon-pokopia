"""
ぽこあポケモン ポケモン図鑑スクレイパー
対象: https://appmedia.jp/pocoapokemon/79811216
出力: pokedex.json / pokedex.csv
"""

import json
import csv
import time
import re
import sys
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("依存ライブラリが不足しています。以下を実行してください:")
    print("  pip install requests beautifulsoup4")
    sys.exit(1)

URL = "https://appmedia.jp/pocoapokemon/79811216"
OUTPUT_DIR = Path(__file__).parent
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_page(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return BeautifulSoup(resp.text, "html.parser")


def extract_pokemon(soup: BeautifulSoup) -> list[dict]:
    """
    AppMediaの図鑑ページからポケモンデータを抽出する。
    テーブル行 or カードブロックを走査して構造化する。
    """
    results = []

    # テーブル形式を試みる
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if not cells:
                continue
            text_cells = [c.get_text(separator=" ", strip=True) for c in cells]
            # No.xxxで始まる行がデータ行
            if not re.match(r"No\.\d+", text_cells[0]):
                continue
            entry = parse_row_cells(cells, text_cells)
            if entry:
                results.append(entry)

    if results:
        return results

    # テーブルがなければカード形式を試みる
    # class名は実際のHTMLに合わせて調整が必要
    cards = soup.select("[class*='pokemon'], [class*='monster'], [class*='entry']")
    for card in cards:
        entry = parse_card(card)
        if entry:
            results.append(entry)

    return results


def parse_row_cells(cells, text_cells: list[str]) -> dict | None:
    """テーブル行のセルをパースする"""
    try:
        no_match = re.search(r"(\d+)", text_cells[0])
        if not no_match:
            return None
        number = int(no_match.group(1))

        # アンカーからポケモン名を取得
        name_cell = cells[1] if len(cells) > 1 else cells[0]
        name_link = name_cell.find("a")
        name = name_link.get_text(strip=True) if name_link else name_cell.get_text(strip=True)
        detail_url = name_link["href"] if name_link and name_link.get("href") else ""

        # アイコン画像URL
        img = cells[0].find("img") or (cells[1].find("img") if len(cells) > 1 else None)
        icon_url = img["src"] if img else ""

        # 残りセルを順番に解析（時間、天気、得意、環境、好きなもの）
        time_slots = extract_icons_or_text(cells, text_cells, index=2)
        weather = extract_icons_or_text(cells, text_cells, index=3)
        skills = extract_icons_or_text(cells, text_cells, index=4)
        environment = extract_icons_or_text(cells, text_cells, index=5)
        favorites = extract_icons_or_text(cells, text_cells, index=6)

        return {
            "no": number,
            "name": name,
            "detail_url": detail_url,
            "icon_url": icon_url,
            "time": time_slots,
            "weather": weather,
            "skills": skills,
            "environment": environment,
            "favorites": favorites,
        }
    except Exception as e:
        print(f"  警告: 行のパースに失敗: {e}", file=sys.stderr)
        return None


def extract_icons_or_text(cells, text_cells: list[str], index: int) -> list[str]:
    """セルからalt属性またはテキストのリストを取得する"""
    if index >= len(cells):
        return []
    cell = cells[index]
    imgs = cell.find_all("img")
    if imgs:
        return [img.get("alt", "").strip() for img in imgs if img.get("alt")]
    raw = text_cells[index] if index < len(text_cells) else ""
    return [s.strip() for s in re.split(r"[、,/・\s]+", raw) if s.strip()]


def parse_card(card) -> dict | None:
    """カード形式のブロックをパースする（フォールバック用）"""
    text = card.get_text(separator="\n", strip=True)
    no_match = re.search(r"No\.(\d+)", text)
    if not no_match:
        return None

    number = int(no_match.group(1))
    name_tag = card.find(["h2", "h3", "h4", "a"])
    name = name_tag.get_text(strip=True) if name_tag else ""
    name = re.sub(r"No\.\d+", "", name).strip()

    img = card.find("img")
    icon_url = img["src"] if img else ""

    def find_after_label(label: str) -> list[str]:
        pattern = re.compile(label)
        match = pattern.search(text)
        if not match:
            return []
        after = text[match.end():]
        line = after.split("\n")[0]
        return [s.strip() for s in re.split(r"[、,/・]+", line) if s.strip()]

    return {
        "no": number,
        "name": name,
        "icon_url": icon_url,
        "detail_url": "",
        "time": find_after_label(r"時間[：:]\s*"),
        "weather": find_after_label(r"天気[：:]\s*"),
        "skills": find_after_label(r"得意[：:]\s*"),
        "environment": find_after_label(r"♥環境[：:]\s*"),
        "favorites": find_after_label(r"♥好きなもの[：:]\s*"),
    }


def save_json(data: list[dict], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"JSON保存: {path} ({len(data)}件)")


def save_csv(data: list[dict], path: Path) -> None:
    if not data:
        return
    fields = ["no", "name", "detail_url", "icon_url", "time", "weather", "skills", "environment", "favorites"]
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in data:
            flat = {k: "、".join(v) if isinstance(v, list) else v for k, v in row.items()}
            writer.writerow(flat)
    print(f"CSV保存: {path} ({len(data)}件)")


def main():
    print(f"取得中: {URL}")
    soup = fetch_page(URL)
    time.sleep(1)  # 礼儀的なウェイト

    pokemon_list = extract_pokemon(soup)

    if not pokemon_list:
        print("データが取得できませんでした。HTMLを手動で確認してください。")
        # デバッグ用: HTMLを保存
        debug_path = OUTPUT_DIR / "debug_page.html"
        debug_path.write_text(soup.prettify(), encoding="utf-8")
        print(f"デバッグ用HTML保存: {debug_path}")
        sys.exit(1)

    pokemon_list.sort(key=lambda p: p["no"])
    print(f"取得完了: {len(pokemon_list)}件")

    save_json(pokemon_list, OUTPUT_DIR / "pokedex.json")
    save_csv(pokemon_list, OUTPUT_DIR / "pokedex.csv")


if __name__ == "__main__":
    main()
