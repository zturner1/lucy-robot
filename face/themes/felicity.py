import pygame
import math
import random
import time
import sys
import os

# CONFIG - Felicity's Custom Theme
W, H = 800, 480
SKY_COLOR = (135, 206, 235)  # Sky blue
CLOUD_COLOR = (255, 255, 255)  # White
EYE_OUTER = (255, 182, 193)  # Pink
PUPIL_COLOR = (100, 149, 237)  # Cornflower blue
SMILE_COLOR = (255, 215, 0)  # Gold/yellow

class FelicityFace:
    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.raw_w, self.raw_h = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.raw_w, self.raw_h), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        
        self.render_surf = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        self.blinking = False
        self.blink_timer = 0
        
        # Cloud animation
        self.clouds = []
        for i in range(5):
            self.clouds.append({
                'x': random.randint(0, W),
                'y': random.randint(0, H // 2),
                'speed': random.uniform(0.3, 0.8),
                'size': random.randint(40, 80)
            })
        
        # Eye movement
        self.eye_offset_x = 0
        self.eye_offset_y = 0
        self.target_eye_x = 0
        self.target_eye_y = 0
        self.next_saccade = time.time() + random.uniform(2, 5)

    def draw_clouds(self):
        for cloud in self.clouds:
            # Move cloud
            cloud['x'] += cloud['speed']
            if cloud['x'] > W + 100:
                cloud['x'] = -100
                cloud['y'] = random.randint(0, H // 2)
            
            # Draw fluffy cloud (overlapping circles)
            size = cloud['size']
            x, y = cloud['x'], cloud['y']
            pygame.draw.circle(self.render_surf, CLOUD_COLOR, (int(x), int(y)), size // 2)
            pygame.draw.circle(self.render_surf, CLOUD_COLOR, (int(x + size//3), int(y)), size // 3)
            pygame.draw.circle(self.render_surf, CLOUD_COLOR, (int(x - size//3), int(y)), size // 3)
            pygame.draw.circle(self.render_surf, CLOUD_COLOR, (int(x), int(y - size//4)), size // 3)

    def draw_eye(self, cx, cy):
        # Apply eye movement offset
        cx += int(self.eye_offset_x)
        cy += int(self.eye_offset_y)
        
        if self.blinking:
            # Draw closed eye as pink arc
            pygame.draw.arc(self.render_surf, EYE_OUTER, (cx - 50, cy - 10, 100, 40), 0, math.pi, 8)
        else:
            # Outer pink eye (oval)
            pygame.draw.ellipse(self.render_surf, EYE_OUTER, (cx - 50, cy - 60, 100, 120), 0)
            pygame.draw.ellipse(self.render_surf, EYE_OUTER, (cx - 48, cy - 58, 96, 116), 0)
            
            # Blue pupil (smaller circle inside)
            pupil_x = cx + int(self.eye_offset_x * 0.3)
            pupil_y = cy + int(self.eye_offset_y * 0.3)
            pygame.draw.circle(self.render_surf, PUPIL_COLOR, (pupil_x, pupil_y), 25)
            
            # Highlight/sparkle
            pygame.draw.circle(self.render_surf, (255, 255, 255), (pupil_x - 8, pupil_y - 8), 8)

    def draw_smile(self, cx, cy):
        # Yellow curved smile
        points = []
        for i in range(-80, 81, 8):
            # Create arc curve
            x = cx + i
            # Parabolic curve for smile
            y = cy + int((i * i) / 200) - 10
            points.append((x, y))
        
        if len(points) > 1:
            pygame.draw.lines(self.render_surf, SMILE_COLOR, False, points, 12)
            # Add second line for thickness
            points2 = [(p[0], p[1] + 6) for p in points]
            pygame.draw.lines(self.render_surf, SMILE_COLOR, False, points2, 12)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            # Update blinking
            if not self.blinking and random.random() < 0.01:
                self.blinking = True
            
            if self.blinking:
                self.blink_timer += 1
                if self.blink_timer > 4:
                    self.blinking = False
                    self.blink_timer = 0

            # Update eye movement
            if time.time() > self.next_saccade:
                self.target_eye_x = random.choice([-15, 0, 15])
                self.target_eye_y = random.choice([-10, 0, 10])
                self.next_saccade = time.time() + random.uniform(2.0, 5.0)
            
            self.eye_offset_x += (self.target_eye_x - self.eye_offset_x) * 0.15
            self.eye_offset_y += (self.target_eye_y - self.eye_offset_y) * 0.15

            # Draw
            self.render_surf.fill(SKY_COLOR)
            self.draw_clouds()
            
            # Face components
            self.draw_eye(W//2 - 140, H//2 - 40)
            self.draw_eye(W//2 + 140, H//2 - 40)
            self.draw_smile(W//2, H//2 + 100)

            # Rotate for mount
            final = pygame.transform.rotate(self.render_surf, 90)
            self.screen.blit(final, (0, 0))
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()

if __name__ == __main__:
    FelicityFace().run()
