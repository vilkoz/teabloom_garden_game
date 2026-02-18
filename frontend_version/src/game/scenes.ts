import { FluidLoadingBackground } from './fluidSimulation';
import { ProceduralBackground } from './proceduralBackground';
import { GameStateManager } from './state';
import { SoundEffect, SoundManager } from './soundManager';
import { SpriteLoader } from './spriteLoader';
import type { CatData, GameData, Point, RGB, Scene, SceneResult, SceneType, TeaData } from './types';

interface LoadingTracker {
  messages: string[];
  done: boolean;
  error: boolean;
}

interface SceneDeps {
  width: number;
  height: number;
  data: GameData;
  gameState: GameStateManager;
  spriteLoader: SpriteLoader;
  soundManager: SoundManager;
  loading: LoadingTracker;
}

interface ButtonDef {
  x: number;
  y: number;
  w: number;
  h: number;
  label: string;
}

type KettleState = 'empty' | 'has_tea' | 'brewing' | 'ready';
type CatState = 'arriving' | 'waiting' | 'happy' | 'disappointed' | 'leaving';

type DragRef = TeaDiskObj | HotWaterObj | TeaKettleObj | ChaHaiObj | TeaCupObj;

interface TeaDiskObj {
  kind: 'tea_disk';
  tea: TeaData;
  base: Point;
  pos: Point;
  radius: number;
}

interface HotWaterObj {
  kind: 'hot_water';
  base: Point;
  pos: Point;
  isPouring: boolean;
  pourTimer: number;
}

interface TeaKettleObj {
  kind: 'tea_kettle';
  base: Point;
  pos: Point;
  state: KettleState;
  tea: TeaData | null;
  brewTimer: number;
  brewDuration: number;
  isPouring: boolean;
  pourTimer: number;
}

interface ChaHaiObj {
  kind: 'cha_hai';
  base: Point;
  pos: Point;
  tea: TeaData | null;
  pourCount: number;
  maxPours: number;
}

interface TeaCupObj {
  kind: 'tea_cup';
  index: number;
  base: Point;
  pos: Point;
  radius: number;
  tea: TeaData | null;
}

interface TeaGodObj {
  pos: Point;
  width: number;
  height: number;
  state: 'clean' | 'pouring_tea' | 'dropping_leaves';
  timer: number;
}

interface CatVisitor {
  data: CatData;
  slotIndex: number;
  slotPos: Point;
  pos: Point;
  state: CatState;
  patience: number;
  waitingTime: number;
  waitingLimit: number;
  served: boolean;
  animationTimer: number;
  birthday: string;
  leavingSoundPlayed: boolean;
}

function rgb(color: RGB, alpha = 1): string {
  return `rgba(${color[0]}, ${color[1]}, ${color[2]}, ${alpha})`;
}

function inRect(point: Point, rect: { x: number; y: number; w: number; h: number }): boolean {
  return point.x >= rect.x && point.x <= rect.x + rect.w && point.y >= rect.y && point.y <= rect.y + rect.h;
}

function drawRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, fill: string, stroke?: string): void {
  ctx.fillStyle = fill;
  ctx.fillRect(x, y, w, h);
  if (stroke) {
    ctx.strokeStyle = stroke;
    ctx.strokeRect(x, y, w, h);
  }
}

function drawText(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  size: number,
  color: string,
  align: CanvasTextAlign = 'left',
): void {
  ctx.font = `${size}px Inter, system-ui, sans-serif`;
  ctx.fillStyle = color;
  ctx.textAlign = align;
  ctx.textBaseline = 'middle';
  ctx.fillText(text, x, y);
}

function drawButton(ctx: CanvasRenderingContext2D, button: ButtonDef, fill: string): void {
  drawRect(ctx, button.x, button.y, button.w, button.h, fill, 'rgba(80, 56, 35, 0.65)');
  drawText(ctx, button.label, button.x + button.w / 2, button.y + button.h / 2, 24, '#3c281c', 'center');
}

function randomBirthday(): string {
  const now = Date.now();
  const ageDays = Math.floor(Math.random() * 15 * 365);
  const d = new Date(now - ageDays * 24 * 60 * 60 * 1000);
  return d.toLocaleDateString();
}

function drawSpriteCentered(
  ctx: CanvasRenderingContext2D,
  sprite: HTMLCanvasElement | null,
  x: number,
  y: number,
  fallback: () => void,
): void {
  if (sprite) {
    ctx.drawImage(sprite, x - sprite.width / 2, y - sprite.height / 2);
  } else {
    fallback();
  }
}

class LoadingScene implements Scene {
  private readonly fluid: FluidLoadingBackground;

  constructor(
    private readonly width: number,
    private readonly height: number,
    private readonly loading: LoadingTracker,
  ) {
    this.fluid = new FluidLoadingBackground();
  }

  update(dt: number): SceneResult {
    this.fluid.update(dt);
    return undefined;
  }

  draw(ctx: CanvasRenderingContext2D): void {
    this.fluid.draw(ctx);

    drawText(ctx, 'Teabloom garden', this.width / 2, 80, 48, 'rgb(100,70,50)', 'center');
    drawText(ctx, 'Loading game assets...', this.width / 2, 130, 24, 'rgb(150,120,90)', 'center');

    const visible = this.loading.messages.slice(-25);
    for (let i = 0; i < visible.length; i += 1) {
      let color = 'rgb(100,100,100)';
      if (visible[i].startsWith('Loaded')) {
        color = 'rgb(50,150,50)';
      } else if (visible[i].startsWith('All sprite loading complete')) {
        color = 'rgb(0,180,0)';
      } else if (visible[i].startsWith('Press')) {
        color = 'rgb(200,100,0)';
      }
      drawText(ctx, visible[i], 80, 180 + i * 22, 20, color);
    }

    if (this.loading.done) {
      drawText(ctx, 'Press any key or click to continue...', this.width / 2, this.height - 40, 20, '#f7e4cc', 'center');
    }
  }

  pointerDown(_point: Point): SceneResult {
    if (this.loading.done && !this.loading.error) {
      return { changeScene: 'menu' };
    }
    return undefined;
  }

