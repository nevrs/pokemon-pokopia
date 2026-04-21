"""
db.txt → pokedex.json パーサー

構造:
  No.XXX名前
  ぽこあポケモン_名前_アイコン
  時間
  朝昼夕夜（連結 or 改行）
  天気
  晴れ曇り雨（連結 or 改行）
  得意
  スキル1,スキル2
  ♥環境
  環境名
  ♥好きなもの
  好み1
  好み2
  ...
  No.XXX次のポケモン
  ...
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "db.txt"
OUTPUT_FILE = BASE_DIR / "pokedex.json"

TIME_LABELS = {"朝", "昼", "夕", "夜"}
WEATHER_LABELS = {"晴れ", "曇り", "雨", "雪"}

def split_time_or_weather(text: str) -> list[str]:
    """「朝昼夕夜」のように連結されている場合に分割する"""
    result = []
    for label in ["朝", "昼", "夕", "夜", "晴れ", "曇り", "雨", "雪"]:
        if label in text:
            result.append(label)
    return result if result else [text]


def parse(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()

    pokemon_list = []
    current = None
    section = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # 新しいポケモンのエントリ
        m = re.match(r"No\.(\d+)(.+)", line)
        if m:
            if current:
                pokemon_list.append(current)
            current = {
                "no": int(m.group(1)),
                "name": m.group(2).strip(),
                "time": [],
                "weather": [],
                "skills": [],
                "environment": [],
                "favorites": [],
            }
            section = None
            continue

        if current is None:
            continue

        # アイコン行はスキップ
        if "_アイコン" in line:
            continue

        # セクション見出し
        if line == "時間":
            section = "time"
            continue
        if line == "天気":
            section = "weather"
            continue
        if line == "得意":
            section = "skills"
            continue
        if line == "♥環境":
            section = "environment"
            continue
        if line == "♥好きなもの":
            section = "favorites"
            continue

        # データ行
        if section == "time":
            current["time"] = split_time_or_weather(line)
        elif section == "weather":
            current["weather"] = split_time_or_weather(line)
        elif section == "skills":
            current["skills"] = [s.strip() for s in re.split(r"[,、]", line) if s.strip()]
        elif section == "environment":
            current["environment"].append(line)
        elif section == "favorites":
            current["favorites"].append(line)

    if current:
        pokemon_list.append(current)

    return pokemon_list


def main():
    data = parse(INPUT_FILE)
    print(f"パース完了: {len(data)}件")

    # サンプル表示
    for p in data[:3]:
        print(f"  No.{p['no']:03d} {p['name']} | 時間:{p['time']} | 天気:{p['weather']} | 得意:{p['skills']} | 環境:{p['environment']} | 好み:{p['favorites'][:2]}...")

    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"保存: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
