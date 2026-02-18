import type { CatData, GameStatistics, TeaData } from './types';

interface SaveData {
  hearts: number;
  unlocked_teas: string[];
  unlocked_cats: string[];
  statistics: GameStatistics;
  best_combo: number;
}

type UnlockResult = { type: 'tea' | 'cat'; id: string };

const SAVE_KEY = 'teabloom_web_save_v1';

export class GameStateManager {
  hearts = 0;
  unlockedTeas: string[] = [];
  unlockedCats: string[] = [];
  statistics: GameStatistics;
  currentCombo = 0;
  bestCombo = 0;

  private readonly teas: TeaData[];
  private readonly cats: CatData[];

  constructor(teas: TeaData[], cats: CatData[]) {
    this.teas = teas;
    this.cats = cats;
    this.unlockedTeas = teas.filter((tea) => tea.unlocked).map((tea) => tea.id);
    this.unlockedCats = cats.filter((cat) => cat.unlocked).map((cat) => cat.id);
    this.statistics = {
      teas_served: 0,
      cats_satisfied: 0,
      cats_disappointed: 0,
      total_hearts: 0,
      correct_serves: 0,
      wrong_serves: 0,
      play_time: 0,
      title_shown: false,
    };

    this.loadProgress();
  }

  addHearts(amount: number): UnlockResult[] {
    this.hearts += amount;
    this.statistics.total_hearts += amount;
    this.saveProgress();
    return this.checkUnlocks();
  }

  isTeaUnlocked(teaId: string): boolean {
    return this.unlockedTeas.includes(teaId);
  }

  isCatUnlocked(catId: string): boolean {
    return this.unlockedCats.includes(catId);
  }

  updatePlaytime(dtMs: number): void {
    this.statistics.play_time += dtMs / 1000;
  }

  recordServe(correct: boolean): void {
    this.statistics.teas_served += 1;
    if (correct) {
      this.statistics.correct_serves += 1;
      this.statistics.cats_satisfied += 1;
      this.currentCombo += 1;
      if (this.currentCombo > this.bestCombo) {
        this.bestCombo = this.currentCombo;
      }
    } else {
      this.statistics.wrong_serves += 1;
      this.statistics.cats_disappointed += 1;
      this.currentCombo = 0;
    }
    this.saveProgress();
  }

  getComboBonus(): number {
    return this.currentCombo >= 5 ? 1 : 0;
  }

  saveProgress(): void {
    const payload: SaveData = {
      hearts: this.hearts,
      unlocked_teas: this.unlockedTeas,
      unlocked_cats: this.unlockedCats,
      statistics: this.statistics,
      best_combo: this.bestCombo,
    };

    localStorage.setItem(SAVE_KEY, JSON.stringify(payload));
  }

  private checkUnlocks(): UnlockResult[] {
    const unlocks: UnlockResult[] = [];

    for (const tea of this.teas) {
      if (tea.unlock_cost > 0 && this.statistics.total_hearts >= tea.unlock_cost) {
        if (!this.unlockedTeas.includes(tea.id)) {
          this.unlockedTeas.push(tea.id);
          unlocks.push({ type: 'tea', id: tea.id });
        }
      }
    }

    for (const cat of this.cats) {
      const required = cat.unlock_requirement ?? 0;
      if (required > 0 && this.statistics.total_hearts >= required) {
        if (!this.unlockedCats.includes(cat.id)) {
          this.unlockedCats.push(cat.id);
          unlocks.push({ type: 'cat', id: cat.id });
        }
      }
    }

    if (unlocks.length > 0) {
      this.saveProgress();
    }

    return unlocks;
  }

  private loadProgress(): void {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) {
      return;
    }

    try {
      const data = JSON.parse(raw) as Partial<SaveData>;
      this.hearts = data.hearts ?? 0;
      this.unlockedTeas = data.unlocked_teas ?? this.unlockedTeas;
      this.unlockedCats = data.unlocked_cats ?? this.unlockedCats;
      this.statistics = data.statistics ?? this.statistics;
      this.bestCombo = data.best_combo ?? 0;
    } catch {
      localStorage.removeItem(SAVE_KEY);
    }
  }
}