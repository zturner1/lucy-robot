import pygame
import math
import random
import time
import sys
import os
import socket
import json
import threading
import subprocess

# CONFIG - Felicity's Custom Theme
W, H = 800, 480
SKY_COLOR = (135, 206, 235)  # Sky blue
CLOUD_COLOR = (255, 255, 255)  # White
EYE_OUTER = (255, 105, 180)  # Hot pink
PUPIL_COLOR = (100, 149, 237)  # Cornflower blue
SMILE_COLOR = (147, 112, 219)  # Medium purple
CHEEK_COLOR = (255, 60, 60)  # Red

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

        # Voice chat process
        self.voice_process = None

        # Cloud animation
        self.clouds = []
        for i in range(6):
            self.clouds.append({
                'x': random.randint(0, W),
                'y': random.randint(0, H // 2),
                'speed': random.uniform(0.3, 1.0),
                'size': random.randint(40, 80)
            })

        # Eye movement
        self.eye_offset_x = 0
        self.eye_offset_y = 0
        self.target_eye_x = 0
        self.target_eye_y = 0
        self.next_saccade = time.time() + random.uniform(1, 3)

        # Expression states
        self.expression = 'happy'
        self.next_expression_change = time.time() + random.uniform(3, 6)

        # Eye sparkle animation
        self.sparkle_size = 8
        self.sparkle_growing = True

        # Bounce animation
        self.bounce_offset = 0
        self.bounce_time = 0

        # Talking and listening states
        self.is_talking = False
        self.is_listening = False
        self.mouth_talk_phase = 0
        self.listening_pulse = 0

        # Start brain listener
        self.start_brain_listener()

        # Auto-start voice chat
        self.start_voice_chat()

    def start_brain_listener(self):
        """Listen for state updates from Lucy's brain"""
        def listen():
            try:
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind(('0.0.0.0', 5555))
                server.listen(1)
                server.settimeout(1.0)

                while True:
                    try:
                        conn, addr = server.accept()
                        data = conn.recv(1024).decode()
                        if data:
                            state = json.loads(data)
                            self.is_talking = state.get('talking', False)
                            self.is_listening = state.get('listening', False)
                        conn.close()
                    except socket.timeout:
                        continue
                    except:
                        break
            except:
                pass

        thread = threading.Thread(target=listen, daemon=True)
        thread.start()

    def start_voice_chat(self):
        """Start the voice chat system automatically"""
        print("Starting voice chat for Felicity...")
        if self.voice_process is None or self.voice_process.poll() is not None:
            # Start voice chat in background
            self.voice_process = subprocess.Popen([
                '/home/z/greenhouse_venv/bin/python3',
                '/home/z/lucy/lucy_voice.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def handle_touch(self, pos):
        """Touch screen restarts voice chat if it stopped"""
        if self.voice_process is None or self.voice_process.poll() is not None:
            # Voice chat stopped, restart it
            self.start_voice_chat()

    def draw_clouds(self):
        for cloud in self.clouds:
            cloud['x'] += cloud['speed']
            if cloud['x'] > W + 100:
                cloud['x'] = -100
                cloud['y'] = random.randint(0, H // 2)

            size = cloud['size']
            x, y = cloud['x'], cloud['y']
            pygame.draw.circle(self.render_surf, CLOUD_COLOR, (int(x), int(y)), size // 2)
            pygame.draw.circle(self.render_surf, CLOUD_COLOR, (int(x + size//3), int(y)), size // 3)
            pygame.draw.circle(self.render_surf, CLOUD_COLOR, (int(x - size//3), int(y)), size // 3)
            pygame.draw.circle(self.render_surf, CLOUD_COLOR, (int(x), int(y - size//4)), size // 3)

    def draw_eye(self, cx, cy, side='left'):
        cx += int(self.eye_offset_x)
        cy += int(self.eye_offset_y)

        if self.blinking:
            pygame.draw.arc(self.render_surf, EYE_OUTER, (cx - 50, cy - 20, 100, 60), 0, math.pi, 12)
        else:
            eye_w = 100
            eye_h = 120
            if self.expression == 'excited' or self.is_talking:
                eye_h = 135
            elif self.expression == 'very_happy':
                eye_h = 125

            # Draw pink outline with thicker border
            pygame.draw.ellipse(self.render_surf, EYE_OUTER, (cx - 52, cy - eye_h//2 - 2, eye_w + 4, eye_h + 4), 0)
            pygame.draw.ellipse(self.render_surf, EYE_OUTER, (cx - 50, cy - eye_h//2, eye_w, eye_h), 0)

            pupil_x = cx + int(self.eye_offset_x * 0.4)
            pupil_y = cy + int(self.eye_offset_y * 0.4)

            pupil_size = 25
            if self.expression == 'excited' or self.is_talking:
                pupil_size = 30

            pygame.draw.circle(self.render_surf, PUPIL_COLOR, (pupil_x, pupil_y), pupil_size)

            # Animated sparkle
            sparkle_offset = 2 if self.expression == 'excited' or self.is_talking else 0
            pygame.draw.circle(self.render_surf, (255, 255, 255),
                             (pupil_x - 8 + sparkle_offset, pupil_y - 8),
                             int(self.sparkle_size))

            pygame.draw.circle(self.render_surf, (200, 220, 255),
                             (pupil_x + 10, pupil_y + 10), 4)

            # Listening indicator - subtle glow around eyes
            if self.is_listening:
                pulse = int(20 + math.sin(self.listening_pulse) * 10)
                s = pygame.Surface((eye_w + 20, eye_h + 20), pygame.SRCALPHA)
                pygame.draw.ellipse(s, (*EYE_OUTER, 80), (0, 0, eye_w + 20, eye_h + 20), pulse)
                self.render_surf.blit(s, (cx - 60, cy - eye_h//2 - 10))

    def draw_cheeks(self, base_y):
        cheek_y = base_y + int(self.bounce_offset)
        pygame.draw.circle(self.render_surf, CHEEK_COLOR, (W//2 - 200, cheek_y), 40)
        pygame.draw.circle(self.render_surf, CHEEK_COLOR, (W//2 + 200, cheek_y), 40)

    def draw_smile(self, cx, cy):
        points = []
        smile_depth = 35
        smile_width = 95

        if self.is_talking:
            self.mouth_talk_phase += 0.3
            open_amount = abs(math.sin(self.mouth_talk_phase))
            smile_depth = int(35 + open_amount * 20)
            smile_width = int(95 + open_amount * 15)
        elif self.expression == 'very_happy':
            smile_depth = 45
            smile_width = 105
        elif self.expression == 'excited':
            smile_depth = 55
            smile_width = 115
        elif self.expression == 'joyful':
            smile_depth = 50
            smile_width = 110

        # Create upward curve
        for i in range(-smile_width, smile_width + 1, 6):
            x = cx + i
            y = cy - int((i * i) / (smile_width * 3.5)) + smile_depth
            points.append((x, y))

        if len(points) > 1:
            pygame.draw.lines(self.render_surf, SMILE_COLOR, False, points, 16)
            points2 = [(p[0], p[1] - 5) for p in points]
            pygame.draw.lines(self.render_surf, SMILE_COLOR, False, points2, 12)

            if self.expression in ['very_happy', 'excited', 'joyful'] or self.is_talking:
                pygame.draw.circle(self.render_surf, SMILE_COLOR, points[0], 10)
                pygame.draw.circle(self.render_surf, SMILE_COLOR, points[-1], 10)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_touch(event.pos)

            # Update expression changes
            if time.time() > self.next_expression_change and not self.is_talking:
                self.expression = random.choice(['happy', 'very_happy', 'excited', 'joyful', 'very_happy'])
                self.next_expression_change = time.time() + random.uniform(4, 8)

            # Update blinking
            if not self.blinking and random.random() < 0.015 and not self.is_talking:
                self.blinking = True

            if self.blinking:
                self.blink_timer += 1
                if self.blink_timer > 3:
                    self.blinking = False
                    self.blink_timer = 0

            # Update eye movement
            if time.time() > self.next_saccade and not self.is_talking:
                self.target_eye_x = random.choice([-20, -10, 0, 10, 20])
                self.target_eye_y = random.choice([-15, -5, 0, 5, 15])
                self.next_saccade = time.time() + random.uniform(1.5, 4.0)

            self.eye_offset_x += (self.target_eye_x - self.eye_offset_x) * 0.2
            self.eye_offset_y += (self.target_eye_y - self.eye_offset_y) * 0.2

            # Animate sparkle size
            if self.sparkle_growing:
                self.sparkle_size += 0.2
                if self.sparkle_size > 10:
                    self.sparkle_growing = False
            else:
                self.sparkle_size -= 0.2
                if self.sparkle_size < 6:
                    self.sparkle_growing = True

            # Gentle bounce animation
            self.bounce_time += 0.08 if not self.is_talking else 0.15
            self.bounce_offset = math.sin(self.bounce_time) * 8

            # Listening pulse
            if self.is_listening:
                self.listening_pulse += 0.1

            # Draw
            self.render_surf.fill(SKY_COLOR)
            self.draw_clouds()

            face_y_offset = int(self.bounce_offset)

            self.draw_eye(W//2 - 140, H//2 - 40 + face_y_offset, 'left')
            self.draw_eye(W//2 + 140, H//2 - 40 + face_y_offset, 'right')
            self.draw_cheeks(H//2 + 60)
            self.draw_smile(W//2, H//2 + 100 + face_y_offset)

            final = pygame.transform.rotate(self.render_surf, 90)
            self.screen.blit(final, (0, 0))
            pygame.display.flip()
            self.clock.tick(30)

        # Cleanup
        if self.voice_process:
            self.voice_process.terminate()
        pygame.quit()

if __name__ == "__main__":
    FelicityFace().run()
