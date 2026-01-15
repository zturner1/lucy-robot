import pygame
import math
import random
import time
import sys
import os

# CONFIG
W, H = 800, 480 
BG_COLOR = (0, 0, 0)
C1 = (255, 0, 50) # Red
C2 = (0, 255, 255) # Cyan

class GlitchFace:
    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.raw_w, self.raw_h = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.raw_w, self.raw_h), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        
        self.render_surf = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()

    def draw_glitch_rect(self):
        if random.random() < 0.2:
            w = random.randint(10, 100)
            h = random.randint(2, 20)
            x = random.randint(0, W)
            y = random.randint(0, H)
            col = C1 if random.random() < 0.5 else C2
            pygame.draw.rect(self.render_surf, col, (x, y, w, h))

    def draw_eye(self, x, y):
        offset = random.randint(-2, 2)
        # Eye X
        pygame.draw.line(self.render_surf, C1, (x-40+offset, y-40), (x+40+offset, y+40), 5)
        pygame.draw.line(self.render_surf, C1, (x-40+offset, y+40), (x+40+offset, y-40), 5)
        # Ghost
        pygame.draw.line(self.render_surf, C2, (x-42, y-40), (x+38, y+40), 2)
        pygame.draw.line(self.render_surf, C2, (x-42, y+40), (x+38, y-40), 2)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    running = False

            self.render_surf.fill(BG_COLOR)
            self.draw_glitch_rect()
            
            # Eyes
            self.draw_eye(W//2 - 150, H//2 - 50)
            self.draw_eye(W//2 + 150, H//2 - 50)
            
            # Mouth (Jagged)
            pts = []
            for i in range(-80, 80, 20):
                h = random.randint(-5, 5)
                pts.append((W//2 + i, H//2 + 100 + h))
            if len(pts) > 1:
                pygame.draw.lines(self.render_surf, C2, False, pts, 3)

            # Rotate & Blit
            final = pygame.transform.rotate(self.render_surf, 90)
            self.screen.blit(final, (0,0))
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()

if __name__ == "__main__":
    GlitchFace().run()
