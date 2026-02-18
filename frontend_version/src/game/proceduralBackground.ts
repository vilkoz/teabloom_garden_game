interface Layer {
  baseAmplitude: number;
  amplitude: number;
  freq: number;
  phase: number;
  baseline: number;
  shade: [number, number, number];
  phaseSpeed: number;
  ampJitter: number;
  depth: number;
}

interface Flower {
  x: number;
  y: number;
  size: number;
  speed: number;
  phase: number;
  color: [number, number, number];
  depth: number;
  layerIdx: number;
  drawX: number;
  drawY: number;
}

interface Heart {
  x: number;
  y: number;
  size: number;
  vy: number;
  bob: number;
  color: [number, number, number];
  depth: number;
  t: number;
}

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

function rgb(color: [number, number, number], alpha = 1): string {
  return `rgba(${color[0]}, ${color[1]}, ${color[2]}, ${alpha})`;
}

export class ProceduralBackground {
  private readonly random: () => number;
  private readonly layers: Layer[] = [];
  private readonly flowers: Flower[] = [];
  private readonly hearts: Heart[] = [];
  private frame = 0;

  constructor(
    private readonly width: number,
    private readonly height: number,
    seed = 0,
  ) {
    let state = seed >>> 0;
    this.random = () => {
      state ^= state << 13;
      state ^= state >>> 17;
      state ^= state << 5;
      return (state >>> 0) / 4294967296;
    };

    this.initLayers();
    this.spawnFlowers(300);
    this.spawnHearts(500);
  }

  update(dtMs: number): void {
    const dt = dtMs > 1 ? dtMs / 1000 : dtMs;
    this.frame += dt;

    for (let i = 0; i < this.layers.length; i += 1) {
      const layer = this.layers[i];
      layer.phase += dt * layer.phaseSpeed;
      const wobble = Math.sin(this.frame * (0.3 + i * 0.1) + layer.phase) * layer.ampJitter;
      layer.amplitude = layer.baseAmplitude + wobble;
    }

    for (const flower of this.flowers) {
      flower.phase += dt * flower.speed;
      const bob = Math.sin(flower.phase) * (flower.size * 0.08);
      const layer = this.layers[flower.layerIdx] ?? this.layers[0];
      const syncV = Math.sin(layer.phase + flower.phase * 0.5) * layer.amplitude;
      const syncX = Math.sin(layer.phase * 0.6 + flower.phase * 0.4) * layer.ampJitter;
      flower.drawX = flower.x + syncX;
      flower.drawY = flower.y + bob + syncV;
    }

    for (const heart of this.hearts) {
      heart.t += dt;
      heart.y += heart.vy * dt;
      heart.x += Math.sin(heart.t * heart.bob) * 8 * dt;
      if (heart.y + heart.size < -20) {
        heart.x = this.random() * this.width;
        heart.y = lerp(this.height * 0.85, this.height * 1.05, this.random());
        heart.vy = -lerp(8, 24, this.random());
        heart.t = 0;
      }
    }
  }

  draw(ctx: CanvasRenderingContext2D): void {
    this.drawVerticalGradient(ctx, [245, 238, 230], [200, 240, 255]);

    const items: Array<{ depth: number; type: 'layer' | 'flower' | 'heart'; payload: unknown }> = [];
    for (let i = 0; i < this.layers.length; i += 1) {
      items.push({ depth: this.layers[i].depth, type: 'layer', payload: i });
    }
    for (const flower of this.flowers) {
      items.push({ depth: flower.depth, type: 'flower', payload: flower });
    }
    for (const heart of this.hearts) {
      items.push({ depth: heart.depth, type: 'heart', payload: heart });
    }

    items.sort((a, b) => b.depth - a.depth);
    for (const item of items) {
      if (item.type === 'layer') {
        this.drawLayer(ctx, this.layers[item.payload as number]);
      } else if (item.type === 'flower') {
        this.drawFlower(ctx, item.payload as Flower);
      } else {
        this.drawHeart(ctx, item.payload as Heart);
      }
    }
  }

  private initLayers(): void {
    const templates = [
      { amplitude: 40, freq: 1.2, color: [170, 123, 105] as [number, number, number], depth: 250 },
      { amplitude: 70, freq: 0.9, color: [181, 129, 123] as [number, number, number], depth: 500 },
      { amplitude: 110, freq: 0.6, color: [124, 60, 50] as [number, number, number], depth: 750 },
    ];

    for (let i = 0; i < templates.length; i += 1) {
      const t = templates[i];
      const shade: [number, number, number] = [
        Math.max(0, t.color[0] + Math.floor(lerp(-8, 8, this.random()))),
        Math.max(0, t.color[1] + Math.floor(lerp(-12, 12, this.random()))),
        Math.max(0, t.color[2] + Math.floor(lerp(-8, 8, this.random()))),
      ];

      this.layers.push({
        baseAmplitude: t.amplitude,
        amplitude: t.amplitude,
        freq: t.freq * (1 + lerp(-0.08, 0.08, this.random())),
        phase: this.random() * Math.PI * 2,
        baseline: Math.floor(this.height * (0.7 - i * 0.15)),
        shade,
        phaseSpeed: 0.12 + i * 0.03,
        ampJitter: Math.max(2, Math.floor(t.amplitude * 0.06)),
        depth: t.depth,
      });
    }
  }

