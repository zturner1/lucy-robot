import pygame
import math
import random
import time
import sys
import os

# CONFIG
W, H = 80, 48 # Tiny resolution for pixel art
SCALE = 10 # Scale up 10x
BG_COLOR = (15, 56, 15) # Gameboy Dark
EYE_COLOR = (155, 188, 15) # Gameboy Light
BLINK_COLOR = (48, 98, 48) # Gameboy Mid

class RPGFace:
    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.raw_w, self.raw_h = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.raw_w, self.raw_h), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        
        self.pixel_surf = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        self.blinking = False
        self.blink_timer = 0

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False

            # Update
            if random.random() < 0.02: self.blinking = True
            if self.blinking:
                self.blink_timer += 1
                if self.blink_timer > 3:
                    self.blinking = False
                    self.blink_timer = 0

            # Draw to pixel surface
            self.pixel_surf.fill(BG_COLOR)
            
            # Eyes (Chunky Rects)
            ex, ey = 20, 15
            ew, eh = 10, 15
            
            if self.blinking:
                pygame.draw.rect(self.pixel_surf, BLINK_COLOR, (ex, ey + 7, ew, 3))
                pygame.draw.rect(self.pixel_surf, BLINK_COLOR, (W - ex - ew, ey + 7, ew, 3))
            else:
                # Left Eye
                pygame.draw.rect(self.pixel_surf, EYE_COLOR, (ex, ey, ew, eh))
                pygame.draw.rect(self.pixel_surf, BG_COLOR, (ex + 3, ey + 3, 4, 4)) # Sparkle
                # Right Eye
                pygame.draw.rect(self.pixel_surf, EYE_COLOR, (W - ex - ew, ey, ew, eh))
                pygame.draw.rect(self.pixel_surf, BG_COLOR, (W - ex - ew + 3, ey + 3, 4, 4)) # Sparkle

            # Mouth
            mx = W // 2 - 10
            my = H // 2 + 10
            mw = 20
            pygame.draw.rect(self.pixel_surf, EYE_COLOR, (mx, my, mw, 2))

            # Scale Up & Rotate
            # Rotation happens on the scaled surface for sharpness
            scaled = pygame.transform.scale(self.pixel_surf, (W * SCALE, H * SCALE))
            final = pygame.transform.rotate(scaled, 90)
            
            # Center on screen
            self.screen.fill((0,0,0))
            self.screen.blit(final, (0,0))
            
            pygame.display.flip()
            self.clock.tick(15) # Lower FPS for retro feel
        pygame.quit()

if __name__ == "__main__":
    RPGFace().run()