  pointerMove(_point: Point): void {}

  pointerUp(_point: Point): SceneResult {
    return undefined;
  }

  keyDown(_key: string): SceneResult {
    if (this.loading.done && !this.loading.error) {
      return { changeScene: 'menu' };
    }
    return undefined;
  }
}

class MenuScene implements Scene {
  private readonly playButton: ButtonDef;
  private readonly statsButton: ButtonDef;
  private readonly quitButton: ButtonDef;
  private readonly muteButton: ButtonDef;
  private readonly background: ProceduralBackground;

  constructor(
    private readonly width: number,
    private readonly height: number,
    private readonly gameState: GameStateManager,
    private readonly spriteLoader: SpriteLoader,
    private readonly soundManager: SoundManager,
  ) {
    const buttonW = 300;
    const buttonH = 60;
    const centerX = this.width / 2 - buttonW / 2;
    this.playButton = { x: centerX, y: 290, w: buttonW, h: buttonH, label: 'Play' };
    this.statsButton = { x: centerX, y: 370, w: buttonW, h: buttonH, label: 'Statistics' };
    this.quitButton = { x: centerX, y: 450, w: buttonW, h: buttonH, label: 'Quit' };
    this.muteButton = { x: this.width - 60, y: this.height - 100, w: 50, h: 40, label: '' };
    this.background = new ProceduralBackground(this.width, this.height, Math.floor(Math.random() * 10000));

    this.soundManager.playMusic('BACKGROUND_MUSIC');
    this.soundManager.playMusic('AMBIENT_GARDEN');
  }

  update(dt: number): SceneResult {
    this.background.update(dt);
    return undefined;
  }

  draw(ctx: CanvasRenderingContext2D): void {
    this.background.draw(ctx);
    drawRect(ctx, 0, 0, this.width, 50, '#ebe2d9');
    drawRect(ctx, 0, this.height - 50, this.width, 50, '#ebe2d9');

    const logo = this.spriteLoader.getSprite('logo', 'single');
    if (logo) {
      ctx.drawImage(logo, this.width / 2 - logo.width / 2, 80);
    } else {
      drawText(ctx, 'Tea Garden Cats', this.width / 2, 165, 72, '#75492e', 'center');
    }

    drawText(ctx, `${this.gameState.hearts} Hearts`, 20, 24, 36, '#c22553');

    drawButton(ctx, this.playButton, '#b8e6b8');
    drawButton(ctx, this.statsButton, '#b8dff4');
    drawButton(ctx, this.quitButton, '#f6cad4');

    const muteColor = this.soundManager.musicEnabled ? '#d4d4d4' : '#9f9f9f';
    drawRect(ctx, this.muteButton.x, this.muteButton.y, this.muteButton.w, this.muteButton.h, muteColor, '#6f6f6f');
    drawText(ctx, this.soundManager.musicEnabled ? '🔊' : '🔇', this.muteButton.x + 25, this.muteButton.y + 20, 24, '#333', 'center');

    drawText(ctx, 'Made with love for someone special', this.width / 2, this.height - 20, 22, '#8b7465', 'center');
  }

  pointerDown(point: Point): SceneResult {
    if (inRect(point, this.muteButton)) {
      this.soundManager.toggleMusic();
      this.soundManager.playSound('BUTTON_CLICK');
      return undefined;
    }
    if (inRect(point, this.playButton)) {
      this.soundManager.playSound('BUTTON_CLICK');
      return { changeScene: 'game' };
    }
    if (inRect(point, this.statsButton)) {
      this.soundManager.playSound('BUTTON_CLICK');
      return { changeScene: 'stats' };
    }
    if (inRect(point, this.quitButton)) {
      this.soundManager.playSound('BUTTON_CLICK');
      return { quit: true };
    }
    return undefined;
  }

  pointerMove(_point: Point): void {}

  pointerUp(_point: Point): SceneResult {
    return undefined;
  }
}

class StatsScene implements Scene {
  private readonly backButton: ButtonDef;

  constructor(
    private readonly width: number,
    private readonly height: number,
    private readonly gameState: GameStateManager,
    private readonly soundManager: SoundManager,
  ) {
    this.backButton = { x: this.width / 2 - 100, y: this.height - 90, w: 200, h: 60, label: 'Back' };
  }

  update(_dt: number): SceneResult {
    return undefined;
  }

  draw(ctx: CanvasRenderingContext2D): void {
    drawRect(ctx, 0, 0, this.width, this.height, '#f5f0df');
    drawText(ctx, 'Statistics', this.width / 2, 60, 56, '#75492e', 'center');

    const s = this.gameState.statistics;
    const lines = [
      `Total Hearts Earned: ${s.total_hearts}`,
      `Current Hearts: ${this.gameState.hearts}`,
      '',
      `Teas Served: ${s.teas_served}`,
      `Cats Satisfied: ${s.cats_satisfied} 😺`,
      `Cats Disappointed: ${s.cats_disappointed} 😿`,
      '',
      `Correct Serves: ${s.correct_serves}`,
      `Wrong Serves: ${s.wrong_serves}`,
      '',
      `Best Combo: ${this.gameState.bestCombo}`,
      `Current Combo: ${this.gameState.currentCombo}`,
      '',
      `Play Time: ${Math.floor(s.play_time / 60)}m ${Math.floor(s.play_time % 60)}s`,
    ];

    let y = 140;
    for (const line of lines) {
      if (line.length > 0) {
        drawText(ctx, line, this.width / 2, y, 28, '#523f35', 'center');
      }
      y += 36;
    }

    drawButton(ctx, this.backButton, '#e5e5e5');
  }

  pointerDown(point: Point): SceneResult {
    if (inRect(point, this.backButton)) {
      this.soundManager.playSound('BUTTON_CLICK');
      return { changeScene: 'menu' };
    }
    return undefined;
  }

  pointerMove(_point: Point): void {}

  pointerUp(_point: Point): SceneResult {
    return undefined;
  }
}

