const WINDOW_WIDTH = 1024;
const WINDOW_HEIGHT = 768;
const CELL_SIZE = 6;
const GRID_W = Math.floor(WINDOW_WIDTH / CELL_SIZE);
const GRID_H = Math.floor(WINDOW_HEIGHT / CELL_SIZE);

const GRAVITY = 60;
const POUR_RATE = 6;
const POUR_RADIUS = 3;
const PARTICLE_RADIUS = 4;
const PARTICLE_DAMP = 0.992;
const PARTICLES_PER_POUR = 8;
const MAX_PARTICLES = 800;

const LEAF_LENGTH = 20;
const LEAF_THICKNESS = 5;
const LEAF_RADIUS = 8;
const CUP_WIDTH = 420;
const CUP_HEIGHT = 500;
const CUP_WALL = 10;
const CUP_MARGIN_BOTTOM = 40;

const WATER_COLOR: [number, number, number] = [90, 140, 220];
const TEA_COLOR: [number, number, number] = [160, 110, 50];
const LEAF_COLOR_DRY: [number, number, number] = [40, 90, 30];
const LEAF_COLOR_WET: [number, number, number] = [160, 110, 50];

interface WaterParticle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  dye: number;
}

interface LeafParticle {
  x: number;
  y: number;
  angle: number;
  length: number;
  strength: number;
  vx: number;
  vy: number;
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

export class FluidSimulation {
  readonly water = new Float32Array(GRID_W * GRID_H);
  readonly dye = new Float32Array(GRID_W * GRID_H);
  readonly u = new Float32Array(GRID_W * GRID_H);
  readonly v = new Float32Array(GRID_W * GRID_H);

  readonly particles: WaterParticle[] = [];
  readonly leaves: LeafParticle[] = [];

  readonly invCell = 1 / CELL_SIZE;
  readonly cupCx: number;
  readonly cupCy: number;
  readonly cupRadius: number;

  constructor() {
    this.cupCx = WINDOW_WIDTH * 0.5;
    this.cupCy = WINDOW_HEIGHT - CUP_MARGIN_BOTTOM - CUP_HEIGHT * 0.5;
    this.cupRadius = Math.min(CUP_WIDTH, CUP_HEIGHT) * 0.5;
  }

  addLeaf(x: number, y: number): void {
    this.leaves.push({
      x,
      y,
      angle: Math.random() * Math.PI,
      length: LEAF_LENGTH * (0.7 + Math.random() * 0.5),
      strength: 1,
      vx: 0,
      vy: 0,
    });
  }

  addWater(gx: number, gy: number, amount: number): void {
    const x0 = Math.max(0, gx - POUR_RADIUS);
    const x1 = Math.min(GRID_W - 1, gx + POUR_RADIUS);
    const y0 = Math.max(0, gy - POUR_RADIUS);
    const y1 = Math.min(GRID_H - 1, gy + POUR_RADIUS);

    for (let y = y0; y <= y1; y += 1) {
      for (let x = x0; x <= x1; x += 1) {
        const idx = y * GRID_W + x;
        this.water[idx] += amount;
        this.v[idx] += GRAVITY * 0.08;
      }
    }

    if (this.particles.length < MAX_PARTICLES) {
      const cx = gx * CELL_SIZE + CELL_SIZE * 0.5;
      const cy = gy * CELL_SIZE + CELL_SIZE * 0.5;
      for (let i = 0; i < PARTICLES_PER_POUR; i += 1) {
        if (this.particles.length >= MAX_PARTICLES) {
          break;
        }
        this.particles.push({
          x: cx + (Math.random() * 2 - 1) * CELL_SIZE,
          y: cy + (Math.random() * 2 - 1) * CELL_SIZE,
          vx: 0,
          vy: 20 + Math.random() * 20,
          radius: PARTICLE_RADIUS,
          dye: 0,
        });
      }
    }
  }

  step(dt: number): void {
    this.stepParticles(dt);
    this.rebuildGrid();
    this.applyCupBounds();
    this.updateLeaves(dt);
  }

