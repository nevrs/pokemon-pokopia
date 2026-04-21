export type TimeSlot = "朝" | "昼" | "夕" | "夜";
export type Weather = "晴れ" | "曇り" | "雨" | "雪";

export interface Pokemon {
  no: number;
  name: string;
  time: TimeSlot[];
  weather: Weather[];
  skills: string[];
  environment: string[];
  favorites: string[];
}
