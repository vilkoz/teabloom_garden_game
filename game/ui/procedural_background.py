import pygame
import math
import random


def _lerp(a, b, t):
    return int(a + (b - a) * t)


class ProceduralBackground:
    """Procedurally generate a layered greenery background.

    Produces a pre-rendered surface for performance. Uses layered
    wavy polygons and soft alpha "blobs" to simulate foliage.
    """

    def __init__(self, width, height, seed=0):
        self.width = width
        self.height = height
        self.seed = seed
        self._rand = random.Random(seed)
        # base static surfaces (sky). Layers will be rendered per-depth.
        self.surface = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        self.sky_surface = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        self._generate()

        # dynamic elements: flowers and hearts
        self.flowers = []
        self.hearts = []
        self._spawn_flowers(300)
        self._spawn_hearts(500)
        self._frame = 0.0

        # static depth buckets array (1000 slots). We'll clear and populate each draw.
        self._depth_buckets = [[] for _ in range(1000)]

    def _vertical_gradient(self, surf, top_color, bottom_color):
        w, h = surf.get_size()
        arr = pygame.Surface((w, 1)).convert_alpha()
        for x in range(w):
            pass
        for y in range(h):
            t = y / float(h - 1)
            r = _lerp(top_color[0], bottom_color[0], t)
            g = _lerp(top_color[1], bottom_color[1], t)
            b = _lerp(top_color[2], bottom_color[2], t)
            a = 255
            pygame.draw.line(surf, (r, g, b, a), (0, y), (w, y))

    def _wavy_heights(self, amplitude, freq, phase, baseline=0, step=6):
        """Generate a height map across the width using layered sines."""
        heights = []
        for x in range(0, self.width + step, step):
            nx = float(x) / self.width
            y = baseline
            y += amplitude * math.sin(nx * freq * 2 * math.pi + phase)
            heights.append((x, int(y)))
        return heights

    def _generate(self):
        # Prepare static sky and layer parameter templates. Actual layer
        # rendering is done in `_render_layers` so we can animate by
        # modifying phase/amplitude only.
        self.surface.fill((0, 0, 0, 0))

        # Sky gradient (static)
        top = (245, 238, 230)
        bottom = (200, 240, 255)
        self._vertical_gradient(self.sky_surface, top, bottom)

        # Define layer templates and create blob surfaces for each layer
        templates = [
            {"amplitude": 40, "freq": 1.2, "color": (170, 210, 160)},
            {"amplitude": 70, "freq": 0.9, "color": (120, 190, 110)},
            {"amplitude": 110, "freq": 0.6, "color": (80, 160, 80)},
        ]

        self._layers = []
        for i, t in enumerate(templates):
            base_amp = t["amplitude"]
            freq = t["freq"] * (1 + self._rand.uniform(-0.08, 0.08))
            phase = self._rand.uniform(0, math.pi * 2)
            baseline = int(self.height * (0.70 - i * 0.15))
            col = t["color"]
            shade = (
                max(0, col[0] + self._rand.randint(-8, 8)),
                max(0, col[1] + self._rand.randint(-12, 12)),
                max(0, col[2] + self._rand.randint(-8, 8)),
            )

            # Precompute a blob surface for texture (static positions)
            blob_surf = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)
            for _ in range(18 - i * 4):
                rx = self._rand.randrange(0, self.width)
                ry = self._rand.randrange(int(self.height * 0.35), self.height)
                rrad = int(self._rand.randrange(40, 120) * (1.0 - i * 0.12))
                alpha = self._rand.randint(30, 80)
                col_blob = (shade[0], shade[1] + 10, shade[2], alpha)
                pygame.draw.circle(blob_surf, col_blob, (rx, ry), rrad)

            layer = {
                "base_amplitude": base_amp,
                "amplitude": base_amp,
                "freq": freq,
                "phase": phase,
                "baseline": baseline,
                "shade": shade,
                "blob_surf": blob_surf,
                "phase_speed": 0.12 + i * 0.03,
                "amp_jitter": max(2, int(base_amp * 0.06)),
                "depth": [250, 500, 750][i],
            }
            self._layers.append(layer)

        # Initial internal frame
        self._frame = 1.0
        # initial render into surface (will be overwritten by depth drawing)
        self._render_layers()

        # Foreground rim and ground strip for visual separation (drawn atop layers)
        ground_color = (60, 120, 60)
        pygame.draw.rect(self.surface, ground_color + (255,), (0, int(self.height * 0.9), self.width, int(self.height * 0.12)))

    def _render_layer(self, i, layer, target_surface):
        amp = layer["amplitude"]
        freq = layer["freq"]
        phase = layer["phase"]
        baseline = layer["baseline"]
        points = [(0, self.height)]
        heights = self._wavy_heights(amp, freq, phase, baseline)
        points.extend(heights)
        points.append((self.width, self.height))
        pygame.draw.polygon(target_surface, layer["shade"] + (255,), points)

        # blit static blob texture with a tiny offset to simulate motion
        ox = int(math.sin(self._frame * (0.25 + i * 0.12)) * 6)
        oy = int(math.cos(self._frame * (0.18 + i * 0.08)) * 3)
        target_surface.blit(layer["blob_surf"], (ox, oy), special_flags=pygame.BLEND_RGBA_ADD)

    def _render_layers(self):
        s = self.surface
        # redraw sky first (keep sky static)
        top = (245, 238, 230)
        bottom = (200, 240, 255)
        self._vertical_gradient(s, top, bottom)

        # draw each layer using current amplitude/phase
        for i, layer in enumerate(self._layers):
            self._render_layer(i, layer, s)

    def _find_layer_for_depth(self, depth):
        """Return index of the first layer whose depth is >= given depth.

        If none match, return the last layer index.
        """
        if not hasattr(self, "_layers") or not self._layers:
            return 0
        for i, layer in enumerate(self._layers):
            if layer.get("depth", 0) >= depth:
                return i
        return len(self._layers) - 1

    def _spawn_flowers(self, count):
        for _ in range(count):
            x = self._rand.uniform(0, self.width)
            y = self._rand.uniform(int(self.height * 0.45), int(self.height * 0.88))
            size = self._rand.uniform(8, 24)
            speed = self._rand.uniform(0.6, 1.6)
            phase = self._rand.uniform(0, math.pi * 2)
            color = (
                self._rand.randint(200, 255),
                self._rand.randint(120, 220),
                self._rand.randint(120, 255),
            )
            depth = self._rand.randint(200, 1000)
            # determine which layer is behind this flower
            layer_idx = self._find_layer_for_depth(depth)
            self.flowers.append({"x": x, "y": y, "size": size, "speed": speed, "phase": phase, "color": color, "depth": depth, "layer_idx": layer_idx})

    def _spawn_hearts(self, count):
        for _ in range(count):
            x = self._rand.uniform(0, self.width)
            y = self._rand.uniform(int(self.height * 0.6), int(self.height * 0.95))
            size = self._rand.uniform(12, 36)
            vy = -self._rand.uniform(8, 24)
            bob = self._rand.uniform(0.8, 2.0)
            color = (255, self._rand.randint(80, 200), self._rand.randint(120, 255))
            depth = self._rand.randint(200, 1000)
            self.hearts.append({"x": x, "y": y, "size": size, "vy": vy, "bob": bob, "t": 0.0, "color": color, "depth": depth})

    def update(self, dt):
        """Update animated elements. dt in seconds."""
        # accept dt in seconds, or ms from pygame.Clock.tick
        if dt > 1.0:
            dt = dt / 1000.0

        # advance internal time
        self._frame += dt

        # animate layer phases and small amplitude jitter but do not
        # regenerate randomness — only adjust parameters
        if hasattr(self, "_layers"):
            for i, layer in enumerate(self._layers):
                layer["phase"] += dt * layer.get("phase_speed", 0.12)
                # gentle amplitude wobble around base_amplitude
                wobble = math.sin(self._frame * (0.3 + i * 0.1) + layer["phase"]) * (layer["amp_jitter"])
                layer["amplitude"] = layer["base_amplitude"] + wobble
            # re-render layers to the base surface
            self._render_layers()

        # Flowers bob gently
        for f in self.flowers:
            f["phase"] += dt * f["speed"]
            bob = math.sin(f["phase"]) * (f["size"] * 0.08)
            # sync movement with the layer behind the flower
            layer_idx = f.get("layer_idx")
            if layer_idx is None:
                layer_idx = self._find_layer_for_depth(int(f.get("depth", 500)))
                f["layer_idx"] = layer_idx
            if 0 <= layer_idx < len(self._layers):
                layer = self._layers[layer_idx]
                # vertical sync offset proportional to layer amplitude
                sync_v = math.sin(layer["phase"] + f["phase"] * 0.5) * (layer["amplitude"])
                # slight horizontal drift following layer phase
                sync_x = math.sin(layer["phase"] * 0.6 + f["phase"] * 0.4) * (layer["amp_jitter"])
            else:
                sync_v = 0.0
                sync_x = 0.0

            f["draw_y"] = f["y"] + bob + sync_v
            f["draw_x"] = f["x"] + sync_x

        # Hearts float upward and bob horizontally, respawn at bottom
        for h in self.hearts:
            h["t"] += dt
            h["y"] += h["vy"] * dt
            h["x"] += math.sin(h["t"] * h["bob"]) * 8 * dt
            if h["y"] + h["size"] < -20:
                # respawn near bottom
                h["x"] = self._rand.uniform(0, self.width)
                h["y"] = self._rand.uniform(int(self.height * 0.85), int(self.height * 1.05))
                h["vy"] = -self._rand.uniform(8, 24)
                h["t"] = 0.0

    def _draw_heart(self, surf, x, y, size, color):
        # draw an approximate heart by combining two circles and a triangle
        w = int(size * 2)
        h = int(size * 2)
        heart_surf = pygame.Surface((w, h), flags=pygame.SRCALPHA)
        cx = w // 2
        cy = h // 3
        r = int(size * 0.50)
        pygame.draw.circle(heart_surf, color + (255,), (int(cx - r * 1.0), cy), r)
        pygame.draw.circle(heart_surf, color + (255,), (int(cx + r * 1.0), cy), r)
        points = [
            (int(cx - size), int(cy + r * 0.2)),
            (int(cx + size), int(cy + r * 0.2)),
            (cx, int(h)),
        ]
        pygame.draw.polygon(heart_surf, color + (255,), points)
        surf.blit(heart_surf, (int(x - w // 2), int(y - h // 2)))

    def _draw_flower(self, surf, x, y, size, color):
        # simple stylized flower: 5 petals + center
        petal_count = 5
        for i in range(petal_count):
            ang = i * (2 * math.pi / petal_count)
            px = x + math.cos(ang) * size * 0.7
            py = y + math.sin(ang) * size * 0.7
            petal_rect = pygame.Rect(0, 0, int(size * 1.1), int(size * 0.6))
            petal_surf = pygame.Surface(petal_rect.size, flags=pygame.SRCALPHA)
            petal_color = (max(0, color[0] - 30), max(0, color[1] - 30), max(0, color[2] - 30))
            pygame.draw.ellipse(petal_surf, petal_color + (220,), petal_surf.get_rect())
            rot = -math.degrees(ang)
            petal_surf = pygame.transform.rotate(petal_surf, rot)
            pr = petal_surf.get_rect(center=(int(px), int(py)))
            surf.blit(petal_surf, pr)
        # center
        pygame.draw.circle(surf, (255, 220, 80), (int(x), int(y)), int(size * 0.45))

    def draw(self, target_surface):
        # Clear and populate depth buckets (static 1000-size array)
        for i in range(len(self._depth_buckets)):
            self._depth_buckets[i].clear()

        # Put layers into buckets at their predefined depths
        for li, layer in enumerate(self._layers):
            d = int(layer.get("depth", 1))
            idx = max(0, min(999, d - 1))
            self._depth_buckets[idx].append(("layer", li))

        # Flowers and hearts get random depth assigned at spawn; ensure present
        for f in self.flowers:
            d = int(f.get("depth", self._rand.randint(1, 1000)))
            idx = max(0, min(999, d - 1))
            self._depth_buckets[idx].append(("flower", f))

        for h in self.hearts:
            d = int(h.get("depth", self._rand.randint(1, 1000)))
            idx = max(0, min(999, d - 1))
            self._depth_buckets[idx].append(("heart", h))

        # Place sky at highest depth so it is drawn first (background)
        self._depth_buckets[999].append(("sky", None))

        depth_modifier = 0.01

        # Iterate from highest depth -> lowest (1000 -> 1)
        for depth_index in range(999, -1, -1):
            bucket = self._depth_buckets[depth_index]
            if not bucket:
                continue
            for item_type, payload in bucket:
                if item_type == "layer":
                    li = payload
                    layer = self._layers[li]
                    self._render_layer(li, layer, target_surface)

                elif item_type == "flower":
                    f = payload
                    depth = max(1, int(f.get("depth", 1)))
                    scale = 1.0 / (float(depth) * depth_modifier)
                    size = max(1, int(f["size"] * scale))
                    draw_y = f.get("draw_y", f["y"]) if isinstance(f, dict) else f["y"]
                    draw_x = f.get("draw_x", f["x"]) if isinstance(f, dict) else f["x"]
                    self._draw_flower(target_surface, draw_x, draw_y, size, f["color"])

                elif item_type == "heart":
                    h = payload
                    depth = max(1, int(h.get("depth", 1)))
                    scale = 1.0 / (float(depth) * depth_modifier)
                    size = max(1, int(h["size"] * scale))
                    self._draw_heart(target_surface, h["x"], h["y"], size, h["color"])

                elif item_type == "sky":
                    # sky drawn last (lowest depth)
                    target_surface.blit(self.sky_surface, (0, 0))
