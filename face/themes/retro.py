import pygame
import math
import random
import time
import sys
import os

# CONFIG
W, H = 800, 480 # Logical
BG_COLOR = (0, 10, 0) 
FG_COLOR = (50, 255, 50) 
SCANLINE_COLOR = (0, 40, 0, 100) 

class RetroFace:
    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.raw_w, self.raw_h = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.raw_w, self.raw_h), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)

        self.render_surf = pygame.Surface((W, H))
        self.scan_surf = pygame.Surface((W, H), pygame.SRCALPHA)
        self._init_scanlines()

        self.clock = pygame.time.Clock()
        self.blinking = False
        self.blink_timer = 0
        self.double_blink = False
        
        # Idle Animation State
        self.eye_offset_x = 0
        self.eye_offset_y = 0
        self.target_eye_x = 0
        self.target_eye_y = 0
        self.next_saccade = time.time() + random.uniform(2, 5)
        
        # Expression: 'IDLE', 'HAPPY', 'THINKING', 'SAD'
        self.expression = 'IDLE'
        self.next_expression = time.time() + 10
        
        # Background Grid
        self.grid_scroll = 0
        
        # Status Logs
        self.logs = ["CORE_INIT: OK", "NEURAL_SYNC: 98%", "DREAM_CYCLE: IDLE"]
        self.log_font = pygame.font.SysFont("Courier New", 14, bold=True)

    def _init_scanlines(self):
        for y in range(0, H, 4):
            pygame.draw.line(self.scan_surf, SCANLINE_COLOR, (0, y), (W, y), 2)

    def draw_grid(self, surf):
        # Draw a scrolling vector grid in the background
        self.grid_scroll = (self.grid_scroll + 1) % 80
        color = (0, 30, 0)
        for x in range(0, W + 80, 80):
            pygame.draw.line(surf, color, (x - self.grid_scroll, 0), (x - self.grid_scroll, H), 1)
        for y in range(0, H + 80, 80):
            pygame.draw.line(surf, color, (0, y), (W, y), 1)

    def draw_status(self, surf):
        # Top Left Logs
        for i, log in enumerate(self.logs):
            txt = self.log_font.render(f"> {log}", True, (0, 100, 0))
            surf.blit(txt, (20, 20 + i * 20))
        
        # Bottom Right Hardware Info
        t = time.strftime("%H:%M:%S")
        txt = self.log_font.render(f"LUCY_OS v2.0.4 // {t}", True, (0, 100, 0))
        surf.blit(txt, (W - txt.get_width() - 20, H - 30))

    def draw_eye(self, x, y, flip=False):
        # Apply saccade offsets
        x += self.eye_offset_x
        y += self.eye_offset_y
        
        # Expression Tilt
        tilt = 0
        if self.expression == 'HAPPY': tilt = 15 if not flip else -15
        elif self.expression == 'SAD': tilt = -15 if not flip else 15
        
        if self.blinking:
            pygame.draw.line(self.render_surf, FG_COLOR, (x-45, y+20), (x+45, y+20), 4)
        else:
            # Bracket Eye
            pts_l = [(x-20, y-40), (x-40, y-40), (x-40, y+40), (x-20, y+40)]
            pts_r = [(x+20, y-40), (x+40, y-40), (x+40, y+40), (x+20, y+40)]
            
            # Apply tilt
            def rotate_pt(pt, angle, center):
                angle = math.radians(angle)
                px, py = pt
                cx, cy = center
                nx = cx + math.cos(angle) * (px - cx) - math.sin(angle) * (py - cy)
                ny = cy + math.sin(angle) * (px - cx) + math.cos(angle) * (py - cy)
                return (nx, ny)

            pts_l = [rotate_pt(p, tilt, (x, y)) for p in pts_l]
            pts_r = [rotate_pt(p, tilt, (x, y)) for p in pts_r]

            pygame.draw.lines(self.render_surf, FG_COLOR, False, pts_l, 8)
            pygame.draw.lines(self.render_surf, FG_COLOR, False, pts_r, 8)

            # Pupil with Thinking logic
            p_y = y
            if self.expression == 'THINKING': p_y -= 15
            pygame.draw.rect(self.render_surf, FG_COLOR, (x-12, p_y-12, 24, 24))

    def draw_mouth(self, cx, cy):
        # New Segmented Phosphor Mouth
        segments = 24
        seg_width = 10
        total_width = segments * (seg_width + 4)
        start_x = cx - total_width // 2
        
        for i in range(segments):
            # Base wave
            freq = 0.15
            speed = time.time() * 8
            h = math.sin(speed + i * freq) * 10
            
            # Expression Shaping
            if self.expression == 'HAPPY':
                dist = abs(i - segments/2) / (segments/2)
                h -= (1.0 - dist) * 25
            elif self.expression == 'SAD':
                dist = abs(i - segments/2) / (segments/2)
                h += (1.0 - dist) * 20
            
            x = start_x + i * (seg_width + 4)
            y = cy + h
            
            pygame.draw.rect(self.render_surf, FG_COLOR, (x, y - 4, seg_width, 8))
            pygame.draw.rect(self.render_surf, (0, 80, 0), (x, y - 12, seg_width, 2))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.MOUSEBUTTONDOWN: running = False

            # Update Expression
            if time.time() > self.next_expression:
                self.expression = random.choice(['IDLE', 'HAPPY', 'THINKING', 'SAD', 'IDLE'])
                self.next_expression = time.time() + random.uniform(5, 12)
                if random.random() < 0.3:
                    self.logs.pop(0)
                    self.logs.append(random.choice(["DATA_NODE: SYNC", "IO_FLUX: LOW", "SCANNING...", "BUFFER: CLEAR"]))

            # Update Saccades
            if time.time() > self.next_saccade:
                self.target_eye_x = random.choice([-25, 0, 25]) if self.expression != 'THINKING' else 0
                self.target_eye_y = random.choice([-10, 0, 10]) if self.expression != 'THINKING' else -15
                self.next_saccade = time.time() + random.uniform(1.5, 6.0)
            
            self.eye_offset_x += (self.target_eye_x - self.eye_offset_x) * 0.2
            self.eye_offset_y += (self.target_eye_y - self.eye_offset_y) * 0.2

            # Update Blinking
            if not self.blinking and random.random() < 0.008:
                self.blinking = True
                self.double_blink = random.random() < 0.2
            
            if self.blinking:
                self.blink_timer += 1
                if self.blink_timer > 4:
                    if self.double_blink: self.double_blink = False; self.blink_timer = 0
                    else: self.blinking = False; self.blink_timer = 0

            # Draw
            self.render_surf.fill(BG_COLOR)
            self.draw_grid(self.render_surf)
            
            # Floating/Breathing Offset
            float_y = math.sin(time.time() * 1.5) * 12

            # Face components
            self.draw_eye(W//2 - 160, H//2 - 40 + float_y, flip=False)
            self.draw_eye(W//2 + 160, H//2 - 40 + float_y, flip=True)
            self.draw_mouth(W//2, H//2 + 120 + float_y)
            
            self.draw_status(self.render_surf)
            self.render_surf.blit(self.scan_surf, (0,0))
            
            # Rotate for mount
            final = pygame.transform.rotate(self.render_surf, 90)
            self.screen.blit(final, (0,0))
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()

if __name__ == "__main__":
    RetroFace().run()