class TitleScene implements Scene {
  private readonly text: string;
  private displayed = '';
  private charIndex = 0;
  private charTimer = 0;
  private readonly charInterval = 40;
  private finished = false;
  private readonly continueButton: ButtonDef;
  private readonly menuButton: ButtonDef;

  constructor(
    private readonly width: number,
    private readonly height: number,
  ) {
    this.text =
      'З Днем Валентина, моя маленька мапко (minimaps))!\n' +
      'Як промені літнього сонця, ти робиш моє життя щасливим.\n' +
      'Дякую тобі за наші вечори, поїздки, чаювання, сміх,\n' +
      'за обійми і за всі маленькі моменти — вони для мене безцінні.\n' +
      'Нехай цей день буде наповнений прогулянками, слодощами\n' +
      'звісно чаєм, усмішками і мільйоном поцілунків для тебе.\n' +
      'Твій лапілапс.';

    const buttonW = 220;
    const buttonH = 52;
    this.continueButton = { x: this.width / 2 - buttonW - 12, y: this.height - 110, w: buttonW, h: buttonH, label: 'Continue Game' };
    this.menuButton = { x: this.width / 2 + 12, y: this.height - 110, w: buttonW, h: buttonH, label: 'Main Menu' };
  }

  update(dt: number): SceneResult {
    if (this.finished) {
      return undefined;
    }

    this.charTimer += dt;
    while (this.charTimer >= this.charInterval && this.charIndex < this.text.length) {
      this.charTimer -= this.charInterval;
      this.displayed += this.text[this.charIndex];
      this.charIndex += 1;
    }

    if (this.charIndex >= this.text.length) {
      this.finished = true;
    }

    return undefined;
  }

  draw(ctx: CanvasRenderingContext2D): void {
    drawRect(ctx, 0, 0, this.width, this.height, '#f0e6ee');
    const panelX = this.width * 0.09;
    const panelY = this.height * 0.1;
    const panelW = this.width * 0.82;
    const panelH = this.height * 0.72;
    drawRect(ctx, panelX, panelY, panelW, panelH, '#fff8f3', '#c9a7aa');
    drawText(ctx, '❤️', this.width / 2, panelY + 70, 90, '#e3567f', 'center');

    const lines = this.wrapText(ctx, this.displayed, panelW - 70);
    let y = panelY + 140;
    for (const line of lines) {
      drawText(ctx, line, panelX + 36, y, 31, '#5d2d45');
      y += 38;
    }

    drawButton(ctx, this.continueButton, '#f7c8d4');
    drawButton(ctx, this.menuButton, '#f7c8d4');
  }

  pointerDown(point: Point): SceneResult {
    if (inRect(point, this.continueButton)) {
      return { changeScene: 'game' };
    }
    if (inRect(point, this.menuButton)) {
      return { changeScene: 'menu' };
    }
    return undefined;
  }

  pointerMove(_point: Point): void {}

  pointerUp(_point: Point): SceneResult {
    return undefined;
  }

  keyDown(key: string): SceneResult {
    if (key === 'Enter' || key === ' ') {
      return { changeScene: 'game' };
    }
    if (key === 'Escape') {
      return { changeScene: 'menu' };
    }
    return undefined;
  }

  private wrapText(ctx: CanvasRenderingContext2D, text: string, maxWidth: number): string[] {
    const output: string[] = [];
    const rawLines = text.split('\n');
    ctx.font = '31px Inter, system-ui, sans-serif';

    for (const raw of rawLines) {
      const words = raw.split(' ');
      let line = '';
      for (const word of words) {
        const candidate = line.length === 0 ? word : `${line} ${word}`;
        if (ctx.measureText(candidate).width <= maxWidth) {
          line = candidate;
        } else {
          if (line.length > 0) {
            output.push(line);
          }
          line = word;
        }
      }
      if (line.length > 0) {
        output.push(line);
      }
    }

    return output;
  }
}

class GameScene implements Scene {
  private teaDisks: TeaDiskObj[] = [];
  private readonly hotWater: HotWaterObj;
  private readonly teaKettle: TeaKettleObj;
  private readonly chaHai: ChaHaiObj;
  private readonly teaCups: TeaCupObj[] = [];
  private readonly teaGod: TeaGodObj;
  private catVisitors: CatVisitor[] = [];
  private catSpawnTimer = 0;
  private readonly catSpawnInterval = 10000;
  private dragging: DragRef | null = null;
  private dragOffset: Point = { x: 0, y: 0 };
  private hoveredCat: CatVisitor | null = null;
  private hoveredCup: TeaCupObj | null = null;
  private readonly menuButton: ButtonDef;
  private readonly muteButton: ButtonDef;
  private popup: { text: string; pos: Point; timer: number } | null = null;

  constructor(
    private readonly width: number,
    private readonly height: number,
    private readonly data: GameData,
    private readonly gameState: GameStateManager,
    private readonly spriteLoader: SpriteLoader,
    private readonly soundManager: SoundManager,
  ) {
    this.menuButton = { x: this.width - 120, y: 10, w: 110, h: 40, label: 'Menu' };
    this.muteButton = { x: this.width - 60, y: this.height - 50, w: 50, h: 40, label: '' };

    for (let i = 0; i < data.teas.length; i += 1) {
      const tea = data.teas[i];
      this.teaDisks.push({
        kind: 'tea_disk',
        tea,
        base: { x: 250 + (i % 8) * 90, y: 80 },
        pos: { x: 250 + (i % 8) * 90, y: 80 },
        radius: 40,
      });
    }

    this.hotWater = {
      kind: 'hot_water',
      base: { x: 120, y: 180 },
      pos: { x: 120, y: 180 },
      isPouring: false,
      pourTimer: 0,
    };

    this.teaKettle = {
      kind: 'tea_kettle',
      base: { x: 120, y: 280 },
      pos: { x: 120, y: 280 },
      state: 'empty',
      tea: null,
      brewTimer: 0,
      brewDuration: 0,
      isPouring: false,
      pourTimer: 0,
    };

    this.chaHai = {
      kind: 'cha_hai',
      base: { x: 120, y: 400 },
      pos: { x: 120, y: 400 },
      tea: null,
      pourCount: 0,
      maxPours: 8,
    };

    const cupPositions: Point[] = [
      { x: 70, y: 500 },
      { x: 120, y: 500 },
      { x: 170, y: 500 },
      { x: 220, y: 500 },
      { x: 70, y: 550 },
      { x: 120, y: 550 },
      { x: 170, y: 550 },
      { x: 220, y: 550 },
    ];
    for (let i = 0; i < cupPositions.length; i += 1) {
      this.teaCups.push({ kind: 'tea_cup', index: i, base: cupPositions[i], pos: { ...cupPositions[i] }, radius: 20, tea: null });
    }

    this.teaGod = { pos: { x: 220, y: 260 }, width: 80, height: 80, state: 'clean', timer: 0 };
    this.spawnCat();
  }