  private stepParticles(dt: number): void {
    const innerR = Math.max(0, this.cupRadius - CUP_WALL - PARTICLE_RADIUS);
    for (const p of this.particles) {
      p.vy += GRAVITY * dt * 0.8;
      p.vx *= PARTICLE_DAMP;
      p.vy *= PARTICLE_DAMP;
      p.x += p.vx * dt;
      p.y += p.vy * dt;

      const dx = p.x - this.cupCx;
      const dy = p.y - this.cupCy;
      const dist = Math.hypot(dx, dy);
      if (dist > innerR && dist > 0) {
        const nx = dx / dist;
        const ny = dy / dist;
        p.x = this.cupCx + nx * innerR;
        p.y = this.cupCy + ny * innerR;
        const vn = p.vx * nx + p.vy * ny;
        if (vn > 0) {
          p.vx -= 1.65 * vn * nx;
          p.vy -= 1.65 * vn * ny;
        }
      }
    }
  }

  private rebuildGrid(): void {
    this.water.fill(0);
    this.dye.fill(0);
    this.u.fill(0);
    this.v.fill(0);
    const count = new Float32Array(GRID_W * GRID_H);

    for (const p of this.particles) {
      const gx = Math.floor(p.x * this.invCell);
      const gy = Math.floor(p.y * this.invCell);
      if (gx < 0 || gx >= GRID_W || gy < 0 || gy >= GRID_H) {
        continue;
      }
      const idx = gy * GRID_W + gx;
      this.water[idx] += 1;
      this.dye[idx] += p.dye;
      this.u[idx] += p.vx;
      this.v[idx] += p.vy;
      count[idx] += 1;
    }

    for (let i = 0; i < count.length; i += 1) {
      if (count[i] > 0) {
        this.u[i] /= count[i];
        this.v[i] /= count[i];
        this.dye[i] /= count[i];
      }
    }
  }

  private applyCupBounds(): void {
    const innerR = Math.max(0, this.cupRadius - CUP_WALL);
    const innerR2 = innerR * innerR;
    for (let y = 0; y < GRID_H; y += 1) {
      for (let x = 0; x < GRID_W; x += 1) {
        const px = (x + 0.5) * CELL_SIZE;
        const py = (y + 0.5) * CELL_SIZE;
        const dx = px - this.cupCx;
        const dy = py - this.cupCy;
        const idx = y * GRID_W + x;
        if (dx * dx + dy * dy > innerR2) {
          this.water[idx] = 0;
          this.dye[idx] = 0;
          this.u[idx] = 0;
          this.v[idx] = 0;
        }
      }
    }
  }

  private updateLeaves(dt: number): void {
    const innerR = Math.max(0, this.cupRadius - CUP_WALL - LEAF_RADIUS);
    for (const leaf of this.leaves) {
      const gx = clamp(Math.floor(leaf.x * this.invCell), 0, GRID_W - 1);
      const gy = clamp(Math.floor(leaf.y * this.invCell), 0, GRID_H - 1);
      const idx = gy * GRID_W + gx;
      leaf.vy += GRAVITY * 0.35 * dt;
      leaf.vx = (leaf.vx + this.u[idx] * dt * 0.6) * 0.96;
      leaf.vy = (leaf.vy + this.v[idx] * dt * 0.6) * 0.96;
      leaf.x += leaf.vx;
      leaf.y += leaf.vy;

      const dx = leaf.x - this.cupCx;
      const dy = leaf.y - this.cupCy;
      const dist = Math.hypot(dx, dy);
      if (dist > innerR && dist > 0) {
        const nx = dx / dist;
        const ny = dy / dist;
        leaf.x = this.cupCx + nx * innerR;
        leaf.y = this.cupCy + ny * innerR;
      }

      if (this.water[idx] > 0.15) {
        leaf.strength = Math.max(0, leaf.strength - 0.6 * dt);
        for (const p of this.particles) {
          const pdx = p.x - leaf.x;
          const pdy = p.y - leaf.y;
          if (pdx * pdx + pdy * pdy <= 400) {
            p.dye = Math.min(1, p.dye + 1.4 * dt);
          }
        }
      }
    }
  }
}

export class FluidRenderer {
  private readonly fieldCanvas: HTMLCanvasElement;
  private readonly fieldCtx: CanvasRenderingContext2D;

  constructor(private readonly sim: FluidSimulation) {
    this.fieldCanvas = document.createElement('canvas');
    this.fieldCanvas.width = GRID_W;
    this.fieldCanvas.height = GRID_H;
    const context = this.fieldCanvas.getContext('2d');
    if (!context) {
      throw new Error('Failed to create fluid field context');
    }
    this.fieldCtx = context;
  }

