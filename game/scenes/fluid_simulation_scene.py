import math
import os
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Tuple

import pygame

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover
    raise SystemExit("This simulation requires numpy. Please install it.") from exc


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 720
CELL_SIZE = 6
GRID_W = WINDOW_WIDTH // CELL_SIZE
GRID_H = WINDOW_HEIGHT // CELL_SIZE
FPS = 60

GRAVITY = 60.0
VELOCITY_DAMP = 0.985
DIFFUSE_WATER = 0
DIFFUSE_DYE = 0
DYE_DECAY = 0.99999
POUR_RATE = 6.0
POUR_RADIUS = 3

PARTICLE_RADIUS = 4
PARTICLE_RESTITUTION = 0.65
PARTICLE_DAMP = 0.992
PARTICLES_PER_POUR = 10
MAX_PARTICLES = 800

LEAF_LENGTH = 20
LEAF_THICKNESS = 5
LEAF_COLOR_DRY = (40, 90, 30)
LEAF_COLOR_WET = (160, 110, 50)
LEAF_RADIUS = 8
LEAF_RESTITUTION = 0.0
LEAF_FRICTION = 0.85
LEAF_SETTLE_PULL = 8.0

TEA_COLOR = np.array([160, 110, 50], dtype=np.float32)
WATER_COLOR = np.array([90, 140, 220], dtype=np.float32)
BACKGROUND = (12, 16, 22)

PRESSURE_STIFFNESS = 18.0
PRESSURE_REST = 0.08
MIN_WATER = 0.02

CUP_WIDTH = 420
CUP_HEIGHT = 500
CUP_WALL = 10
CUP_MARGIN_BOTTOM = 40
CUP_COLOR = (200, 200, 210)


