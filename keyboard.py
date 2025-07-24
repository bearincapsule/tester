import pygame
from pynput import keyboard

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Keyboard Layout")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)

# Key layout (simplified example)
keys = [
    {"key": "Q", "rect": pygame.Rect(50, 50, 50, 50)},
    {"key": "W", "rect": pygame.Rect(110, 50, 50, 50)},
    {"key": "E", "rect": pygame.Rect(170, 50, 50, 50)},
    {"key": "A", "rect": pygame.Rect(50, 110, 50, 50)},
    {"key": "S", "rect": pygame.Rect(110, 110, 50, 50)},
    {"key": "D", "rect": pygame.Rect(170, 110, 50, 50)},
]

# Track pressed keys
pressed_keys = set()

# Function to draw the keyboard layout
def draw_keyboard():
    screen.fill(BLACK)
    for key in keys:
        color = BLUE if key["key"] in pressed_keys else GRAY
        pygame.draw.rect(screen, color, key["rect"])
        pygame.draw.rect(screen, WHITE, key["rect"], 2)
        font = pygame.font.Font(None, 36)
        text = font.render(key["key"], True, WHITE)
        text_rect = text.get_rect(center=key["rect"].center)
        screen.blit(text, text_rect)

# Pynput listener for key presses
def on_press(key):
    try:
        pressed_keys.add(key.char.upper())
    except AttributeError:
        pass

def on_release(key):
    try:
        pressed_keys.discard(key.char.upper())
    except AttributeError:
        pass

# Start pynput listener
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_keyboard()
    pygame.display.flip()

# Quit pygame
pygame.quit()
listener.stop()