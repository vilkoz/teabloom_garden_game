export type RGB = [number, number, number];

export interface TeaData {
  id: string;
  name: string;
  category: string;
  brew_time: number;
  heart_value: number;
  rarity: string;
  unlocked: boolean;
  unlock_cost: number;
  color: RGB;
}

export interface CatData {
  id: string;
  name: string;
  description: string;
  personality: string;
  favorite_tea: string;
  unlocked: boolean;
  unlock_requirement?: number;
  color: RGB;
  happy_popup_text?: string;
}

export interface TeaDataFile {
  teas: TeaData[];
}

export interface CatDataFile {
  cats: CatData[];
}

export interface GameData {
  teas: TeaData[];
  cats: CatData[];
}

export interface SpriteConfig {
  name: string;
  variants: string[];
  grid_cols: number;
  grid_rows: number;
  sprite_size: [number, number];
  render_size: [number, number];
  border_offset: [number, number];
  grid_offset: [number, number];
}

export interface AssetBundle {
  sprites: SpriteConfig[];
}

export interface GameStatistics {
  teas_served: number;
  cats_satisfied: number;
  cats_disappointed: number;
  total_hearts: number;
  correct_serves: number;
  wrong_serves: number;
  play_time: number;
  title_shown: boolean;
}

export type SceneType = 'loading' | 'menu' | 'game' | 'stats' | 'title';

export interface Point {
  x: number;
  y: number;
}

export type SceneResult =
  | { changeScene: SceneType }
  | { quit: true }
  | undefined;

export interface Scene {
  update(dt: number): SceneResult;
  draw(ctx: CanvasRenderingContext2D): void;
  pointerDown(point: Point): SceneResult;
  pointerMove(point: Point): void;
  pointerUp(point: Point): SceneResult;
  keyDown?(key: string): SceneResult;
}