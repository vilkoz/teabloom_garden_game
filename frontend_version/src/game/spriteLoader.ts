import type { SpriteConfig } from './types';
import { appUrl } from './paths';

type SpriteMap = Map<string, Map<string, HTMLCanvasElement>>;

function createCanvas(width: number, height: number): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  return canvas;
}

async function loadImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error(`Failed to load image: ${url}`));
    image.src = url;
  });
}

function removeBlackBackground(ctx: CanvasRenderingContext2D, width: number, height: number): void {
  const imageData = ctx.getImageData(0, 0, width, height);
  const data = imageData.data;
  for (let i = 0; i < data.length; i += 4) {
    if (data[i] < 10 && data[i + 1] < 10 && data[i + 2] < 10) {
      data[i + 3] = 0;
    }
  }
  ctx.putImageData(imageData, 0, 0);
}

function parseVariant(variant: string): string {
  return variant.split(':')[0].trim();
}

export class SpriteLoader {
  private readonly sprites: SpriteMap = new Map();

  async loadAll(configs: SpriteConfig[], messageCallback?: (message: string) => void): Promise<void> {
    for (const cfg of configs) {
      await this.loadGrid(cfg, messageCallback);
    }
    messageCallback?.('All sprite loading complete!');
  }

  getSprite(entityName: string, variantName: string): HTMLCanvasElement | null {
    const entity = this.sprites.get(entityName);
    if (!entity) {
      return null;
    }
    return entity.get(variantName) ?? null;
  }

  hasSprite(entityName: string, variantName?: string): boolean {
    const entity = this.sprites.get(entityName);
    if (!entity) {
      return false;
    }
    if (!variantName) {
      return true;
    }
    return entity.has(variantName);
  }

  private async loadGrid(cfg: SpriteConfig, messageCallback?: (message: string) => void): Promise<void> {
    const imageUrl = appUrl(`assets/images/grids/${cfg.name}_grid.png`);
    const [spriteWidth, spriteHeight] = cfg.sprite_size;
    const [renderWidth, renderHeight] = cfg.render_size ?? cfg.sprite_size;

    try {
      const image = await loadImage(imageUrl);
      if (!this.sprites.has(cfg.name)) {
        this.sprites.set(cfg.name, new Map());
      }

      const entity = this.sprites.get(cfg.name)!;

      for (let idx = 0; idx < cfg.variants.length; idx += 1) {
        const row = Math.floor(idx / cfg.grid_cols);
        const col = idx % cfg.grid_cols;

        const sx = cfg.border_offset[0] + col * (spriteWidth + cfg.grid_offset[0]);
        const sy = cfg.border_offset[1] + row * (spriteHeight + cfg.grid_offset[1]);

        const extractCanvas = createCanvas(spriteWidth, spriteHeight);
        const extractCtx = extractCanvas.getContext('2d');
        if (!extractCtx) {
          continue;
        }

        extractCtx.drawImage(image, sx, sy, spriteWidth, spriteHeight, 0, 0, spriteWidth, spriteHeight);
        removeBlackBackground(extractCtx, spriteWidth, spriteHeight);

        let finalCanvas = extractCanvas;
        if (renderWidth !== spriteWidth || renderHeight !== spriteHeight) {
          const scaled = createCanvas(renderWidth, renderHeight);
          const scaledCtx = scaled.getContext('2d');
          if (scaledCtx) {
            scaledCtx.imageSmoothingEnabled = true;
            scaledCtx.drawImage(extractCanvas, 0, 0, renderWidth, renderHeight);
            finalCanvas = scaled;
          }
        }

        entity.set(parseVariant(cfg.variants[idx]), finalCanvas);
      }

      messageCallback?.(`Loaded ${cfg.variants.length} sprites for '${cfg.name}'`);
    } catch {
      messageCallback?.(`⚠️ Grid not found: ${imageUrl}`);
      this.createFallbackSprites(cfg);
    }
  }

  private createFallbackSprites(cfg: SpriteConfig): void {
    if (!this.sprites.has(cfg.name)) {
      this.sprites.set(cfg.name, new Map());
    }

    const entity = this.sprites.get(cfg.name)!;
    const [w, h] = cfg.render_size ?? cfg.sprite_size;

    for (const variant of cfg.variants) {
      const variantName = parseVariant(variant);
      const canvas = createCanvas(w, h);
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        continue;
      }

      ctx.fillStyle = '#c9c9c9';
      ctx.fillRect(0, 0, w, h);
      ctx.strokeStyle = '#666';
      ctx.strokeRect(0, 0, w, h);
      ctx.fillStyle = '#222';
      ctx.font = '12px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(variantName, w / 2, h / 2);
      entity.set(variantName, canvas);
    }
  }
}