  update(dt: number): SceneResult {
    this.gameState.updatePlaytime(dt);

    if (this.teaKettle.state === 'brewing') {
      this.teaKettle.brewTimer += dt;
      if (this.teaKettle.brewTimer >= this.teaKettle.brewDuration) {
        this.teaKettle.state = 'ready';
      }
    }

    if (this.hotWater.isPouring) {
      this.hotWater.pourTimer += dt;
      if (this.hotWater.pourTimer >= 800) {
        this.hotWater.isPouring = false;
        this.hotWater.pourTimer = 0;
        this.hotWater.pos = { ...this.hotWater.base };
      }
    }

    if (this.teaKettle.isPouring) {
      this.teaKettle.pourTimer += dt;
      if (this.teaKettle.pourTimer >= 800) {
        this.teaKettle.isPouring = false;
        this.teaKettle.pourTimer = 0;
        this.teaKettle.pos = { ...this.teaKettle.base };
      }
    }

    if (this.teaGod.state !== 'clean') {
      this.teaGod.timer += dt;
      if (this.teaGod.timer >= 800) {
        this.teaGod.state = 'clean';
        this.teaGod.timer = 0;
      }
    }

    if (this.popup) {
      this.popup.timer -= dt;
      if (this.popup.timer <= 0) {
        this.popup = null;
      }
    }

    for (const cat of this.catVisitors) {
      cat.animationTimer += dt;
      if (cat.state === 'arriving') {
        if (cat.pos.x > cat.slotPos.x) {
          cat.pos.x -= dt * 0.03;
        } else {
          cat.pos.x = cat.slotPos.x;
          cat.state = 'waiting';
          cat.animationTimer = 0;
        }
      } else if (cat.state === 'waiting') {
        cat.waitingTime += dt;
        cat.patience = Math.max(0, 100 - (cat.waitingTime / cat.waitingLimit) * 100);
        if (cat.patience <= 0) {
          cat.state = 'leaving';
          cat.animationTimer = 0;
        }
      } else if (cat.state === 'happy') {
        if (cat.animationTimer > 2000) {
          cat.state = 'leaving';
          cat.animationTimer = 0;
        }
      } else if (cat.state === 'disappointed') {
        if (cat.animationTimer > 1500) {
          cat.state = 'leaving';
          cat.animationTimer = 0;
        }
      } else if (cat.state === 'leaving') {
        if (!cat.leavingSoundPlayed) {
          this.soundManager.playSound('CAT_LEAVE');
          cat.leavingSoundPlayed = true;
        }
        cat.pos.x += dt * 0.18;
      }
    }

    this.catVisitors = this.catVisitors.filter((cat) => cat.pos.x <= 900);

    this.catSpawnTimer += dt;
    if (this.catSpawnTimer >= this.catSpawnInterval) {
      this.catSpawnTimer = 0;
      this.spawnCat();
    }

    if (this.gameState.statistics.total_hearts >= 120 && !this.gameState.statistics.title_shown) {
      this.gameState.statistics.title_shown = true;
      this.gameState.saveProgress();
      return { changeScene: 'title' };
    }

    return undefined;
  }

