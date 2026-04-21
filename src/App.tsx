import { useEffect, useMemo, useState } from "react";
import pokedexRaw from "./data/pokedex.json";
import type { Pokemon } from "./types";
import { PokemonCard } from "./components/PokemonCard";
import "./index.css";

const pokedex = pokedexRaw as Pokemon[];

const ALL_TIMES = ["朝", "昼", "夕", "夜"] as const;
const ALL_WEATHERS = ["晴れ", "曇り", "雨", "雪"] as const;

const ALL_SKILLS = [
  "もやす", "さいばい", "うるおす", "きをきる", "けんちく", "じならし",
  "さがしもの", "そらをとぶ", "テレポート", "リサイクル", "しわける", "はつでん",
  "つぶす", "ちらかす", "とりひき", "もりあげる", "あくび", "ゆめしま",
  "ミツあつめ", "しゅうのう", "ばくはつ", "コレクター", "レアもの", "かんてい",
  "はっこう", "ペイント", "くいしんぼ", "パーティー", "DJ", "しょくにん", "へんしん",
];
const allEnvironments = [...new Set(pokedex.flatMap((p) => p.environment))].sort();

function FilterChip({
  label,
  active,
  onClick,
  color,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
  color?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1 rounded-full text-sm border transition-colors ${
        active
          ? `${color ?? "bg-green-600 border-green-600"} text-white`
          : "bg-white border-gray-300 text-gray-600 hover:border-gray-400"
      }`}
    >
      {label}
    </button>
  );
}

export default function App() {
  const [query, setQuery] = useState("");
  const [timeFilter, setTimeFilter] = useState<string[]>([]);
  const [weatherFilter, setWeatherFilter] = useState<string[]>([]);
  const [skillFilter, setSkillFilter] = useState<string[]>([]);
  const [envFilter, setEnvFilter] = useState<string[]>([]);

  function toggle(arr: string[], val: string): string[] {
    return arr.includes(val) ? arr.filter((x) => x !== val) : [...arr, val];
  }

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [timeFilter, weatherFilter, skillFilter, envFilter, query]);

  const filtered = useMemo(() => {
    return pokedex.filter((p) => {
      if (query) {
        const q = query.trim();
        const matchNo = String(p.no).padStart(3, "0").includes(q) || String(p.no).includes(q);
        const matchName = p.name.includes(q);
        if (!matchNo && !matchName) return false;
      }
      if (timeFilter.length > 0 && !p.time.some((t) => timeFilter.includes(t))) return false;
      if (weatherFilter.length > 0 && !p.weather.some((w) => weatherFilter.includes(w))) return false;
      if (skillFilter.length > 0 && !p.skills.some((s) => skillFilter.includes(s))) return false;
      if (envFilter.length > 0 && !p.environment.some((e) => envFilter.includes(e))) return false;
      return true;
    }).sort((a, b) => a.no - b.no);
  }, [query, timeFilter, weatherFilter, skillFilter, envFilter]);

  const hasFilter = query || timeFilter.length > 0 || weatherFilter.length > 0 || skillFilter.length > 0 || envFilter.length > 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-green-700 text-white px-4 py-3 shadow">
        <h1 className="text-xl font-bold tracking-wide">ぽこあポケモン 図鑑</h1>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-4 space-y-3">
        {/* 検索 */}
        <input
          type="text"
          placeholder="名前 or No. で検索..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
        />

        {/* フィルター */}
        <div className="space-y-2">
          <div className="flex flex-wrap gap-2 items-center">
            <span className="text-xs text-gray-500 w-10">時間</span>
            {ALL_TIMES.map((t) => (
              <FilterChip
                key={t}
                label={t}
                active={timeFilter.includes(t)}
                onClick={() => setTimeFilter((prev) => toggle(prev, t))}
                color={t === "朝" ? "bg-orange-500 border-orange-500" : t === "昼" ? "bg-yellow-500 border-yellow-500" : t === "夕" ? "bg-red-500 border-red-500" : "bg-indigo-600 border-indigo-600"}
              />
            ))}
          </div>
          <div className="flex flex-wrap gap-2 items-center">
            <span className="text-xs text-gray-500 w-10">天気</span>
            {ALL_WEATHERS.map((w) => (
              <FilterChip
                key={w}
                label={w}
                active={weatherFilter.includes(w)}
                onClick={() => setWeatherFilter((prev) => toggle(prev, w))}
                color="bg-blue-500 border-blue-500"
              />
            ))}
          </div>
          <div className="flex flex-wrap gap-2 items-center">
            <span className="text-xs text-gray-500 w-10">得意</span>
            {ALL_SKILLS.map((s) => (
              <FilterChip
                key={s}
                label={s}
                active={skillFilter.includes(s)}
                onClick={() => setSkillFilter((prev) => toggle(prev, s))}
                color="bg-emerald-600 border-emerald-600"
              />
            ))}
          </div>
          <div className="flex flex-wrap gap-2 items-center">
            <span className="text-xs text-gray-500 w-10">環境</span>
            {allEnvironments.map((e) => (
              <FilterChip
                key={e}
                label={e}
                active={envFilter.includes(e)}
                onClick={() => setEnvFilter((prev) => toggle(prev, e))}
                color="bg-pink-500 border-pink-500"
              />
            ))}
          </div>
        </div>

        {/* 件数 & リセット */}
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>{filtered.length} / {pokedex.length} 件</span>
          {hasFilter && (
            <button
              onClick={() => { setQuery(""); setTimeFilter([]); setWeatherFilter([]); setSkillFilter([]); setEnvFilter([]); }}
              className="text-red-500 hover:underline"
            >
              フィルターをリセット
            </button>
          )}
        </div>

        {/* グリッド */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {filtered.map((p) => (
            <PokemonCard key={`${p.no}-${p.name}`} pokemon={p} />
          ))}
        </div>

        {filtered.length === 0 && (
          <p className="text-center text-gray-400 py-16">該当するポケモンが見つかりませんでした</p>
        )}
      </div>
    </div>
  );
}
