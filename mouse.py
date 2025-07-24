import pygame

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Key and Mouse Press Squares")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Square positions and sizes
square_size = 50
left_square = pygame.Rect(100, 75, square_size, square_size)
right_square = pygame.Rect(250, 75, square_size, square_size)
left_mouse_square = pygame.Rect(100, 200, square_size, square_size)
right_mouse_square = pygame.Rect(250, 200, square_size, square_size)

# Track mouse button states
mouse_buttons = {"left": False, "right": False}

# Main loop
running = True
while running:
    screen.fill(BLACK)

    # Draw keyboard squares
    pygame.draw.rect(screen, RED if pygame.key.get_pressed()[pygame.K_a] else WHITE, left_square)
    pygame.draw.rect(screen, BLUE if pygame.key.get_pressed()[pygame.K_d] else WHITE, right_square)

    # Draw mouse button squares
    pygame.draw.rect(screen, GREEN if mouse_buttons["left"] else WHITE, left_mouse_square)
    pygame.draw.rect(screen, YELLOW if mouse_buttons["right"] else WHITE, right_mouse_square)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_buttons["left"] = True
            elif event.button == 3:  # Right mouse button
                mouse_buttons["right"] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                mouse_buttons["left"] = False
            elif event.button == 3:  # Right mouse button
                mouse_buttons["right"] = False

    # Update display
    pygame.display.flip()

# Quit pygame
pygame.quit()