  private spawnFlowers(count: number): void {
    for (let i = 0; i < count; i += 1) {
      const depth = Math.floor(lerp(200, 1000, this.random()));
      this.flowers.push({
        x: this.random() * this.width,
        y: lerp(this.height * 0.45, this.height * 0.88, this.random()),
        size: lerp(8, 24, this.random()),
        speed: lerp(0.6, 1.6, this.random()),
        phase: this.random() * Math.PI * 2,
        color: [Math.floor(lerp(200, 255, this.random())), Math.floor(lerp(120, 220, this.random())), Math.floor(lerp(120, 255, this.random()))],
        depth,
        layerIdx: this.findLayerForDepth(depth),
        drawX: 0,
        drawY: 0,
      });
    }
  }

  private spawnHearts(count: number): void {
    for (let i = 0; i < count; i += 1) {
      this.hearts.push({
        x: this.random() * this.width,
        y: lerp(this.height * 0.6, this.height * 0.95, this.random()),
        size: lerp(12, 36, this.random()),
        vy: -lerp(8, 24, this.random()),
        bob: lerp(0.8, 2, this.random()),
        color: [255, Math.floor(lerp(80, 200, this.random())), Math.floor(lerp(120, 255, this.random()))],
        depth: Math.floor(lerp(200, 1000, this.random())),
        t: 0,
      });
    }
  }

  private drawVerticalGradient(ctx: CanvasRenderingContext2D, top: [number, number, number], bottom: [number, number, number]): void {
    const gradient = ctx.createLinearGradient(0, 0, 0, this.height);
    gradient.addColorStop(0, rgb(top));
    gradient.addColorStop(1, rgb(bottom));
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, this.width, this.height);
  }

  private drawLayer(ctx: CanvasRenderingContext2D, layer: Layer): void {
    const step = 6;
    ctx.beginPath();
    ctx.moveTo(0, this.height);
    for (let x = 0; x <= this.width + step; x += step) {
      const nx = x / this.width;
      const y = layer.baseline + layer.amplitude * Math.sin(nx * layer.freq * 2 * Math.PI + layer.phase);
      ctx.lineTo(x, y);
    }
    ctx.lineTo(this.width, this.height);
    ctx.closePath();
    ctx.fillStyle = rgb(layer.shade);
    ctx.fill();
  }

  private drawHeart(ctx: CanvasRenderingContext2D, heart: Heart): void {
    const depthModifier = 0.01;
    const scale = 1 / (Math.max(1, heart.depth) * depthModifier);
    const size = Math.max(1, Math.floor(heart.size * scale));
    const x = heart.x;
    const y = heart.y;
    const r = size * 0.5;

    ctx.fillStyle = rgb(heart.color);
    ctx.beginPath();
    ctx.arc(x - r, y - r * 0.2, r, 0, Math.PI * 2);
    ctx.arc(x + r, y - r * 0.2, r, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(x - size, y);
    ctx.lineTo(x + size, y);
    ctx.lineTo(x, y + size * 1.6);
    ctx.closePath();
    ctx.fill();
  }

  private drawFlower(ctx: CanvasRenderingContext2D, flower: Flower): void {
    const depthModifier = 0.01;
    const scale = 1 / (Math.max(1, flower.depth) * depthModifier);
    const size = Math.max(1, Math.floor(flower.size * scale));
    const x = flower.drawX || flower.x;
    const y = flower.drawY || flower.y;

    const petalCount = 5;
    for (let i = 0; i < petalCount; i += 1) {
      const angle = (i * Math.PI * 2) / petalCount;
      const px = x + Math.cos(angle) * size * 0.7;
      const py = y + Math.sin(angle) * size * 0.7;
      ctx.beginPath();
      ctx.ellipse(px, py, size * 0.55, size * 0.3, -angle, 0, Math.PI * 2);
      ctx.fillStyle = rgb([
        Math.max(0, flower.color[0] - 30),
        Math.max(0, flower.color[1] - 30),
        Math.max(0, flower.color[2] - 30),
      ]);
      ctx.fill();
    }

    ctx.beginPath();
    ctx.arc(x, y, size * 0.45, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,220,80,1)';
    ctx.fill();
  }

  private findLayerForDepth(depth: number): number {
    for (let i = 0; i < this.layers.length; i += 1) {
      if (this.layers[i].depth >= depth) {
        return i;
      }
    }
    return this.layers.length - 1;
  }
}