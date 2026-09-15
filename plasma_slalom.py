#!/usr/bin/env python3
"""Plasma Slalom — neon canyon-gate arcade for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/home/workdir/artifacts/PLASMA_SLALOM_ElbowOS.mp4")
TITLE, HANDLE = "PLASMA SLALOM", "x.com/ElbowOS"

BG = (10, 6, 22)
NAVY = (18, 12, 40)
GOLD = (255, 196, 64)
MAG = (255, 48, 140)
CYAN = (48, 240, 220)
LIME = (180, 255, 90)
WHITE = (250, 248, 255)
VIO = (160, 90, 255)
ORANGE = (255, 120, 40)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption(TITLE)
        self.font_lg = pygame.font.SysFont("DejaVu Sans", 58, bold=True)
        self.font = pygame.font.SysFont("DejaVu Sans", 36, bold=True)
        self.font_sm = pygame.font.SysFont("DejaVu Sans", 26)
        self.clock = pygame.time.Clock()
        self.x = W * 0.5
        self.y = 1420
        self.vx = 0
        self.score = self.combo = self.t = self.flash = self.lives = 0
        self.speed = 14
        self.gates, self.pillars, self.sparks, self.trail = [], [], [], []
        self.stars = [[random.randint(0, W), random.randint(0, H),
                       random.uniform(1.2, 4.0), random.choice((CYAN, VIO, GOLD, MAG))]
                      for _ in range(70)]
        self.wall_phase = 0.0
        self.reset()

    def reset(self):
        self.gates.clear()
        self.pillars.clear()
        self.lives = 3
        self.combo = 0
        self.x = W * 0.5
        self.spawn_cd = 8
        self.pillar_cd = 18

    def burst(self, x, y, col, n=14):
        for _ in range(n):
            a = random.uniform(0, 6.2832)
            sp = random.uniform(3, 13)
            self.sparks.append([x, y, math.cos(a) * sp, math.sin(a) * sp, 16, col])

    def walls_at(self, y):
        p = self.wall_phase + y * 0.004
        mid = W * 0.5 + math.sin(p) * 90 + math.sin(p * 0.37) * 50
        half = 310 + 40 * math.sin(p * 0.7)
        return mid - half, mid + half

    def spawn_gate(self):
        L, R = self.walls_at(-40)
        gap = random.randint(150, 210)
        cx = random.uniform(L + gap * 0.6, R - gap * 0.6)
        self.gates.append([cx, -50, gap, False])

    def spawn_pillar(self):
        L, R = self.walls_at(-80)
        side = random.choice((-1, 1))
        px = (L + 70) if side < 0 else (R - 70)
        px += random.uniform(-30, 30)
        self.pillars.append([px, -80, 28 + random.random() * 10])

    def hit_check(self):
        for g in self.gates:
            if g[3]:
                continue
            if abs(g[1] - self.y) < 28:
                if abs(self.x - g[0]) < g[2] * 0.48:
                    g[3] = True
                    self.combo += 1
                    self.score += 20 + self.combo * 4
                    self.burst(self.x, self.y, GOLD, 18)
                else:
                    self.combo = 0
                    g[3] = True
        for p in list(self.pillars):
            if (self.x - p[0]) ** 2 + (self.y - p[1]) ** 2 < (p[2] + 26) ** 2:
                self.lives -= 1
                self.combo = 0
                self.flash = 10
                self.burst(self.x, self.y, MAG, 22)
                self.pillars.remove(p)
                if self.lives <= 0:
                    self.score = max(0, self.score - 25)
                    self.reset()

    def autoplay(self):
        upcoming = [g for g in self.gates if not g[3] and -20 < g[1] < self.y + 40]
        hazards = [p for p in self.pillars if abs(p[1] - self.y) < 280]
        want = self.x
        if upcoming:
            g = min(upcoming, key=lambda z: self.y - z[1])
            want = g[0]
        L, R = self.walls_at(self.y)
        want = max(L + 70, min(R - 70, want))
        for p in hazards:
            if abs(want - p[0]) < 70:
                want += 110 if self.x >= p[0] else -110
        want = max(L + 70, min(R - 70, want))
        err = want - self.x
        self.vx = max(-24, min(24, err * 0.28 + math.sin(self.t * 0.11) * 1.4))

    def tick(self):
        self.t += 1
        self.flash = max(0, self.flash - 1)
        self.speed = 13 + min(8, self.t / 90)
        self.wall_phase += 0.045
        self.x = max(80, min(W - 80, self.x + self.vx))
        self.vx *= 0.88
        L, R = self.walls_at(self.y)
        if self.x < L + 36 or self.x > R - 36:
            self.x = max(L + 40, min(R - 40, self.x))
            self.flash = max(self.flash, 4)
        self.spawn_cd -= 1
        self.pillar_cd -= 1
        if self.spawn_cd <= 0:
            self.spawn_gate()
            self.spawn_cd = max(18, 28 - self.t // 60)
        if self.pillar_cd <= 0:
            self.spawn_pillar()
            self.pillar_cd = max(16, 26 - self.t // 70)
        dy = self.speed
        for g in self.gates:
            g[1] += dy
        for p in self.pillars:
            p[1] += dy
        self.gates = [g for g in self.gates if g[1] < H + 40]
        self.pillars = [p for p in self.pillars if p[1] < H + 40]
        self.hit_check()
        self.trail.append([self.x, self.y, 12])
        self.trail = self.trail[-28:]
        for tr in self.trail:
            tr[2] -= 0.35
        for s in self.sparks:
            s[0] += s[2]
            s[1] += s[3] + dy * 0.15
            s[4] -= 1
        self.sparks = [s for s in self.sparks if s[4] > 0]
        for st in self.stars:
            st[1] += st[2] + self.speed * 0.25
            if st[1] > H + 4:
                st[1] = -4
                st[0] = random.randint(0, W)

    def draw(self, surf):
        surf.fill(BG)
        for st in self.stars:
            pygame.draw.circle(surf, st[3], (int(st[0]), int(st[1])), 2)
        for y in range(-40, H + 40, 16):
            L, R = self.walls_at(y)
            shade = 14 + int(10 * math.sin(y * 0.02 + self.t * 0.05))
            pygame.draw.rect(surf, (shade, 8, 28), (0, y, max(0, L), 18))
            pygame.draw.rect(surf, (shade, 8, 28), (R, y, W - R, 18))
            pygame.draw.line(surf, MAG if (y // 16 + self.t // 4) % 7 == 0 else VIO,
                             (L, y), (L, y + 18), 3)
            pygame.draw.line(surf, CYAN if (y // 16 + self.t // 4) % 5 == 0 else VIO,
                             (R, y), (R, y + 18), 3)
        for g in self.gates:
            gx, gy, gap, done = g
            col = LIME if done else GOLD
            pygame.draw.line(surf, col, (gx - gap / 2, gy), (gx + gap / 2, gy), 8)
            pygame.draw.circle(surf, WHITE, (int(gx - gap / 2), int(gy)), 10)
            pygame.draw.circle(surf, WHITE, (int(gx + gap / 2), int(gy)), 10)
            pygame.draw.circle(surf, col, (int(gx - gap / 2), int(gy)), 6)
            pygame.draw.circle(surf, col, (int(gx + gap / 2), int(gy)), 6)
        for p in self.pillars:
            pygame.draw.circle(surf, MAG, (int(p[0]), int(p[1])), int(p[2]))
            pygame.draw.circle(surf, ORANGE, (int(p[0]), int(p[1])), int(p[2] * 0.45))
            pygame.draw.circle(surf, WHITE, (int(p[0]), int(p[1])), 4)
        for tr in self.trail:
            if tr[2] > 0:
                pygame.draw.circle(surf, CYAN, (int(tr[0]), int(tr[1])), max(2, int(tr[2])))
        bx, by = int(self.x), int(self.y)
        lean = self.vx * 1.6
        board = [(bx - 34 + lean, by + 10), (bx + 34 + lean, by + 10),
                 (bx + 22 + lean, by + 28), (bx - 22 + lean, by + 28)]
        pygame.draw.polygon(surf, GOLD, board)
        pygame.draw.polygon(surf, WHITE, board, 2)
        body = [(bx + lean * 0.4, by - 38), (bx - 16, by + 8), (bx + 16, by + 8)]
        pygame.draw.polygon(surf, CYAN, body)
        pygame.draw.circle(surf, WHITE, (bx + int(lean * 0.2), by - 44), 10)
        pygame.draw.circle(surf, MAG, (bx + int(lean * 0.2), by - 44), 5)
        for s in self.sparks:
            pygame.draw.circle(surf, s[5], (int(s[0]), int(s[1])), max(2, s[4] // 4))
        if self.flash:
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((255, 40, 110, 55))
            surf.blit(ov, (0, 0))
        title = self.font_lg.render(TITLE, True, GOLD)
        surf.blit(title, title.get_rect(center=(W // 2, 84)))
        sub = self.font_sm.render(HANDLE, True, CYAN)
        surf.blit(sub, sub.get_rect(center=(W // 2, 146)))
        sc = self.font.render(f"SCORE  {self.score}", True, WHITE)
        lv = self.font.render(f"LIVES  {'\u25c6' * max(0, self.lives)}", True, MAG)
        cb = self.font_sm.render(f"COMBO  x{self.combo}", True, LIME)
        surf.blit(sc, sc.get_rect(center=(W // 2, H - 168)))
        surf.blit(lv, lv.get_rect(center=(W // 2, H - 108)))
        surf.blit(cb, cb.get_rect(center=(W // 2, H - 58)))

    def play_interactive(self):
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    running = False
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    self.reset()
                    self.score = 0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vx = -20
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vx = 20
            self.tick()
            self.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

    def record(self):
        frames = FPS * SECS
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "fast", "-movflags", "+faststart",
            OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        canvas = pygame.Surface((W, H))
        try:
            for i in range(frames):
                self.autoplay()
                self.tick()
                self.draw(canvas)
                proc.stdin.write(pygame.image.tostring(canvas, "RGB"))
                if i % 30 == 0:
                    print(f"frame {i}/{frames}", flush=True)
        finally:
            proc.stdin.close()
            err = proc.stderr.read().decode("utf-8", "ignore")
            rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT)
        pygame.quit()


def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()


if __name__ == "__main__":
    main()
