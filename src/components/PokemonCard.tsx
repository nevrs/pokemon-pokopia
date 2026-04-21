import type { Pokemon } from "../types";

const TIME_COLOR: Record<string, string> = {
  朝: "bg-orange-100 text-orange-700",
  昼: "bg-yellow-100 text-yellow-700",
  夕: "bg-red-100 text-red-700",
  夜: "bg-indigo-100 text-indigo-700",
};

const WEATHER_COLOR: Record<string, string> = {
  晴れ: "bg-amber-100 text-amber-700",
  曇り: "bg-gray-100 text-gray-600",
  雨: "bg-blue-100 text-blue-700",
  雪: "bg-sky-100 text-sky-700",
};

const SKILL_COLOR: Record<string, string> = {
  さいばい: "bg-green-100 text-green-700",
  もやす: "bg-red-100 text-red-700",
  うるおす: "bg-blue-100 text-blue-700",
  そらをとぶ: "bg-sky-100 text-sky-700",
  ちらかす: "bg-yellow-100 text-yellow-700",
  とりひき: "bg-purple-100 text-purple-700",
};

function Badge({ label, colorClass }: { label: string; colorClass: string }) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
      {label}
    </span>
  );
}

export function PokemonCard({ pokemon }: { pokemon: Pokemon }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex flex-col gap-2 hover:shadow-md transition-shadow">
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-400 font-mono">No.{String(pokemon.no).padStart(3, "0")}</span>
        <span className="font-bold text-gray-800 text-base">{pokemon.name}</span>
      </div>

      <div className="flex flex-wrap gap-1">
        {pokemon.time.map((t) => (
          <Badge key={t} label={t} colorClass={TIME_COLOR[t] ?? "bg-gray-100 text-gray-600"} />
        ))}
        {pokemon.weather.map((w) => (
          <Badge key={w} label={w} colorClass={WEATHER_COLOR[w] ?? "bg-gray-100 text-gray-600"} />
        ))}
      </div>

      {pokemon.skills.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {pokemon.skills.map((s) => (
            <Badge key={s} label={`⚡ ${s}`} colorClass={SKILL_COLOR[s] ?? "bg-emerald-100 text-emerald-700"} />
          ))}
        </div>
      )}

      {pokemon.environment.length > 0 && (
        <div className="text-xs text-gray-500">
          <span className="font-medium text-pink-600">♥環境</span>{" "}
          {pokemon.environment.join(" / ")}
        </div>
      )}

      {pokemon.favorites.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {pokemon.favorites.map((f) => (
            <span key={f} className="text-xs bg-pink-50 text-pink-600 px-2 py-0.5 rounded-full">
              {f}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