  draw(ctx: CanvasRenderingContext2D): void {
    const imageData = this.fieldCtx.createImageData(GRID_W, GRID_H);
    for (let i = 0; i < GRID_W * GRID_H; i += 1) {
      const waterIntensity = clamp(this.sim.water[i] * 1.8, 0, 1);
      const dyeIntensity = clamp(this.sim.dye[i] * 3, 0, 1);
      const base = i * 4;
      imageData.data[base] = clamp(WATER_COLOR[0] * waterIntensity + TEA_COLOR[0] * dyeIntensity + 15, 0, 255);
      imageData.data[base + 1] = clamp(WATER_COLOR[1] * waterIntensity + TEA_COLOR[1] * dyeIntensity + 15, 0, 255);
      imageData.data[base + 2] = clamp(WATER_COLOR[2] * waterIntensity + TEA_COLOR[2] * dyeIntensity + 15, 0, 255);
      imageData.data[base + 3] = 255;
    }

    this.fieldCtx.putImageData(imageData, 0, 0);
    ctx.drawImage(this.fieldCanvas, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT);

    for (const p of this.sim.particles) {
      const gx = Math.floor(p.x * this.sim.invCell);
      const gy = Math.floor(p.y * this.sim.invCell);
      let dye = 0;
      if (gx >= 0 && gx < GRID_W && gy >= 0 && gy < GRID_H) {
        dye = this.sim.dye[gy * GRID_W + gx];
      }
      const t = Math.min(1, dye * 1.5);
      const r = Math.floor(WATER_COLOR[0] * (1 - t) + TEA_COLOR[0] * t);
      const g = Math.floor(WATER_COLOR[1] * (1 - t) + TEA_COLOR[1] * t);
      const b = Math.floor(WATER_COLOR[2] * (1 - t) + TEA_COLOR[2] * t);
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgb(${r},${g},${b})`;
      ctx.fill();
    }

    for (const leaf of this.sim.leaves) {
      const t = 1 - leaf.strength;
      const r = Math.floor(LEAF_COLOR_DRY[0] * (1 - t) + LEAF_COLOR_WET[0] * t);
      const g = Math.floor(LEAF_COLOR_DRY[1] * (1 - t) + LEAF_COLOR_WET[1] * t);
      const b = Math.floor(LEAF_COLOR_DRY[2] * (1 - t) + LEAF_COLOR_WET[2] * t);
      const dx = Math.cos(leaf.angle) * leaf.length * 0.5;
      const dy = Math.sin(leaf.angle) * leaf.length * 0.5;
      ctx.beginPath();
      ctx.moveTo(leaf.x - dx, leaf.y - dy);
      ctx.lineTo(leaf.x + dx, leaf.y + dy);
      ctx.strokeStyle = `rgb(${r},${g},${b})`;
      ctx.lineWidth = LEAF_THICKNESS;
      ctx.stroke();
    }

    this.drawCup(ctx);
  }

  private drawCup(ctx: CanvasRenderingContext2D): void {
    ctx.beginPath();
    ctx.arc(this.sim.cupCx, this.sim.cupCy, this.sim.cupRadius, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgb(200,200,210)';
    ctx.lineWidth = CUP_WALL;
    ctx.stroke();

    const eraseH = Math.max(4, CUP_WALL + 90);
    ctx.fillStyle = 'rgb(12,16,22)';
    ctx.fillRect(this.sim.cupCx - this.sim.cupRadius, this.sim.cupCy - this.sim.cupRadius - eraseH / 2, this.sim.cupRadius * 2, eraseH);
  }
}

export class FluidLoadingBackground {
  private readonly sim = new FluidSimulation();
  private readonly renderer = new FluidRenderer(this.sim);
  private readonly pourGx = Math.floor((WINDOW_WIDTH * 0.5) / CELL_SIZE);
  private readonly pourGy: number;

  constructor() {
    const pourPx = this.sim.cupCy - this.sim.cupRadius + CUP_WALL + 2;
    this.pourGy = Math.floor(pourPx / CELL_SIZE);

    for (let i = 0; i < 50; i += 1) {
      this.sim.addLeaf(
        WINDOW_WIDTH * (0.3 + Math.random() * 0.4),
        WINDOW_HEIGHT * (0.5 + Math.random() * 0.4),
      );
    }
  }

  update(dtMs: number): void {
    const dt = dtMs / 1000;
    this.sim.addWater(this.pourGx, this.pourGy, POUR_RATE * dt);
    this.sim.step(dt);
  }

  draw(ctx: CanvasRenderingContext2D): void {
    ctx.fillStyle = 'rgb(12,16,22)';
    ctx.fillRect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT);
    this.renderer.draw(ctx);
  }
}