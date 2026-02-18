import { appUrl } from './paths';

export const SoundEffect = {
  BUTTON_CLICK: 'button_click.wav',
  BUTTON_HOVER: 'button_hover.mp3',
  SUCCESS: 'success.wav',
  ERROR: 'error.wav',
  NOTIFICATION: 'notification.wav',
  HEART_COLLECT: 'heart_collect.wav',

  WATER_POUR: 'water_pour.wav',
  TEA_POUR: 'cup_fill.wav',
  CUP_FILL: 'cup_fill.wav',
  LEAVES_DISPOSE: 'leaves_dispose.wav',
  PICKUP: 'pickup.mp3',

  CAT_ARRIVE: 'cat_arrive.mp3',
  CAT_HAPPY: 'cat_happy.wav',
  CAT_DISAPPOINTED: 'cat_disappointed.wav',
  CAT_LEAVE: 'cat_arrive.wav',
  CAT_PET: 'cat_pet.wav',

  BACKGROUND_MUSIC: 'background_music.mp3',
  AMBIENT_GARDEN: 'ambient_garden.mp3',
} as const;

export type SoundEffectKey = keyof typeof SoundEffect;

const MUSIC_SOUND_TABLE: Partial<Record<SoundEffectKey, number>> = {
  BACKGROUND_MUSIC: 0.5,
  AMBIENT_GARDEN: 1.0,
};

const FALLBACK_BY_KEY: Partial<Record<SoundEffectKey, string[]>> = {
  CAT_LEAVE: ['cat_arrive.mp3'],
  WATER_POUR: ['water_pour.mp3'],
};

export class SoundManager {
  private readonly loaded = new Map<SoundEffectKey, string>();
  private readonly music = new Map<SoundEffectKey, HTMLAudioElement>();
  private musicVolume = 0.1;
  private sfxVolume = 0.7;
  private muted = false;
  musicEnabled = true;
  private sfxEnabled = true;
  private unlocked = false;

  unlock(): void {
    this.unlocked = true;
  }

  async warmup(): Promise<void> {
    const keys = Object.keys(SoundEffect) as SoundEffectKey[];
    await Promise.all(keys.map(async (key) => {
      const resolved = await this.resolveUrl(key);
      if (resolved) {
        this.loaded.set(key, resolved);
      }
    }));
  }

  playSound(key: SoundEffectKey, volume?: number): void {
    if (!this.sfxEnabled || this.muted || !this.unlocked) {
      return;
    }

    const src = this.loaded.get(key);
    if (!src) {
      return;
    }

    const sound = new Audio(src);
    sound.volume = Math.max(0, Math.min(1, volume ?? this.sfxVolume));
    void sound.play().catch(() => undefined);
  }

  playMusic(key: SoundEffectKey, loops = true): void {
    if (!this.musicEnabled || this.muted || !this.unlocked) {
      return;
    }

    const src = this.loaded.get(key);
    if (!src) {
      return;
    }

    let track = this.music.get(key);
    if (!track) {
      track = new Audio(src);
      track.loop = loops;
      this.music.set(key, track);
    }

    const correction = MUSIC_SOUND_TABLE[key] ?? 0.5;
    track.volume = this.musicVolume * correction;
    void track.play().catch(() => undefined);
  }

  stopAllMusic(): void {
    for (const track of this.music.values()) {
      track.pause();
      track.currentTime = 0;
    }
  }

  toggleMusic(): boolean {
    this.musicEnabled = !this.musicEnabled;
    if (!this.musicEnabled) {
      for (const track of this.music.values()) {
        track.pause();
      }
    } else {
      for (const [key, track] of this.music.entries()) {
        const correction = MUSIC_SOUND_TABLE[key] ?? 0.5;
        track.volume = this.musicVolume * correction;
        void track.play().catch(() => undefined);
      }
    }
    return this.musicEnabled;
  }

  setMusicVolume(volume: number): void {
    this.musicVolume = Math.max(0, Math.min(1, volume));
    for (const [key, track] of this.music.entries()) {
      const correction = MUSIC_SOUND_TABLE[key] ?? 0.5;
      track.volume = this.musicVolume * correction;
    }
  }

  setSfxVolume(volume: number): void {
    this.sfxVolume = Math.max(0, Math.min(1, volume));
  }

  private async resolveUrl(key: SoundEffectKey): Promise<string | null> {
    const primary = SoundEffect[key];
    const candidates = [primary, ...(FALLBACK_BY_KEY[key] ?? [])];

    for (const filename of candidates) {
      const url = appUrl(`assets/sounds/${filename}`);
      try {
        const response = await fetch(url, { method: 'HEAD' });
        if (response.ok) {
          return url;
        }
      } catch {
        continue;
      }
    }

    return null;
  }
}