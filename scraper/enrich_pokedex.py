"""
ぽこあポケモン 詳細ページ補完スクレイパー
- pokedex.json の detail_url を使って各ポケモン詳細ページを取得
- 得意なこと / 好きな環境 / 好きなもの を抽出して pokedex_full.json に保存
"""

import json
import time
import re
import sys
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("pip install requests beautifulsoup4")
    sys.exit(1)

BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "pokedex.json"
OUTPUT_FILE = BASE_DIR / "pokedex_full.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
DELAY = 1.5  # 秒（サーバー負荷軽減）


def fetch_detail(url: str) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"  取得失敗: {url} → {e}", file=sys.stderr)
        return None


def extract_list_items_after_heading(soup: BeautifulSoup, heading_text: str) -> list[str]:
    """見出しの直後のulリストを取得する"""
    for tag in soup.find_all(["h2", "h3", "h4", "strong", "b"]):
        if heading_text in tag.get_text():
            ul = tag.find_next("ul")
            if ul:
                return [li.get_text(strip=True) for li in ul.find_all("li")]
            # ulがなければ次のテキストノードを探す
            sibling = tag.find_next_sibling()
            if sibling:
                text = sibling.get_text(separator="、", strip=True)
                return [s.strip() for s in re.split(r"[、,\n]", text) if s.strip()]
    return []


def extract_text_after_label(soup: BeautifulSoup, label: str) -> list[str]:
    """「ラベル：値」形式のテキストを抽出する"""
    text = soup.get_text(separator="\n")
    pattern = re.compile(rf"{re.escape(label)}[：:]\s*(.+)")
    match = pattern.search(text)
    if match:
        value = match.group(1).strip()
        return [s.strip() for s in re.split(r"[、,/・\s]+", value) if s.strip()]
    return []


def parse_detail_page(soup: BeautifulSoup) -> dict:
    result = {
        "skills": [],
        "environment": [],
        "favorites": [],
        "time": [],
        "weather": [],
    }

    # 得意なこと（複数スキルの可能性あり）
    skills = extract_list_items_after_heading(soup, "得意なこと")
    if not skills:
        skills = extract_text_after_label(soup, "得意なこと")
    # 「得意なこと：さいばい」のような形式もある
    if not skills:
        text = soup.get_text(separator="\n")
        m = re.search(r"得意なこと[：:]\s*([^\n]+)", text)
        if m:
            skills = [s.strip() for s in re.split(r"[、,/・]+", m.group(1)) if s.strip()]
    result["skills"] = skills

    # 好きな環境
    result["environment"] = extract_list_items_after_heading(soup, "好きな環境")

    # 好きなもの
    result["favorites"] = extract_list_items_after_heading(soup, "好きなもの")

    # 時間・天気：アイコン画像のaltを探す
    for img in soup.find_all("img"):
        alt = img.get("alt", "")
        if alt in ("朝", "昼", "夕", "夜"):
            result["time"].append(alt)
        elif alt in ("晴れ", "曇り", "雨", "雪"):
            result["weather"].append(alt)

    result["time"] = list(dict.fromkeys(result["time"]))
    result["weather"] = list(dict.fromkeys(result["weather"]))

    return result


def main():
    if not INPUT_FILE.exists():
        print(f"入力ファイルが見つかりません: {INPUT_FILE}")
        sys.exit(1)

    with open(INPUT_FILE, encoding="utf-8") as f:
        pokemon_list: list[dict] = json.load(f)

    # 既存の出力があればそこから再開（中断対応）
    existing: dict[int, dict] = {}
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            for p in json.load(f):
                existing[p["no"]] = p
        print(f"既存データ読み込み: {len(existing)}件（再開モード）")

    results = []
    total = len(pokemon_list)

    for i, pokemon in enumerate(pokemon_list):
        no = pokemon["no"]
        name = pokemon["name"]
        url = pokemon.get("detail_url", "")

        # 既にデータがある場合はスキップ
        if no in existing and any(existing[no].get(k) for k in ("skills", "environment", "favorites")):
            results.append(existing[no])
            print(f"[{i+1}/{total}] No.{no:03d} {name} → スキップ（既存）")
            continue

        merged = dict(pokemon)

        if not url:
            print(f"[{i+1}/{total}] No.{no:03d} {name} → URLなし（スキップ）")
            results.append(merged)
            continue

        print(f"[{i+1}/{total}] No.{no:03d} {name} → 取得中...", end=" ", flush=True)
        soup = fetch_detail(url)

        if soup:
            detail = parse_detail_page(soup)
            merged.update(detail)
            status = f"スキル:{detail['skills']} 環境:{detail['environment']} 好み:{len(detail['favorites'])}件"
            print(status)
        else:
            print("失敗")

        results.append(merged)

        # 10件ごとに中間保存
        if (i + 1) % 10 == 0:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"  → 中間保存: {len(results)}件")

        time.sleep(DELAY)

    # 最終保存
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    filled = sum(1 for p in results if p.get("skills") or p.get("favorites"))
    print(f"\n完了: {len(results)}件保存 / うちデータあり {filled}件")
    print(f"出力: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