  draw(ctx: CanvasRenderingContext2D): void {
    drawRect(ctx, 0, 0, this.width, this.height, '#f5ebdc');

    const border = this.spriteLoader.getSprite('border_frame', 'single');
    if (border) {
      ctx.drawImage(border, this.width / 2 - border.width / 2, this.height / 2 - border.height / 2);
    } else {
      drawRect(ctx, 0, 0, this.width, 20, '#7ea06b');
      drawRect(ctx, 0, this.height - 20, this.width, 20, '#7ea06b');
      drawRect(ctx, 0, 0, 20, this.height, '#7ea06b');
      drawRect(ctx, this.width - 20, 0, 20, this.height, '#7ea06b');
    }

    const teaDrawerSprite = this.spriteLoader.getSprite('tea_drawer', 'single');
    if (teaDrawerSprite) {
      ctx.drawImage(teaDrawerSprite, 500 - teaDrawerSprite.width / 2, 80 - teaDrawerSprite.height / 2);
    } else {
      drawRect(ctx, 230, 40, 540, 80, '#8b5a3c', '#4f3322');
    }
    drawText(ctx, 'Tea Drawer - Drag tea to kettle', 500, 30, 18, '#fff6cf', 'center');

    for (const disk of this.teaDisks) {
      if (this.dragging !== disk) {
        this.drawTeaDisk(ctx, disk);
      }
    }

    const chaBan = this.spriteLoader.getSprite('cha_ban', 'single');
    if (chaBan) {
      ctx.drawImage(chaBan, 150 - chaBan.width / 2, 380 - chaBan.height / 2);
    } else {
      drawRect(ctx, 30, 140, 240, 480, '#a07850', '#5f4128');
    }
    drawText(ctx, 'Cha Ban', 150, 150, 20, '#fff6cf', 'center');

    if (this.dragging !== this.hotWater && !this.hotWater.isPouring) {
      this.drawHotWater(ctx, this.hotWater);
    }
    if (this.dragging !== this.teaKettle && !this.teaKettle.isPouring) {
      this.drawTeaKettle(ctx, this.teaKettle);
    }
    if (this.dragging !== this.hotWater && this.hotWater.isPouring) {
      this.drawHotWater(ctx, this.hotWater);
    }
    if (this.dragging !== this.chaHai) {
      this.drawChaHai(ctx, this.chaHai);
    }
    if (this.dragging !== this.teaKettle && this.teaKettle.isPouring) {
      this.drawTeaKettle(ctx, this.teaKettle);
    }

    for (const cup of this.teaCups) {
      if (this.dragging !== cup) {
        this.drawTeaCup(ctx, cup);
      }
    }
    this.drawTeaGod(ctx);

    drawText(ctx, 'Cat Visitors', 550, 160, 22, '#6a4a34', 'center');
    for (const cat of this.catVisitors) {
      this.drawCat(ctx, cat);
    }

    drawText(ctx, `Hearts: ${this.gameState.hearts}`, 650, 30, 28, '#c83232', 'center');
    if (this.gameState.currentCombo > 1) {
      drawText(ctx, `Combo x${this.gameState.currentCombo}!`, 650, 60, 24, '#f09a00', 'center');
    }

    drawButton(ctx, this.menuButton, '#dfdfdf');
    const muteColor = this.soundManager.musicEnabled ? '#d4d4d4' : '#9f9f9f';
    drawRect(ctx, this.muteButton.x, this.muteButton.y, this.muteButton.w, this.muteButton.h, muteColor, '#6f6f6f');
    drawText(ctx, this.soundManager.musicEnabled ? '🔊' : '🔇', this.muteButton.x + 25, this.muteButton.y + 20, 24, '#333', 'center');

    const instructions = [
      '1. Drag tea disk to kettle',
      '2. Drag hot water to kettle',
      '3. Wait for brewing',
      '4. Drag kettle to cha hai',
      '5. Drag cha hai to cups',
      '6. Drag cups to cats',
      '7. Pet happy cats for bonus!',
    ];
    for (let i = 0; i < instructions.length; i += 1) {
      drawText(ctx, instructions[i], 300, 520 + i * 14, 14, '#75513b');
    }

    if (this.dragging) {
      if (this.dragging.kind === 'tea_disk') {
        this.drawTeaDisk(ctx, this.dragging);
      } else if (this.dragging.kind === 'hot_water') {
        this.drawHotWater(ctx, this.dragging);
      } else if (this.dragging.kind === 'tea_kettle') {
        this.drawTeaKettle(ctx, this.dragging);
      } else if (this.dragging.kind === 'cha_hai') {
        this.drawChaHai(ctx, this.dragging);
      } else if (this.dragging.kind === 'tea_cup') {
        this.drawTeaCup(ctx, this.dragging);
      }
    }

    if (this.hoveredCat) {
      this.drawTooltip(
        ctx,
        { x: this.hoveredCat.pos.x + 52, y: this.hoveredCat.pos.y - 62 },
        this.hoveredCat.data.name,
        [
          this.hoveredCat.data.description,
          `Personality: ${this.hoveredCat.data.personality}`,
          `Birthday: ${this.hoveredCat.birthday}`,
        ],
      );
    } else if (this.hoveredCup && this.hoveredCup.tea) {
      this.drawTooltip(
        ctx,
        { x: this.hoveredCup.pos.x + 34, y: this.hoveredCup.pos.y - 40 },
        this.hoveredCup.tea.name,
        [
          `Type: ${this.hoveredCup.tea.category.replace('_', ' ')}`,
          `Brew Time: ${this.hoveredCup.tea.brew_time.toFixed(1)}s`,
        ],
      );
    }

    if (this.popup) {
      drawRect(ctx, this.popup.pos.x - 120, this.popup.pos.y - 40, 240, 50, 'rgba(255, 247, 231, 0.96)', 'rgba(130, 89, 59, 0.8)');
      drawText(ctx, this.popup.text, this.popup.pos.x, this.popup.pos.y - 15, 18, '#6b4635', 'center');
    }
  }

  pointerDown(point: Point): SceneResult {
    if (inRect(point, this.muteButton)) {
      this.soundManager.toggleMusic();
      this.soundManager.playSound('BUTTON_CLICK');
      return undefined;
    }

    if (inRect(point, this.menuButton)) {
      this.soundManager.playSound('BUTTON_CLICK');
      return { changeScene: 'menu' };
    }

    for (const cat of this.catVisitors) {
      if (this.catContains(cat, point) && cat.state === 'happy' && cat.animationTimer < 2500) {
        this.gameState.addHearts(1);
        this.soundManager.playSound('CAT_PET');
        this.soundManager.playSound('HEART_COLLECT');
        this.popup = { text: '+1 heart for petting!', pos: { x: cat.pos.x, y: cat.pos.y - 44 }, timer: 1000 };
        return undefined;
      }
    }

    for (const disk of this.teaDisks) {
      if (this.gameState.isTeaUnlocked(disk.tea.id) && this.circleContains(point, disk.pos, disk.radius)) {
        this.dragging = disk;
        this.dragOffset = { x: disk.pos.x - point.x, y: disk.pos.y - point.y };
        this.soundManager.playSound('PICKUP');
        return undefined;
      }
    }

    if (this.hotWaterContains(point)) {
      this.dragging = this.hotWater;
      this.dragOffset = { x: this.hotWater.pos.x - point.x, y: this.hotWater.pos.y - point.y };
      this.soundManager.playSound('PICKUP');
      return undefined;
    }

    if (this.teaKettle.state === 'ready' && this.kettleContains(point)) {
      this.dragging = this.teaKettle;
      this.dragOffset = { x: this.teaKettle.pos.x - point.x, y: this.teaKettle.pos.y - point.y };
      this.soundManager.playSound('PICKUP');
      return undefined;
    }

    if (this.chaHai.tea && this.chaHaiContains(point)) {
      this.dragging = this.chaHai;
      this.dragOffset = { x: this.chaHai.pos.x - point.x, y: this.chaHai.pos.y - point.y };
      this.soundManager.playSound('PICKUP');
      return undefined;
    }

    for (const cup of this.teaCups) {
      if (cup.tea && this.circleContains(point, cup.pos, cup.radius)) {
        this.dragging = cup;
        this.dragOffset = { x: cup.pos.x - point.x, y: cup.pos.y - point.y };
        this.soundManager.playSound('PICKUP');
        return undefined;
      }
    }

    return undefined;
  }

