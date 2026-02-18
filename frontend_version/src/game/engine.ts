import { createScene } from './scenes';
import { SoundManager } from './soundManager';
import { SpriteLoader } from './spriteLoader';
import { GameStateManager } from './state';
import type { AssetBundle, GameData, Point, Scene, SceneResult, SceneType } from './types';

export class TeaGardenWebGame {
  private readonly ctx: CanvasRenderingContext2D;
  private readonly gameState: GameStateManager;
  private readonly spriteLoader: SpriteLoader;
  private readonly soundManager: SoundManager;
  private readonly loading = { messages: [] as string[], done: false, error: false };
  private currentSceneType: SceneType = 'loading';
  private currentScene: Scene;
  private running = false;
  private raf = 0;
  private lastTime = 0;

  constructor(
    private readonly canvas: HTMLCanvasElement,
    private readonly data: GameData & AssetBundle,
    private readonly setStatus: (status: string) => void,
  ) {
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      throw new Error('Canvas 2D context is unavailable');
    }

    this.ctx = ctx;
    this.gameState = new GameStateManager(data.teas, data.cats);
    this.spriteLoader = new SpriteLoader();
    this.soundManager = new SoundManager();
    this.currentScene = createScene('loading', {
      width: this.canvas.width,
      height: this.canvas.height,
      data: this.data,
      gameState: this.gameState,
      spriteLoader: this.spriteLoader,
      soundManager: this.soundManager,
      loading: this.loading,
    });

    this.handlePointerDown = this.handlePointerDown.bind(this);
    this.handlePointerMove = this.handlePointerMove.bind(this);
    this.handlePointerUp = this.handlePointerUp.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.tick = this.tick.bind(this);
  }

  start(): void {
    if (this.running) {
      return;
    }
    this.running = true;
    this.lastTime = performance.now();
    this.bindEvents();
    this.setStatus('Loading sprites and sounds...');
    void this.bootAssets();
    this.raf = requestAnimationFrame(this.tick);
  }

  stop(): void {
    this.running = false;
    cancelAnimationFrame(this.raf);
    this.unbindEvents();
    this.gameState.saveProgress();
  }

  private tick(now: number): void {
    if (!this.running) {
      return;
    }

    const dt = Math.min(now - this.lastTime, 50);
    this.lastTime = now;

    const updateResult = this.currentScene.update(dt);
    this.consumeResult(updateResult);

    this.currentScene.draw(this.ctx);
    this.raf = requestAnimationFrame(this.tick);
  }

  private handlePointerDown(event: PointerEvent): void {
    this.soundManager.unlock();
    this.canvas.setPointerCapture(event.pointerId);
    const point = this.toCanvasPoint(event);
    this.consumeResult(this.currentScene.pointerDown(point));
  }

  private handlePointerMove(event: PointerEvent): void {
    const point = this.toCanvasPoint(event);
    this.currentScene.pointerMove(point);
  }

  private handlePointerUp(event: PointerEvent): void {
    const point = this.toCanvasPoint(event);
    this.consumeResult(this.currentScene.pointerUp(point));
  }

  private handleKeyDown(event: KeyboardEvent): void {
    if (!this.currentScene.keyDown) {
      return;
    }

    this.consumeResult(this.currentScene.keyDown(event.key));
  }

  private consumeResult(result: SceneResult): void {
    if (!result) {
      return;
    }

    if ('quit' in result && result.quit) {
      this.setStatus('Game loop stopped (Quit clicked)');
      this.stop();
      return;
    }

    if ('changeScene' in result) {
      this.currentSceneType = result.changeScene;
      this.currentScene = createScene(this.currentSceneType, {
        width: this.canvas.width,
        height: this.canvas.height,
        data: this.data,
        gameState: this.gameState,
        spriteLoader: this.spriteLoader,
        soundManager: this.soundManager,
        loading: this.loading,
      });
      this.setStatus(`Scene: ${this.currentSceneType}`);
    }
  }

  private async bootAssets(): Promise<void> {
    this.loading.messages.push('Loading game sprites...');

    try {
      await this.spriteLoader.loadAll(this.data.sprites, (message) => {
        this.loading.messages.push(message);
      });

      this.loading.messages.push('Loading sounds...');
      await this.soundManager.warmup();
      this.loading.messages.push('All sounds loaded (missing files are skipped).');
      this.loading.messages.push('');
      this.loading.messages.push('Press any key to continue...');
      this.loading.done = true;
      this.setStatus('Assets loaded');
    } catch (error) {
      this.loading.error = true;
      this.loading.done = true;
      const message = error instanceof Error ? error.message : 'Asset load failed';
      this.loading.messages.push(`Error loading assets: ${message}`);
      this.loading.messages.push('Press any key to continue...');
      this.setStatus('Asset loading failed');
    }
  }

  private toCanvasPoint(event: PointerEvent): Point {
    const rect = this.canvas.getBoundingClientRect();
    const sx = this.canvas.width / rect.width;
    const sy = this.canvas.height / rect.height;
    return {
      x: (event.clientX - rect.left) * sx,
      y: (event.clientY - rect.top) * sy,
    };
  }

  private bindEvents(): void {
    this.canvas.addEventListener('pointerdown', this.handlePointerDown);
    this.canvas.addEventListener('pointermove', this.handlePointerMove);
    this.canvas.addEventListener('pointerup', this.handlePointerUp);
    window.addEventListener('keydown', this.handleKeyDown);
  }

  private unbindEvents(): void {
    this.canvas.removeEventListener('pointerdown', this.handlePointerDown);
    this.canvas.removeEventListener('pointermove', this.handlePointerMove);
    this.canvas.removeEventListener('pointerup', this.handlePointerUp);
    window.removeEventListener('keydown', this.handleKeyDown);
  }
}