@dataclass
class LeafParticle:
    x: float
    y: float
    angle: float
    length: float
    strength: float
    vx: float = 0.0
    vy: float = 0.0

    def as_segment(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        dx = math.cos(self.angle) * self.length * 0.5
        dy = math.sin(self.angle) * self.length * 0.5
        return (self.x - dx, self.y - dy), (self.x + dx, self.y + dy)


@dataclass
class WaterParticle:
    x: float
    y: float
    vx: float
    vy: float
    radius: float
    dye: float


class FluidSimulation:
    def __init__(self, grid_w: int, grid_h: int):
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.inv_cell = 1.0 / CELL_SIZE

        self.u = np.zeros((grid_h, grid_w), dtype=np.float32)
        self.v = np.zeros((grid_h, grid_w), dtype=np.float32)
        self.water = np.zeros((grid_h, grid_w), dtype=np.float32)
        self.dye = np.zeros((grid_h, grid_w), dtype=np.float32)

        self._water_next = np.zeros_like(self.water)
        self._dye_next = np.zeros_like(self.dye)

        grid_y, grid_x = np.mgrid[0:grid_h, 0:grid_w]
        self.grid_x = grid_x.astype(np.float32)
        self.grid_y = grid_y.astype(np.float32)

        self.cup_rect = self._build_cup_rect()
        self.cup_mask = self._build_cup_mask()

        self.leaves: List[LeafParticle] = []
        self.particles: List[WaterParticle] = []
        self._lock = threading.Lock()

        self._vel_count = np.zeros((grid_h, grid_w), dtype=np.float32)
        self._particle_buckets: dict[Tuple[int, int], List[int]] = {}
        self._particle_bucket_size = max(2, PARTICLE_RADIUS * 2)
        self._leaf_buckets: dict[Tuple[int, int], List[int]] = {}
        self._leaf_bucket_size = max(4, LEAF_RADIUS * 2)

        workers = max(2, (os.cpu_count() or 4) - 1)
        self.executor = ThreadPoolExecutor(max_workers=workers)

    def add_leaf(self, x: float, y: float) -> None:
        angle = random.uniform(0, math.pi)
        length = random.uniform(LEAF_LENGTH * 0.7, LEAF_LENGTH * 1.2)
        self.leaves.append(LeafParticle(x, y, angle, length, 1.0))

    def add_water(self, gx: int, gy: int, amount: float) -> None:
        x0 = max(0, gx - POUR_RADIUS)
        x1 = min(self.grid_w, gx + POUR_RADIUS + 1)
        y0 = max(0, gy - POUR_RADIUS)
        y1 = min(self.grid_h, gy + POUR_RADIUS + 1)

        self.water[y0:y1, x0:x1] += amount
        self.v[y0:y1, x0:x1] += GRAVITY * 0.08

        if len(self.particles) < MAX_PARTICLES:
            cx = gx * CELL_SIZE + CELL_SIZE * 0.5
            cy = gy * CELL_SIZE + CELL_SIZE * 0.5
            for _ in range(PARTICLES_PER_POUR):
                if len(self.particles) >= MAX_PARTICLES:
                    break
                px = cx + random.uniform(-CELL_SIZE, CELL_SIZE)
                py = cy + random.uniform(-CELL_SIZE, CELL_SIZE)
                self.particles.append(
                    WaterParticle(
                        px,
                        py,
                        0.0,
                        random.uniform(20.0, 40.0),
                        PARTICLE_RADIUS,
                        0.0,
                    )
                )

    def step(self, dt: float) -> None:
        self._step_particles(dt)
        self._rebuild_velocity_and_water()

        self._water_next[:, :] = self.water
        self._advect_field(self.dye, self._dye_next, dt)

        self._diffuse_inplace(self._water_next, DIFFUSE_WATER)
        self._diffuse_inplace(self._dye_next, DIFFUSE_DYE)

        self._dye_next *= DYE_DECAY
        self.water[:, :] = self._water_next
        self.dye[:, :] = self._dye_next

        self._apply_cup_bounds()

        self._update_leaves(dt)

    def _advect_field(self, src: np.ndarray, dst: np.ndarray, dt: float) -> None:
        rows = self.grid_h
        chunk = max(8, rows // (os.cpu_count() or 4))
        futures = []

        for y0 in range(0, rows, chunk):
            y1 = min(rows, y0 + chunk)
            futures.append(
                self.executor.submit(
                    self._advect_chunk, src, dst, y0, y1, dt
                )
            )

        for future in futures:
            future.result()

    def _advect_chunk(
        self, src: np.ndarray, dst: np.ndarray, y0: int, y1: int, dt: float
    ) -> None:
        x = self.grid_x[y0:y1]
        y = self.grid_y[y0:y1]
        u = self.u[y0:y1]
        v = self.v[y0:y1]

        back_x = x - u * dt * self.inv_cell
        back_y = y - v * dt * self.inv_cell

        back_x = np.clip(back_x, 0, self.grid_w - 1.001)
        back_y = np.clip(back_y, 0, self.grid_h - 1.001)

        x0 = np.floor(back_x).astype(np.int32)
        y0i = np.floor(back_y).astype(np.int32)
        x1 = np.clip(x0 + 1, 0, self.grid_w - 1)
        y1i = np.clip(y0i + 1, 0, self.grid_h - 1)

        sx = back_x - x0
        sy = back_y - y0i

        a = src[y0i, x0]
        b = src[y0i, x1]
        c = src[y1i, x0]
        d = src[y1i, x1]

        dst[y0:y1] = (
            (a * (1 - sx) + b * sx) * (1 - sy)
            + (c * (1 - sx) + d * sx) * sy
        )

    def _diffuse_inplace(self, field: np.ndarray, rate: float) -> None:
        if rate <= 0.0:
            return
        presence = (self.water > MIN_WATER).astype(np.float32)
        n0 = np.roll(field, 1, axis=0)
        n1 = np.roll(field, -1, axis=0)
        n2 = np.roll(field, 1, axis=1)
        n3 = np.roll(field, -1, axis=1)

        p0 = np.roll(presence, 1, axis=0)
        p1 = np.roll(presence, -1, axis=0)
        p2 = np.roll(presence, 1, axis=1)
        p3 = np.roll(presence, -1, axis=1)

        weighted = n0 * p0 + n1 * p1 + n2 * p2 + n3 * p3
        denom = p0 + p1 + p2 + p3
        neighbor_avg = np.where(denom > 0, weighted / denom, field)
        field += (neighbor_avg - field) * rate

    def _step_particles(self, dt: float) -> None:
        if not self.particles:
            return

        for p in self.particles:
            p.vy += GRAVITY * dt * 0.8
            p.vx *= PARTICLE_DAMP
            p.vy *= PARTICLE_DAMP

            p.x += p.vx * dt
            p.y += p.vy * dt

            # circular cup collision: constrain to interior radius
            dx = p.x - self.cup_cx
            dy = p.y - self.cup_cy
            dist = math.hypot(dx, dy)
            inner_r = max(0.0, self.cup_radius - CUP_WALL - p.radius)
            if dist > inner_r:
                if dist == 0.0:
                    nx, ny = 1.0, 0.0
                else:
                    nx, ny = dx / dist, dy / dist
                # project back inside
                p.x = self.cup_cx + nx * inner_r
                p.y = self.cup_cy + ny * inner_r

                # reflect outward component
                vn = p.vx * nx + p.vy * ny
                if vn > 0:
                    p.vx -= (1.0 + PARTICLE_RESTITUTION) * vn * nx
                    p.vy -= (1.0 + PARTICLE_RESTITUTION) * vn * ny

        cell = self._particle_bucket_size
        buckets: dict[Tuple[int, int], List[int]] = {}
        for idx, p in enumerate(self.particles):
            key = (int(p.x // cell), int(p.y // cell))
            buckets.setdefault(key, []).append(idx)

        self._particle_buckets = buckets

        for idx, p in enumerate(self.particles):
            cx = int(p.x // cell)
            cy = int(p.y // cell)
            for oy in (-1, 0, 1):
                for ox in (-1, 0, 1):
                    other = buckets.get((cx + ox, cy + oy))
                    if not other:
                        continue
                    for j in other:
                        if j <= idx:
                            continue
                        q = self.particles[j]
                        dx = q.x - p.x
                        dy = q.y - p.y
                        dist2 = dx * dx + dy * dy
                        min_dist = p.radius + q.radius
                        if dist2 <= 0.0001 or dist2 >= min_dist * min_dist:
                            continue
                        dist = math.sqrt(dist2)
                        nx = dx / dist
                        ny = dy / dist
                        overlap = min_dist - dist
                        p.x -= nx * overlap * 0.5
                        p.y -= ny * overlap * 0.5
                        q.x += nx * overlap * 0.5
                        q.y += ny * overlap * 0.5

                        rvx = q.vx - p.vx
                        rvy = q.vy - p.vy
                        vn = rvx * nx + rvy * ny
                        if vn >= 0:
                            continue
                        impulse = -(1.0 + PARTICLE_RESTITUTION) * vn * 0.5
                        ix = impulse * nx
                        iy = impulse * ny
                        p.vx -= ix
                        p.vy -= iy
                        q.vx += ix
                        q.vy += iy

                        # dye mixing is handled by the grid diffusion step; do not
                        # mutate per-particle dye here.

    def _rebuild_velocity_and_water(self) -> None:
        self.water.fill(0.0)
        self.dye.fill(0.0)
        self.u.fill(0.0)
        self.v.fill(0.0)
        self._vel_count.fill(0.0)

        for p in self.particles:
            gx = int(p.x * self.inv_cell)
            gy = int(p.y * self.inv_cell)
            if gx < 0 or gx >= self.grid_w or gy < 0 or gy >= self.grid_h:
                continue
            self.water[gy, gx] += 1.0
            self.dye[gy, gx] += p.dye
            self.u[gy, gx] += p.vx
            self.v[gy, gx] += p.vy
            self._vel_count[gy, gx] += 1.0

        mask = self._vel_count > 0
        self.u[mask] /= self._vel_count[mask]
        self.v[mask] /= self._vel_count[mask]
        self.dye[mask] /= self._vel_count[mask]

    def _update_leaves(self, dt: float) -> None:
        if not self.leaves:
            return

        for leaf in self.leaves:
            gx = int(leaf.x * self.inv_cell)
            gy = int(leaf.y * self.inv_cell)
            gx = max(0, min(self.grid_w - 1, gx))
            gy = max(0, min(self.grid_h - 1, gy))

            vel_x = float(self.u[gy, gx]) * dt
            vel_y = float(self.v[gy, gx]) * dt

            leaf.vy += GRAVITY * 0.35 * dt
            leaf.vx = (leaf.vx + vel_x * 0.6) * 0.96
            leaf.vy = (leaf.vy + vel_y * 0.6) * 0.96

            leaf.x = max(0.0, min(WINDOW_WIDTH, leaf.x + leaf.vx))
            leaf.y = max(0.0, min(WINDOW_HEIGHT, leaf.y + leaf.vy))

            bottom = self.cup_cy + (self.cup_radius - CUP_WALL)
            if leaf.y < bottom:
                leaf.vy += LEAF_SETTLE_PULL * dt

            self._clamp_leaf_to_cup(leaf)

            if self.water[gy, gx] > 0.15:
                leaf.strength = max(0.0, leaf.strength - 0.6 * dt)
                self._diffuse_leaf_dye(leaf, dt)

        self._resolve_leaf_collisions()

    def _diffuse_leaf_dye(self, leaf: LeafParticle, dt: float) -> None:
        if not self.particles:
            return
        radius = 20.0
        radius2 = radius * radius
        cell = self._particle_bucket_size
        cx = int(leaf.x // cell)
        cy = int(leaf.y // cell)

        for oy in (-1, 0, 1):
            for ox in (-1, 0, 1):
                indices = self._particle_buckets.get((cx + ox, cy + oy))
                if not indices:
                    continue
                for idx in indices:
                    p = self.particles[idx]
                    dx = p.x - leaf.x
                    dy = p.y - leaf.y
                    if dx * dx + dy * dy <= radius2:
                        p.dye = min(1.0, p.dye + 1.4 * dt)

    def _resolve_leaf_collisions(self) -> None:
        if len(self.leaves) < 2:
            return

        cell = self._leaf_bucket_size
        buckets: dict[Tuple[int, int], List[int]] = {}
        for idx, leaf in enumerate(self.leaves):
            key = (int(leaf.x // cell), int(leaf.y // cell))
            buckets.setdefault(key, []).append(idx)

        self._leaf_buckets = buckets
        min_dist = LEAF_RADIUS * 2
        min_dist2 = min_dist * min_dist

        for idx, leaf in enumerate(self.leaves):
            cx = int(leaf.x // cell)
            cy = int(leaf.y // cell)
            for oy in (-1, 0, 1):
                for ox in (-1, 0, 1):
                    others = buckets.get((cx + ox, cy + oy))
                    if not others:
                        continue
                    for j in others:
                        if j <= idx:
                            continue
                        other = self.leaves[j]
                        dx = other.x - leaf.x
                        dy = other.y - leaf.y
                        dist2 = dx * dx + dy * dy
                        if dist2 <= 0.0001 or dist2 >= min_dist2:
                            continue
                        dist = math.sqrt(dist2)
                        nx = dx / dist
                        ny = dy / dist
                        overlap = min_dist - dist
                        leaf.x -= nx * overlap * 0.5
                        leaf.y -= ny * overlap * 0.5
                        other.x += nx * overlap * 0.5
                        other.y += ny * overlap * 0.5

                        rvx = other.vx - leaf.vx
                        rvy = other.vy - leaf.vy
                        vn = rvx * nx + rvy * ny
                        if vn < 0:
                            impulse = -(1.0 + LEAF_RESTITUTION) * vn * 0.5
                            ix = impulse * nx
                            iy = impulse * ny
                            leaf.vx -= ix
                            leaf.vy -= iy
                            other.vx += ix
                            other.vy += iy

                        leaf.vx *= LEAF_FRICTION
                        leaf.vy *= LEAF_FRICTION
                        other.vx *= LEAF_FRICTION
                        other.vy *= LEAF_FRICTION

                        self._clamp_leaf_to_cup(leaf)
                        self._clamp_leaf_to_cup(other)

    def _build_cup_rect(self) -> pygame.Rect:
        cx = WINDOW_WIDTH * 0.5
        cy = WINDOW_HEIGHT - CUP_MARGIN_BOTTOM - (CUP_HEIGHT * 0.5)
        radius = min(CUP_WIDTH, CUP_HEIGHT) * 0.5
        self.cup_cx = float(cx)
        self.cup_cy = float(cy)
        self.cup_radius = float(radius)

        left = int(cx - radius)
        top = int(cy - radius)
        return pygame.Rect(left, top, int(radius * 2), int(radius * 2))

    def _build_cup_mask(self) -> np.ndarray:
        mask = np.zeros((self.grid_h, self.grid_w), dtype=np.float32)

        # compute pixel positions of each cell center
        x_pix = (self.grid_x + 0.5) * CELL_SIZE
        y_pix = (self.grid_y + 0.5) * CELL_SIZE

        dx = x_pix - self.cup_cx
        dy = y_pix - self.cup_cy
        dist2 = dx * dx + dy * dy

        inner_radius = max(0.0, self.cup_radius - CUP_WALL)
        mask[dist2 <= (inner_radius * inner_radius)] = 1.0
        return mask

    def _apply_cup_bounds(self) -> None:
        self.water *= self.cup_mask
        self.dye *= self.cup_mask
        self.u *= self.cup_mask
        self.v *= self.cup_mask

    def _clamp_leaf_to_cup(self, leaf: LeafParticle) -> None:
        # clamp leaf to circular interior
        dx = leaf.x - self.cup_cx
        dy = leaf.y - self.cup_cy
        dist = math.hypot(dx, dy)
        inner_r = max(0.0, self.cup_radius - CUP_WALL - LEAF_RADIUS)
        if dist > inner_r and dist > 0.0:
            nx, ny = dx / dist, dy / dist
            leaf.x = self.cup_cx + nx * inner_r
            leaf.y = self.cup_cy + ny * inner_r

        bottom = self.cup_cy + (self.cup_radius - CUP_WALL)
        if leaf.y >= bottom - 0.5:
            leaf.vy = 0.0
            leaf.vx *= LEAF_FRICTION


class FluidRenderer:
    def __init__(self, sim: FluidSimulation):
        self.sim = sim
        self.surface = pygame.Surface((GRID_W, GRID_H))

    def draw(self, screen: pygame.Surface) -> None:
        water = self.sim.water
        dye = self.sim.dye

        water_intensity = np.clip(water * 1.8, 0.0, 1.0)
        dye_intensity = np.clip(dye * 3.0, 0.0, 1.0)

        color = (
            WATER_COLOR * water_intensity[..., None]
            + TEA_COLOR * dye_intensity[..., None]
        )
        color = np.clip(color + 15, 0, 255).astype(np.uint8)

        pygame.surfarray.blit_array(self.surface, color.swapaxes(0, 1))
        scaled = pygame.transform.smoothscale(
            self.surface, (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        screen.blit(scaled, (0, 0))

        for p in self.sim.particles:
            gx = int(p.x * self.sim.inv_cell)
            gy = int(p.y * self.sim.inv_cell)
            if 0 <= gx < self.sim.grid_w and 0 <= gy < self.sim.grid_h:
                dye = float(self.sim.dye[gy, gx])
            else:
                dye = 0.0
            t = min(1.0, dye * 1.5)
            color = (
                int(WATER_COLOR[0] * (1 - t) + TEA_COLOR[0] * t),
                int(WATER_COLOR[1] * (1 - t) + TEA_COLOR[1] * t),
                int(WATER_COLOR[2] * (1 - t) + TEA_COLOR[2] * t),
            )
            pygame.draw.circle(screen, color, (int(p.x), int(p.y)), int(p.radius))

        for leaf in self.sim.leaves:
            t = 1.0 - leaf.strength
            color = (
                int(LEAF_COLOR_DRY[0] * (1 - t) + LEAF_COLOR_WET[0] * t),
                int(LEAF_COLOR_DRY[1] * (1 - t) + LEAF_COLOR_WET[1] * t),
                int(LEAF_COLOR_DRY[2] * (1 - t) + LEAF_COLOR_WET[2] * t),
            )
            start, end = leaf.as_segment()
            pygame.draw.line(
                screen,
                color,
                (start[0], start[1]),
                (end[0], end[1]),
                LEAF_THICKNESS,
            )

        self._draw_cup(screen)

    def _draw_cup(self, screen: pygame.Surface) -> None:
        # draw circular cup (wall thickness = CUP_WALL) and visually open the top
        cx = int(self.sim.cup_cx)
        cy = int(self.sim.cup_cy)
        radius = int(self.sim.cup_radius)

        pygame.draw.circle(screen, CUP_COLOR, (cx, cy), radius, CUP_WALL)

        # erase a small portion of the rim at the top to make the cup open
        erase_h = max(4, CUP_WALL + 90)
        erase_rect = pygame.Rect(cx - radius, cy - radius - erase_h // 2, radius * 2, erase_h)
        pygame.draw.rect(screen, BACKGROUND, erase_rect)


class FluidSimulationScene:
    """Scene wrapper exposing the simulation as a scene-like object.

    Methods: `handle_event(event)`, `update(dt)`, `draw()` to match
    other scene classes in the project.
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        self.sim = FluidSimulation(GRID_W, GRID_H)
        self.renderer = FluidRenderer(self.sim)

        # precompute pour grid position at the cup rim
        self.pour_gx = int(self.sim.cup_cx * self.sim.inv_cell)
        pour_px = self.sim.cup_cy - self.sim.cup_radius + CUP_WALL + 2
        self.pour_gy = int(pour_px * self.sim.inv_cell)

        # add a few leaves as background detail
        for _ in range(50):
            self.sim.add_leaf(
                random.uniform(WINDOW_WIDTH * 0.3, WINDOW_WIDTH * 0.7),
                random.uniform(WINDOW_HEIGHT * 0.5, WINDOW_HEIGHT * 0.9),
            )

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "quit"
        if event.type == pygame.MOUSEBUTTONDOWN:
            return "quit"
        return None

    def update(self, dt: float):
        # continuous pour into the cup
        self.sim.add_water(self.pour_gx, self.pour_gy, POUR_RATE * dt)
        self.sim.step(dt)
        return None

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)
        self.renderer.draw(self.screen)