  pointerMove(point: Point): void {
    if (!this.dragging) {
      this.hoveredCat = null;
      this.hoveredCup = null;

      for (const cat of this.catVisitors) {
        if (this.catContains(cat, point)) {
          this.hoveredCat = cat;
          break;
        }
      }

      if (!this.hoveredCat) {
        for (const cup of this.teaCups) {
          if (cup.tea && this.circleContains(point, cup.pos, cup.radius)) {
            this.hoveredCup = cup;
            break;
          }
        }
      }
      return;
    }

    this.dragging.pos.x = point.x + this.dragOffset.x;
    this.dragging.pos.y = point.y + this.dragOffset.y;

    if (this.dragging.kind === 'tea_kettle' && this.chaHaiContains(point) && this.teaKettle.state === 'ready') {
      this.teaKettle.isPouring = true;
      this.teaKettle.pourTimer = 0;
    }
  }

  pointerUp(point: Point): SceneResult {
    if (!this.dragging) {
      return undefined;
    }

    if (this.dragging.kind === 'tea_disk') {
      if (this.kettleContains(point) && this.teaKettle.state === 'empty') {
        this.teaKettle.state = 'has_tea';
        this.teaKettle.tea = this.dragging.tea;
      }
      this.dragging.pos = { ...this.dragging.base };
    } else if (this.dragging.kind === 'hot_water') {
      if (this.kettleContains(point) && this.teaKettle.state === 'has_tea' && this.teaKettle.tea) {
        this.teaKettle.state = 'brewing';
        this.teaKettle.brewTimer = 0;
        this.teaKettle.brewDuration = this.teaKettle.tea.brew_time * 1000;
        this.hotWater.isPouring = true;
        this.hotWater.pourTimer = 0;
        this.hotWater.pos = { x: this.teaKettle.pos.x - 50, y: this.teaKettle.pos.y - 100 };
        this.soundManager.playSound('WATER_POUR');
      } else {
        this.hotWater.pos = { ...this.hotWater.base };
        this.soundManager.playSound('ERROR');
      }
    } else if (this.dragging.kind === 'tea_kettle') {
      if (this.teaGodContains(point)) {
        this.teaKettle.state = 'empty';
        this.teaKettle.tea = null;
        this.teaKettle.brewTimer = 0;
        this.teaKettle.brewDuration = 0;
        this.teaGod.state = 'dropping_leaves';
        this.teaGod.timer = 0;
        this.soundManager.playSound('LEAVES_DISPOSE');
      } else if (this.chaHaiContains(point) && this.teaKettle.state === 'ready' && this.teaKettle.tea) {
        this.chaHai.tea = this.teaKettle.tea;
        this.chaHai.pourCount = 0;
        this.teaKettle.state = 'empty';
        this.teaKettle.tea = null;
        this.teaKettle.brewTimer = 0;
        this.teaKettle.brewDuration = 0;
        this.teaKettle.isPouring = true;
        this.teaKettle.pourTimer = 0;
        this.teaKettle.pos = { x: this.chaHai.pos.x - 50, y: this.chaHai.pos.y - 100 };
        this.soundManager.playSound('TEA_POUR');
      } else {
        this.teaKettle.pos = { ...this.teaKettle.base };
      }
    } else if (this.dragging.kind === 'cha_hai') {
      if (this.teaGodContains(point)) {
        this.chaHai.tea = null;
        this.chaHai.pourCount = 0;
        this.teaGod.state = 'pouring_tea';
        this.teaGod.timer = 0;
        this.soundManager.playSound('LEAVES_DISPOSE');
      } else {
        for (const cup of this.teaCups) {
          if (!cup.tea && this.circleContains(point, cup.pos, cup.radius) && this.chaHai.tea) {
            cup.tea = this.chaHai.tea;
            this.chaHai.pourCount += 1;
            this.soundManager.playSound('CUP_FILL');
            if (this.chaHai.pourCount >= this.chaHai.maxPours) {
              this.chaHai.tea = null;
              this.chaHai.pourCount = 0;
            }
            break;
          }
        }
      }
      this.chaHai.pos = { ...this.chaHai.base };
    } else if (this.dragging.kind === 'tea_cup') {
      if (this.teaGodContains(point)) {
        this.dragging.tea = null;
        this.teaGod.state = 'pouring_tea';
        this.teaGod.timer = 0;
        this.soundManager.playSound('LEAVES_DISPOSE');
      } else {
        for (const cat of this.catVisitors) {
          if (this.catContains(cat, point) && cat.state === 'waiting' && this.dragging.tea) {
            const servedTea = this.dragging.tea;
            this.dragging.tea = null;
            cat.served = true;
            cat.animationTimer = 0;

            const match = servedTea.id === cat.data.favorite_tea;
            const hearts = match ? 3 : 1;
            cat.state = match ? 'happy' : 'disappointed';

            this.gameState.recordServe(match);
            this.gameState.addHearts(hearts);

            if (match) {
              this.soundManager.playSound('CAT_HAPPY');
              this.soundManager.playSound('SUCCESS');
              if (cat.data.happy_popup_text) {
                this.popup = { text: cat.data.happy_popup_text, pos: { x: cat.pos.x, y: cat.pos.y - 50 }, timer: 2200 };
              }
            } else {
              this.soundManager.playSound('CAT_DISAPPOINTED');
            }
            this.soundManager.playSound('HEART_COLLECT');
            break;
          }
        }
      }

      this.dragging.pos = { ...this.dragging.base };
    }

    this.dragging = null;
    this.dragOffset = { x: 0, y: 0 };
    this.gameState.saveProgress();
    return undefined;
  }

  keyDown(_key: string): SceneResult {
    return undefined;
  }

