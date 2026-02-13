import multiprocessing as mp
from multiprocessing.shared_memory import SharedMemory
import os
import sys
import time
import random
from typing import Optional, Tuple

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import numpy as np
import pygame


def _sim_worker(
    shm_names: Tuple[str, str],
    width: int,
    height: int,
    frame_counter: mp.Array,
    stop_event: mp.Event,
    start_event: mp.Event,
):
    # headless pygame in worker only
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    # Import here to avoid circular imports at spawn time
    from game.scenes.fluid_simulation_scene import (
        FluidSimulation,
        FluidRenderer,
        GRID_W,
        GRID_H,
        BACKGROUND,
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        CUP_WALL,
        POUR_RATE,
    )

    # Recreate shared buffers
    shms = [SharedMemory(name=n) for n in shm_names]
    buffers = [np.ndarray((height, width, 3), dtype=np.uint8, buffer=shm.buf) for shm in shms]

    # Init pygame (headless surface)
    pygame.init()
    sim = FluidSimulation(GRID_W, GRID_H, enable_dye=False)
    renderer = FluidRenderer(sim)
    surface = pygame.Surface((width, height))

    # seed leaves similar to FluidSimulationScene
    for _ in range(50):
        sim.add_leaf(
            random.uniform(WINDOW_WIDTH * 0.3, WINDOW_WIDTH * 0.7),
            random.uniform(WINDOW_HEIGHT * 0.5, WINDOW_HEIGHT * 0.9),
        )

    # perf tracking
    dt_samples = []
    step_samples = []
    draw_samples = []
    copy_samples = []
    last_report = time.perf_counter()
    pour_gx = int(sim.cup_cx * sim.inv_cell)
    pour_px = sim.cup_cy - sim.cup_radius + CUP_WALL + 2
    pour_gy = int(pour_px * sim.inv_cell)

    start_event.set()

    active = 0
    clock = pygame.time.Clock()
    while not stop_event.is_set():
        dt = clock.tick(60) / 1000.0

        t_step_start = time.perf_counter()
        sim.add_water(pour_gx, pour_gy, POUR_RATE * dt)
        sim.step(dt)
        t_step_end = time.perf_counter()

        t_draw_start = time.perf_counter()
        surface.fill(BACKGROUND)
        renderer.draw(surface)
        t_draw_end = time.perf_counter()

        t_copy_start = time.perf_counter()
        # array3d returns shape (width, height, 3); transpose to (height, width, 3)
        view = pygame.surfarray.array3d(surface).transpose(1, 0, 2)
        np.copyto(buffers[active], view)
        t_copy_end = time.perf_counter()

        with frame_counter.get_lock():
            frame_counter[0] = (frame_counter[0] + 1) % (1 << 30)  # frame count
            frame_counter[1] = active  # store active index

        active ^= 1

        # perf samples (bounded)
        dt_samples.append(dt)
        step_samples.append(t_step_end - t_step_start)
        draw_samples.append(t_draw_end - t_draw_start)
        copy_samples.append(t_copy_end - t_copy_start)
        if len(dt_samples) > 600:
            dt_samples.pop(0)
            step_samples.pop(0)
            draw_samples.pop(0)
            copy_samples.pop(0)

        now = time.perf_counter()
        if now - last_report >= 2.0:
            def stats(buf):
                return (min(buf), sum(buf) / len(buf), max(buf)) if buf else (0, 0, 0)

            dt_min, dt_avg, dt_max = stats(dt_samples)
            st_min, st_avg, st_max = stats(step_samples)
            dr_min, dr_avg, dr_max = stats(draw_samples)
            cp_min, cp_avg, cp_max = stats(copy_samples)
            print(
                f"[sim worker perf] samples={len(dt_samples)} "
                f"dt_ms {dt_min*1000:.2f}/{dt_avg*1000:.2f}/{dt_max*1000:.2f} "
                f"step_ms {st_min*1000:.2f}/{st_avg*1000:.2f}/{st_max*1000:.2f} "
                f"draw_ms {dr_min*1000:.2f}/{dr_avg*1000:.2f}/{dr_max*1000:.2f} "
                f"copy_ms {cp_min*1000:.2f}/{cp_avg*1000:.2f}/{cp_max*1000:.2f}"
            )
            last_report = now

    for shm in shms:
        shm.close()
    pygame.quit()


class SharedSimSurface:
    """Runs the fluid simulation in a separate process and exposes shared RGB buffers."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.buf_size = width * height * 3
        self.shms = [SharedMemory(create=True, size=self.buf_size) for _ in range(2)]
        self.frame_counter = mp.Array('i', [0, 0])  # [frame_count, active_index]
        self.stop_event = mp.Event()
        self.start_event = mp.Event()
        self.proc: Optional[mp.Process] = None
        self.surfaces = [None, None]

    def start(self):
        self.proc = mp.Process(
            target=_sim_worker,
            args=([
                self.shms[0].name,
                self.shms[1].name,
            ], self.width, self.height, self.frame_counter, self.stop_event, self.start_event),
            daemon=True,
        )
        self.proc.start()
        # Wait until worker signals readiness
        self.start_event.wait(timeout=5)
        self.surfaces = [self._surface_from_shm(shm) for shm in self.shms]

    def _surface_from_shm(self, shm: SharedMemory) -> pygame.Surface:
        buf = shm.buf
        return pygame.image.frombuffer(buf, (self.width, self.height), "RGB")

    def get_surface(self) -> pygame.Surface:
        idx = self.frame_counter[1]
        return self.surfaces[idx]

    def shutdown(self):
        self.stop_event.set()
        if self.proc is not None:
            self.proc.join(timeout=3)
        for shm in self.shms:
            shm.close()
            shm.unlink()

    def __del__(self):
        try:
            self.shutdown()
        except Exception:
            pass