  private spawnCat(): void {
    if (this.catVisitors.length >= 5) {
      return;
    }

    const available = this.data.cats.filter((cat) => this.gameState.isCatUnlocked(cat.id));
    if (available.length === 0) {
      return;
    }

    const occupied = new Set(this.catVisitors.map((cat) => cat.slotIndex));
    const freeSlots = [0, 1, 2, 3, 4].filter((slot) => !occupied.has(slot));
    if (freeSlots.length === 0) {
      return;
    }

    const slotIndex = freeSlots[Math.floor(Math.random() * freeSlots.length)];
    const catData = available[Math.floor(Math.random() * available.length)];
    const slotPos = { x: 500, y: 200 + slotIndex * 90 };

    this.catVisitors.push({
      data: catData,
      slotIndex,
      slotPos,
      pos: { x: 850, y: slotPos.y },
      state: 'arriving',
      patience: 100,
      waitingTime: 0,
      waitingLimit: 15000,
      served: false,
      animationTimer: 0,
      birthday: randomBirthday(),
      leavingSoundPlayed: false,
    });
    this.soundManager.playSound('CAT_ARRIVE');
  }

  private drawTeaDisk(ctx: CanvasRenderingContext2D, disk: TeaDiskObj): void {
    const unlocked = this.gameState.isTeaUnlocked(disk.tea.id);
    const sprite = this.spriteLoader.getSprite('tea_disks', disk.tea.id);
    drawSpriteCentered(ctx, sprite, disk.pos.x, disk.pos.y, () => {
      ctx.beginPath();
      ctx.arc(disk.pos.x, disk.pos.y, disk.radius, 0, Math.PI * 2);
      ctx.fillStyle = rgb(disk.tea.color);
      ctx.fill();
      ctx.strokeStyle = 'rgba(80, 60, 40, 0.8)';
      ctx.stroke();
    });

    drawText(ctx, disk.tea.name.slice(0, 8), disk.pos.x, disk.pos.y - 5, 14, '#ffffff', 'center');
    drawText(ctx, `${Math.floor(disk.tea.brew_time)}s`, disk.pos.x, disk.pos.y + 10, 14, '#fff4cc', 'center');

    if (!unlocked) {
      const lock = this.spriteLoader.getSprite('lock_icon', 'single');
      if (lock) {
        ctx.drawImage(lock, disk.pos.x - lock.width / 2, disk.pos.y - lock.height / 2);
      } else {
        ctx.beginPath();
        ctx.arc(disk.pos.x, disk.pos.y, disk.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(0,0,0,0.55)';
        ctx.fill();
        drawText(ctx, 'LOCK', disk.pos.x, disk.pos.y, 15, '#ffd269', 'center');
      }
    }
  }

  private drawHotWater(ctx: CanvasRenderingContext2D, hotWater: HotWaterObj): void {
    const variant = hotWater.isPouring ? 'pouring' : 'ready';
    const sprite = this.spriteLoader.getSprite('kettle', variant);
    drawSpriteCentered(ctx, sprite, hotWater.pos.x, hotWater.pos.y, () => {
      drawRect(ctx, hotWater.pos.x - 35, hotWater.pos.y - 35, 70, 70, '#666a7f', '#43465a');
      drawText(ctx, '~~~', hotWater.pos.x, hotWater.pos.y - 48, 20, '#d5e5ff', 'center');
      drawText(ctx, 'Hot', hotWater.pos.x, hotWater.pos.y + 2, 13, '#ffffff', 'center');
    });
  }

  private drawTeaKettle(ctx: CanvasRenderingContext2D, kettle: TeaKettleObj): void {
    const variantMap: Record<KettleState, string> = {
      empty: 'empty',
      has_tea: 'tea_leaves',
      brewing: 'brewing',
      ready: 'ready',
    };
    const sprite = this.spriteLoader.getSprite('gaiwan', variantMap[kettle.state]);
    drawSpriteCentered(ctx, sprite, kettle.pos.x, kettle.pos.y, () => {
      let color = '#c8c8c8';
      if (kettle.state === 'has_tea' && kettle.tea) {
        color = rgb(kettle.tea.color);
      } else if (kettle.state === 'brewing') {
        color = '#b69568';
      } else if (kettle.state === 'ready') {
        color = '#f2cb53';
      }
      drawRect(ctx, kettle.pos.x - 40, kettle.pos.y - 40, 80, 80, color, '#6f5138');
    });

    let stateText = 'Empty';
    if (kettle.state === 'has_tea') {
      stateText = 'Add ♨';
    } else if (kettle.state === 'brewing') {
      const pct = Math.min(100, Math.floor((kettle.brewTimer / Math.max(1, kettle.brewDuration)) * 100));
      stateText = `${pct}%`;
    } else if (kettle.state === 'ready') {
      stateText = 'Ready!';
    }
    drawText(ctx, stateText, kettle.pos.x, kettle.pos.y + 70, 14, '#49362a', 'center');
  }

  private drawChaHai(ctx: CanvasRenderingContext2D, chaHai: ChaHaiObj): void {
    const variant = chaHai.tea ? 'filled' : 'empty';
    const sprite = this.spriteLoader.getSprite('chahai', variant);
    drawSpriteCentered(ctx, sprite, chaHai.pos.x, chaHai.pos.y, () => {
      const color = chaHai.tea ? rgb(chaHai.tea.color) : '#dddddd';
      ctx.beginPath();
      ctx.ellipse(chaHai.pos.x, chaHai.pos.y, 30, 25, 0, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.strokeStyle = '#6b4a31';
      ctx.stroke();
    });
    if (chaHai.tea) {
      drawText(ctx, `Pour (${chaHai.maxPours - chaHai.pourCount})`, chaHai.pos.x, chaHai.pos.y + 52, 13, '#49362a', 'center');
    }
  }

  private drawTeaCup(ctx: CanvasRenderingContext2D, cup: TeaCupObj): void {
    const variant = cup.tea ? 'filled' : 'empty';
    const sprite = this.spriteLoader.getSprite('teacup', variant);
    drawSpriteCentered(ctx, sprite, cup.pos.x, cup.pos.y, () => {
      ctx.beginPath();
      ctx.arc(cup.pos.x, cup.pos.y, cup.radius, 0, Math.PI * 2);
      ctx.fillStyle = cup.tea ? rgb(cup.tea.color) : '#ffffff';
      ctx.fill();
      ctx.strokeStyle = '#6f5138';
      ctx.stroke();
    });
  }

  private drawTeaGod(ctx: CanvasRenderingContext2D): void {
    let variant = 'clean';
    if (this.teaGod.state === 'pouring_tea') {
      variant = this.teaGod.timer < 400 ? 'pouring_tea_1' : 'pouring_tea_2';
    } else if (this.teaGod.state === 'dropping_leaves') {
      variant = this.teaGod.timer < 400 ? 'dropping_leaves_1' : 'dropping_leaves_2';
    }

    const sprite = this.spriteLoader.getSprite('tea_god', variant);
    drawSpriteCentered(ctx, sprite, this.teaGod.pos.x, this.teaGod.pos.y, () => {
      drawRect(
        ctx,
        this.teaGod.pos.x - this.teaGod.width / 2,
        this.teaGod.pos.y - this.teaGod.height / 2,
        this.teaGod.width,
        this.teaGod.height,
        '#9f816c',
        '#5b4131',
      );
    });
    drawText(ctx, 'Tea God', this.teaGod.pos.x, this.teaGod.pos.y + 54, 13, '#fff3e6', 'center');
  }

  private drawCat(ctx: CanvasRenderingContext2D, cat: CatVisitor): void {
    let variant = 'normal';
    if (cat.state === 'happy') {
      variant = 'happy';
    } else if (cat.state === 'disappointed') {
      variant = 'disappointed';
    } else if (cat.patience < 40) {
      variant = 'impatient';
    }
    if (cat.state === 'arriving' || cat.state === 'leaving') {
      variant = Math.floor(cat.animationTimer / 200) % 2 === 0 ? 'moving1' : 'moving2';
    }

    const sprite = this.spriteLoader.getSprite(cat.data.id, variant);
    drawSpriteCentered(ctx, sprite, cat.pos.x, cat.pos.y, () => {
      ctx.beginPath();
      ctx.arc(cat.pos.x, cat.pos.y, 34, 0, Math.PI * 2);
      ctx.fillStyle = rgb(cat.data.color);
      ctx.fill();
      ctx.strokeStyle = '#433028';
      ctx.stroke();
      drawText(ctx, '😺', cat.pos.x, cat.pos.y, 32, '#000', 'center');
    });

    drawText(ctx, cat.data.name, cat.pos.x, cat.pos.y + 50, 15, '#5f3f2c', 'center');

    if (cat.state === 'waiting') {
      const bubble = this.spriteLoader.getSprite('thought_bubble', 'single');
      if (bubble) {
        ctx.drawImage(bubble, cat.pos.x + 58 - bubble.width / 2, cat.pos.y - 36 - bubble.height / 2);
      } else {
        ctx.beginPath();
        ctx.arc(cat.pos.x + 58, cat.pos.y - 36, 24, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();
        ctx.strokeStyle = '#8a8a8a';
        ctx.stroke();
      }

      drawText(ctx, 'Tea', cat.pos.x + 58, cat.pos.y - 34, 13, '#547147', 'center');

      drawRect(ctx, cat.pos.x - 30, cat.pos.y + 62, 60, 6, '#949494');
      const barColor = cat.patience > 60 ? '#65b765' : cat.patience > 30 ? '#edc256' : '#e56f6f';
      drawRect(ctx, cat.pos.x - 30, cat.pos.y + 62, (cat.patience / 100) * 60, 6, barColor);
    }
  }

  private drawTooltip(ctx: CanvasRenderingContext2D, origin: Point, title: string, lines: string[]): void {
    const width = 320;
    const height = 22 + (lines.length + 1) * 18;
    drawRect(ctx, origin.x, origin.y, width, height, 'rgba(255, 255, 245, 0.96)', 'rgba(107, 79, 55, 0.9)');
    drawText(ctx, title, origin.x + 10, origin.y + 16, 15, '#4a3428');
    for (let i = 0; i < lines.length; i += 1) {
      drawText(ctx, lines[i], origin.x + 10, origin.y + 35 + i * 18, 13, '#5b463a');
    }
  }

  private circleContains(point: Point, center: Point, radius: number): boolean {
    const dx = point.x - center.x;
    const dy = point.y - center.y;
    return dx * dx + dy * dy <= radius * radius;
  }

  private hotWaterContains(point: Point): boolean {
    return inRect(point, { x: this.hotWater.pos.x - 40, y: this.hotWater.pos.y - 40, w: 80, h: 80 });
  }

  private kettleContains(point: Point): boolean {
    return inRect(point, { x: this.teaKettle.pos.x - 50, y: this.teaKettle.pos.y - 50, w: 100, h: 100 });
  }

  private chaHaiContains(point: Point): boolean {
    return inRect(point, { x: this.chaHai.pos.x - 35, y: this.chaHai.pos.y - 30, w: 70, h: 60 });
  }

  private teaGodContains(point: Point): boolean {
    return inRect(point, {
      x: this.teaGod.pos.x - this.teaGod.width / 2,
      y: this.teaGod.pos.y - this.teaGod.height / 2,
      w: this.teaGod.width,
      h: this.teaGod.height,
    });
  }

  private catContains(cat: CatVisitor, point: Point): boolean {
    return inRect(point, { x: cat.pos.x - 40, y: cat.pos.y - 40, w: 80, h: 80 });
  }
}

export function createScene(sceneType: SceneType, deps: SceneDeps): Scene {
  if (sceneType === 'loading') {
    return new LoadingScene(deps.width, deps.height, deps.loading);
  }
  if (sceneType === 'menu') {
    return new MenuScene(deps.width, deps.height, deps.gameState, deps.spriteLoader, deps.soundManager);
  }
  if (sceneType === 'game') {
    return new GameScene(deps.width, deps.height, deps.data, deps.gameState, deps.spriteLoader, deps.soundManager);
  }
  if (sceneType === 'stats') {
    return new StatsScene(deps.width, deps.height, deps.gameState, deps.soundManager);
  }
  return new TitleScene(deps.width, deps.height);
}
